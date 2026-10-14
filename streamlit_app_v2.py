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
from router_cui import consultar_contexto_cui
from rag_multifuente import DB as RAG_V4_DB

st.set_page_config(
    page_title='Investigador de elegibilidad sostenible | Perú',
    page_icon='🌱', layout='wide', initial_sidebar_state='expanded',
)

st.title('Investigación de elegibilidad sostenible')
st.caption('Marco del Bono Sostenible del Perú (2021) · Prototipo académico · No certifica elegibilidad')

with st.sidebar:
    st.header('Evaluación')
    modo = st.radio('Motor', ['Investigador V4 (3 casos + RAG multifuente)', 'Investigador V3 (planificación y reflexión)', 'Investigador V2 (baseline)', 'Clasificador V1 (baseline)'])
    cui_input = st.text_input('Código Único de Inversión (CUI)', value='2017723')
    st.caption('Datos locales: 423 CUIs históricos, sin etiquetas durante inferencia.')
    if DB_PATH.exists():
        st.success('Universo 2023–2026 indexado disponible')
    else:
        st.info('Universo ampliado opcional: falta preparar la base SQLite local.')
    st.caption('Biblioteca V4: ' + ('15 documentos indexados' if RAG_V4_DB.exists() else 'sin índice; instalar parche'))
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
            ficha = consultar_contexto_cui(cui) if modo.startswith('Investigador V4') else consultar_proyecto_v2(cui)
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
                if modo.startswith('Investigador V4'):
                    from investigacion_v4 import investigar_cui
                    resultado = investigar_cui(cui)
                    st.session_state['respuesta_v2'] = {'modo': 'v4', 'cui': cui, 'estado': resultado}
                elif modo.startswith('Investigador V3'):
                    from investigacion_v3 import investigar_cui
                    resultado = investigar_cui(cui)
                    st.session_state['respuesta_v2'] = {'modo': 'v3', 'cui': cui, 'estado': resultado}
                elif modo.startswith('Investigador V2'):
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
    es_v3 = respuesta['modo'] == 'v3'
    es_v4 = respuesta['modo'] == 'v4'
    es_investigador = respuesta['modo'] in ('v2', 'v3', 'v4')
    if es_investigador:
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
    if es_v4:
        st.info('Caso detectado: ' + str(d.get('caso', estado.get('caso', 'Sin identificar'))) + ' | Orígenes: ' + str(d.get('origenes', {})))
    k1, k2, k3 = st.columns(3)
    k1.metric('Motor', ('Investigación V4' if es_v4 else ('Investigación V3' if es_v3 else 'Investigación V2')) if es_investigador else 'Clasificación V1')
    k2.metric('Pasos / iteraciones', pasos)
    k3.metric('Revisión humana', 'Sí' if advertencia else 'No')
    if advertencia:
        st.warning('Diagnóstico preliminar sujeto a revisión humana. No representa certificación ni aprobación financiera.')

    tab_result, tab_evidence, tab_plan, tab_export = st.tabs([
        'Diagnóstico', 'Evidencia', 'Plan y trayectoria', 'Datos / exportación',
    ])
    with tab_result:
        if es_investigador:
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
            if es_v4:
                st.markdown('**Requisitos expresos del Marco 2021 (cuando recuperados)**')
                st.write(d.get('requisitos_marco', []))
                st.markdown('**Recomendaciones de mejora / alineamiento prospectivo**')
                st.write(d.get('recomendaciones_mejora', []))
                st.markdown('**Fuentes de contexto recuperadas (no son citas individuales de cada afirmación)**')
                st.write(d.get('fuentes_contexto', []))
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
        if es_investigador:
            st.json(estado.get('proyecto', {}))
            st.markdown('**Consultas y hallazgos de herramientas**')
            st.json(estado.get('evidencia', []))
            if estado.get('opiniones'):
                st.markdown('**Opiniones especializadas independientes**')
                st.json(estado['opiniones'])
        else:
            st.json(estado.get('tool_outputs', []))

    with tab_plan:
        if es_investigador:
            st.markdown('**Plan final / vigente**')
            if es_v3 or es_v4:
                tareas = estado.get('plan', [])
                if tareas:
                    st.dataframe([
                        {'Tarea': t['id'], 'Pregunta': t['pregunta'], 'Estado': t['estado'],
                         'Hallazgo': t.get('hallazgo', ''), 'Evidencia': ', '.join(t.get('evidencia_ids',t.get('evidencias', []))),
                         'Bloqueo': t.get('motivo_bloqueo', '')} for t in tareas
                    ], use_container_width=True, hide_index=True)
                st.caption('Resuelta = evidencia registrada; bloqueada = falta una fuente o se alcanzó un límite.')
                st.write('**Motivo de cierre:**', estado.get('motivo_cierre', '—'))
                st.write('**Decisiones del supervisor:**', estado.get('decisiones', 0))
                st.write('**Revisiones de cierre rechazadas:**', estado.get('cierres_rechazados', 0))
            else:
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
**Cómo funciona V4:** detecta 3 casos de uso, consulta ambas BBDD por CUI, separa
criterios del Marco 2021 de políticas e indicadores y propone mejoras para proyectos prospectivos.

**V3:** planifica tareas verificables, elige herramientas, reflexiona
sobre la evidencia después de cada consulta y audita el cierre de tareas pendientes.
V1 y V2 permanecen disponibles para comparaciones controladas.
''')
