"""Frontend de investigación V2; V1 intacta y seleccionable desde la barra lateral.

Ejecutar desde la raiz del repo: streamlit run streamlit_app_v2.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
try:
    if 'OPENAI_API_KEY' in st.secrets and not os.getenv('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
except Exception:
    pass

from guardrails import validar_cui
from universo_v2 import DB_PATH, consultar_proyecto_v2

st.set_page_config(
    page_title='Investigador de elegibilidad sostenible | Perú',
    page_icon='🌱', layout='wide', initial_sidebar_state='expanded',
)

st.title('Investigación de elegibilidad sostenible')
st.caption('Marco del Bono Sostenible del Perú (2021) · Prototipo académico · No certifica elegibilidad')

with st.sidebar:
    st.header('Evaluación')
    modo = st.radio('Motor', ['Investigador V2 (agéntico)', 'Clasificador V1 (baseline)'])
    cui_input = st.text_input('Código Único de Inversión (CUI)', value='2017723')
    st.caption('Datos locales: 423 CUIs históricos, sin etiquetas durante inferencia.')
    if DB_PATH.exists():
        st.success('Universo 2023–2026 indexado disponible')
    else:
        st.info('Universo ampliado opcional: falta preparar la base SQLite local.')
    st.divider()
    st.caption('Las llamadas al modelo usan créditos de API. No hay ejecución automática.')
    inspeccionar = st.button('Consultar ficha (sin IA)', use_container_width=True)
    ejecutar = st.button('Ejecutar investigación', type='primary', use_container_width=True)

if 'respuesta_v2' not in st.session_state:
    st.session_state['respuesta_v2'] = None

if inspeccionar or ejecutar:
    try:
        cui = validar_cui(cui_input)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    if inspeccionar:
        try:
            ficha = consultar_proyecto_v2(cui)
            if ficha.get('encontrado'):
                st.success(f'Ficha encontrada: {ficha.get("fuente", "base local")}')
                st.json(ficha)
            else:
                st.warning('No está en las fuentes locales disponibles.')
                st.json(ficha)
        except Exception as exc:
            st.error(f'No se pudo cargar ficha: {type(exc).__name__}: {exc}')
    else:
        if not os.getenv('OPENAI_API_KEY'):
            st.error('Configura OPENAI_API_KEY en .env o Streamlit Secrets antes de ejecutar modelos.')
            st.stop()
        try:
            with st.spinner('Investigando: planificación, recuperación y verificación de evidencia...'):
                if modo.startswith('Investigador'):
                    from investigacion_v2 import investigar_cui
                    resultado = investigar_cui(cui)
                    st.session_state['respuesta_v2'] = {'modo': 'v2', 'cui': cui, 'estado': resultado}
                else:
                    from graph import clasificar_cui
                    resultado = clasificar_cui(cui)
                    st.session_state['respuesta_v2'] = {'modo': 'v1', 'cui': cui, 'estado': resultado}
        except Exception as exc:
            st.error(f'La ejecución no terminó: {type(exc).__name__}: {exc}')

respuesta = st.session_state['respuesta_v2']
if respuesta:
    estado = respuesta['estado']
    es_v2 = respuesta['modo'] == 'v2'
    if es_v2:
        d = estado.get('diagnostico', {})
        clasificacion = d.get('clasificacion_preliminar', 'Sin conclusión')
        advertencia = bool(d.get('requiere_revision_humana', True))
        pasos = estado.get('pasos', 0)
        herramientas = estado.get('contadores', {})
        trayectoria = estado.get('trayectoria', [])
    else:
        d = estado.get('resultado', {})
        clasificacion = d.get('clasificacion', 'Sin conclusión')
        advertencia = bool(d.get('requiere_revision_humana', False))
        pasos = d.get('iteraciones', 0)
        herramientas = {n: 1 for n in d.get('herramientas_utilizadas', [])}
        trayectoria = estado.get('trajectory', [])

    st.divider()
    st.subheader(f'CUI {respuesta["cui"]} · {clasificacion}')
    k1, k2, k3 = st.columns(3)
    k1.metric('Motor', 'Investigación V2' if es_v2 else 'Clasificación V1')
    k2.metric('Pasos / iteraciones', pasos)
    k3.metric('Revisión humana', 'Sí' if advertencia else 'No')
    if advertencia:
        st.warning('Diagnóstico preliminar sujeto a revisión humana. No representa certificación ni aprobación financiera.')

    tab_result, tab_evidence, tab_plan, tab_export = st.tabs([
        'Diagnóstico', 'Evidencia', 'Plan y trayectoria', 'Datos / exportación',
    ])
    with tab_result:
        if es_v2:
            st.write(d.get('explicacion', ''))
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('**Criterios potenciales**')
                st.write(d.get('criterios_posibles', []))
                st.markdown('**Evidencia documentada**')
                st.write(d.get('evidencia_documentada', []))
            with c2:
                st.markdown('**Incertidumbres**')
                st.write(d.get('incertidumbres', []))
                st.markdown('**Documentación requerida**')
                st.write(d.get('documentacion_requerida', []))
            st.markdown('**Acciones recomendadas**')
            st.write(d.get('acciones_recomendadas', []))
            st.caption(f'Páginas normativas efectivamente recuperadas: {d.get("paginas_marco", [])}')
            if d.get('advertencias_control'):
                st.warning('Controles: ' + '; '.join(d['advertencias_control']))
        else:
            st.write(d.get('justificacion', ''))
            st.write('Criterio:', d.get('criterio_principal'))
            st.write('Páginas del marco:', d.get('paginas_marco', []))
            st.write('Evidencia:', d.get('evidencia_marco', []))

    with tab_evidence:
        st.caption('Solo datos del proyecto y documentos recuperados. Nunca etiquetas históricas.')
        if es_v2:
            st.json(estado.get('proyecto', {}))
            st.markdown('**Consultas y hallazgos de herramientas**')
            st.json(estado.get('evidencia', []))
            if estado.get('opiniones'):
                st.markdown('**Opiniones especializadas independientes**')
                st.json(estado['opiniones'])
        else:
            st.json(estado.get('tool_outputs', []))

    with tab_plan:
        if es_v2:
            st.markdown('**Plan final / vigente**')
            st.write(estado.get('plan', []))
            st.markdown('**Herramientas utilizadas**')
            st.json(herramientas)
        st.markdown('**Trayectoria auditable**')
        st.json(trayectoria)

    with tab_export:
        st.json(d)
        st.download_button(
            'Descargar diagnóstico JSON',
            data=json.dumps(d, ensure_ascii=False, indent=2, default=str),
            file_name=f'diagnostico_{respuesta["cui"]}_{respuesta["modo"]}.json',
            mime='application/json',
            use_container_width=True,
        )
        st.download_button(
            'Descargar trayectoria JSON',
            data=json.dumps(trayectoria, ensure_ascii=False, indent=2, default=str),
            file_name=f'trayectoria_{respuesta["cui"]}_{respuesta["modo"]}.json',
            mime='application/json',
            use_container_width=True,
        )
else:
    st.info('Ingresa un CUI y consulta su ficha sin IA, o ejecuta una investigación con tu clave OpenAI.')
    st.markdown('''
**Cómo funciona V2:** el supervisor observa el contexto y decide qué acción realizar. Puede consultar
normativa, intentar extraer un marco lógico, contrastar hipótesis especializadas o terminar.
Cada paso queda registrado para comparar su estrategia contra el clasificador V1.
''')
