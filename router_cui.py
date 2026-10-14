"""V4: consulta ambas BBDD; no expone ground truth en inferencia."""
from __future__ import annotations
import re
from guardrails import validar_cui


def _num(x):
    if x is None or isinstance(x, bool):
        return 0.0
    try:
        return float(str(x).replace(',', ''))
    except (ValueError, TypeError):
        return 0.0


def _si(x):
    if isinstance(x, bool): return x
    return str(x).strip().lower() in ('1', 'true', 'si', 'sí', 'yes', 'verdadero')


def unir_fuentes(cui: str, historico: dict, reciente: dict) -> dict:
    """Fusión sin perder trazabilidad; CUI histórico tiene prioridad textual, reciente aporta estado/gasto."""
    h = bool(historico.get('encontrado'))
    u = bool(reciente.get('encontrado'))
    if not h and not u:
        return {'encontrado': False, 'cui': cui, 'fuente': 'sin_registro', 'caso': 'no_encontrado', 'proyecto': {}, 'brechas': []}
    ph = historico.get('proyecto') or {} if h else {}
    pu = reciente.get('proyecto') or {} if u else {}
    # Las dos fuentes se conservan; los campos comunes de 423 prevalecen para su descripción.
    combinado = {**pu, **{k: v for k, v in ph.items() if v not in (None, '')}}
    brechas_h = historico.get('brechas') or [] if h else []
    brechas_u = reciente.get('brechas') or [] if u else []
    gastos_recientes = [_num(pu.get(f'DEVENGADO_{a}')) for a in (2023, 2024, 2025, 2026)]
    gasto_anteriores = [_num(ph.get(f'GASTO_{a}')) for a in range(2018, 2025)]
    hay_reciente = any(x > 0 for x in gastos_recientes)
    hay_historico = any(x > 0 for x in gasto_anteriores)
    primer_dev = pu.get('PRIMER_DEVENGADO')
    empezo = _si(pu.get('EMPEZO'))
    no_empezo = _si(pu.get('NO_HA_EMPEZADO'))
    inicio_explicito = no_empezo and not empezo and not primer_dev and not (hay_reciente or hay_historico)
    if h:
        caso = 'A_historico_423'
    elif hay_reciente or hay_historico or empezo or primer_dev:
        caso = 'B_universo_con_ejecucion'
    elif inicio_explicito:
        caso = 'C_prospectivo_sin_inicio'
    else:
        # Evita inferir "no ejecutado" solo de 4 años de gasto cero.
        caso = 'C_prospectivo_por_confirmar'
    return {
        'encontrado': True, 'cui': cui, 'caso': caso,
        'fuente': '423_y_universo' if (h and u) else ('423_historico' if h else 'universo_2023_2026'),
        'en_423': h, 'en_universo': u,
        'proyecto': combinado,
        'brechas': brechas_h if brechas_h else brechas_u,
        'brechas_por_fuente': {'423': brechas_h, 'universo': brechas_u},
        'n_brechas': max(historico.get('n_brechas') or 0, reciente.get('n_brechas') or 0),
        'resumen_ejecucion': {
            'devengado_2023_2026': dict(zip(('2023','2024','2025','2026'), gastos_recientes)),
            'gasto_reciente_positivo': hay_reciente,
            'gasto_historico_positivo': hay_historico,
            'primer_devengado': primer_dev,
            'indicador_empezo': pu.get('EMPEZO'),
            'indicador_no_ha_empezado': pu.get('NO_HA_EMPEZADO'),
            'inicio_confirmado_ausente': inicio_explicito,
        },
        'advertencias_fuentes': [
            'Las etiquetas históricas de los 423 CUIs NO están disponibles durante la inferencia.',
            'Gasto cero entre 2023-2026 no prueba que no existiera ejecución anterior.',
            'Las estadísticas generales no acreditan efectos atribuibles a un CUI específico.',
        ],
    }


def consultar_contexto_cui(cui: str) -> dict:
    cui = validar_cui(cui)
    from toolbox import obtener_proyecto_dict
    from universo_v2 import consultar_universo
    try:
        historico = obtener_proyecto_dict(cui)
    except FileNotFoundError:
        historico = {'encontrado': False, 'cui': cui}
    reciente = consultar_universo(cui)
    return unir_fuentes(cui, historico, reciente)
