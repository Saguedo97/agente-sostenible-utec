"""
LangGraph de clasificación con feedback y autocorrección.

Flujo:
START -> agente_evidencia -> clasificador -> validacion_determinista
      -> verificador_semantico -> APROBADO
                           -> feedback -> agente_evidencia (loop)
                           -> REVISION_HUMANA al llegar al límite
"""

from __future__ import annotations

import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agent import ejecutar_agente_evidencia
from guardrails import validar_candidato_basico, validar_cui
from schemas import (
    ClasificacionPropuesta,
    ResultadoFinal,
    VeredictoVerificador,
)

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
JUDGE_MODEL = os.getenv("OPENAI_JUDGE_MODEL", MODEL)
MAX_ITERACIONES = int(os.getenv("MAX_AGENT_ITERATIONS", "3"))


class AgentState(TypedDict, total=False):
    cui: str
    iteracion: int
    feedback: str
    dossier: str
    tool_calls: list[dict]
    consultas_marco: list[str]
    tool_outputs: list[dict]
    candidato: dict
    validacion_ok: bool
    problemas_validacion: list[str]
    veredicto: dict
    resultado: dict
    trajectory: list[dict]


_classifier_model = ChatOpenAI(
    model=MODEL,
    use_responses_api=True,
    reasoning_effort="medium",
).with_structured_output(ClasificacionPropuesta)
_judge_model = ChatOpenAI(
    model=JUDGE_MODEL,
    use_responses_api=True,
    reasoning_effort="medium",
).with_structured_output(VeredictoVerificador)


def nodo_agente(state: AgentState) -> dict:
    cui = validar_cui(state["cui"])
    iteracion = state.get("iteracion", 0) + 1

    run = ejecutar_agente_evidencia(
        cui=cui,
        feedback=state.get("feedback", ""),
    )

    trajectory = list(state.get("trajectory", []))
    trajectory.append(
        {
            "iteracion": iteracion,
            "fase": "agente_evidencia",
            "tool_calls": run["tool_calls"],
            "consultas_marco": run["consultas_marco"],
        }
    )

    return {
        "cui": cui,
        "iteracion": iteracion,
        "dossier": run["dossier"],
        "tool_calls": list(state.get("tool_calls", [])) + run["tool_calls"],
        "consultas_marco": list(state.get("consultas_marco", [])) + run["consultas_marco"],
        "tool_outputs": run["tool_outputs"],
        "trajectory": trajectory,
        "feedback": "",
    }


def _contexto_tools(state: AgentState) -> str:
    bloques = []
    for item in state.get("tool_outputs", []):
        content = item.get("content", "")
        # Límite defensivo para evitar que una tool monopolice el contexto.
        if len(content) > 15000:
            content = content[:15000] + "\n[TRUNCADO]"
        bloques.append(f"TOOL: {item.get('tool')}\n{content}")
    return "\n\n".join(bloques)


def nodo_clasificador(state: AgentState) -> dict:
    prompt = f"""
Clasifica el CUI {state['cui']} exclusivamente a partir de la evidencia recuperada
por el agente y el Marco 2021.

DOSSIER DEL AGENTE
------------------
{state.get('dossier', '')}

SALIDAS DE TOOLS
----------------
{_contexto_tools(state)}

REGLAS
- No uses conocimiento sobre clasificaciones históricas.
- Distingue evidencia del proyecto de criterio normativo.
- Una palabra clave por sí sola no basta: debe existir correspondencia material
  entre la intervención y el criterio del Marco.
- Si existe ambigüedad relevante entre dos categorías y no puede resolverse,
  usa "Información insuficiente".
- "No aplica" significa que hay información suficiente para concluir que no
  corresponde a ninguna categoría verde del Marco.
- Cita solo páginas realmente recuperadas.
- No inventes información.
- No expongas cadena de pensamiento; la justificación debe ser breve y auditable.
"""
    candidato = _classifier_model.invoke(prompt)
    return {"candidato": candidato.model_dump()}


def nodo_validacion(state: AgentState) -> dict:
    ok, problemas = validar_candidato_basico(
        state["candidato"],
        state["cui"],
    )

    trajectory = list(state.get("trajectory", []))
    trajectory.append(
        {
            "iteracion": state.get("iteracion", 0),
            "fase": "validacion_determinista",
            "aprobado": ok,
            "problemas": problemas,
        }
    )

    if not ok:
        return {
            "validacion_ok": False,
            "problemas_validacion": problemas,
            "feedback": "Corrige estos problemas formales/evidenciales: " + "; ".join(problemas),
            "trajectory": trajectory,
        }

    return {
        "validacion_ok": True,
        "problemas_validacion": [],
        "trajectory": trajectory,
    }


def ruta_post_validacion(state: AgentState) -> str:
    if state.get("validacion_ok"):
        return "verificador"
    if state.get("iteracion", 0) >= MAX_ITERACIONES:
        return "revision_humana"
    return "agente"


def nodo_verificador(state: AgentState) -> dict:
    prompt = f"""
Actúa como verificador independiente de evidencia normativa.

CUI: {state['cui']}

CANDIDATO
---------
{json.dumps(state['candidato'], ensure_ascii=False, indent=2)}

DOSSIER
-------
{state.get('dossier', '')}

EVIDENCIA RECUPERADA
--------------------
{_contexto_tools(state)}

Evalúa únicamente:
1. Si la categoría propuesta está sustentada por los hechos recuperados.
2. Si los criterios normativos citados corresponden al Marco 2021 recuperado.
3. Si la conclusión va más allá de la evidencia.
4. Si debería abstenerse por información insuficiente.
5. Si existe una categoría alternativa que deba contrastarse antes de cerrar.

No uses ground truth, reportes de asignación ni conocimiento histórico del proyecto.
No expongas cadena de pensamiento. Entrega problemas concretos y feedback accionable.
"""
    veredicto = _judge_model.invoke(prompt)
    payload = veredicto.model_dump()

    trajectory = list(state.get("trajectory", []))
    trajectory.append(
        {
            "iteracion": state.get("iteracion", 0),
            "fase": "verificador_semantico",
            "aprobado": payload["aprobado"],
            "categoria_sustentada": payload["categoria_sustentada"],
            "evidencia_suficiente": payload["evidencia_suficiente"],
            "problemas": payload["problemas"],
            "feedback": payload["feedback_para_agente"],
            "siguiente_accion": (
                "finalizar" if payload["aprobado"]
                else (
                    "revision_humana"
                    if state.get("iteracion", 0) >= MAX_ITERACIONES
                    else "replanificar"
                )
            ),
        }
    )

    return {
        "veredicto": payload,
        "feedback": payload["feedback_para_agente"] if not payload["aprobado"] else "",
        "trajectory": trajectory,
    }


def ruta_post_verificador(state: AgentState) -> str:
    if state["veredicto"].get("aprobado"):
        return "finalizar"
    if state.get("iteracion", 0) >= MAX_ITERACIONES:
        return "revision_humana"
    return "agente"


def _final_common(state: AgentState, estado: str) -> dict:
    cand = dict(state["candidato"])
    tools = [x.get("name") for x in state.get("tool_calls", []) if x.get("name")]
    resultado = ResultadoFinal(
        **cand,
        estado=estado,
        iteraciones=state.get("iteracion", 0),
        herramientas_utilizadas=list(dict.fromkeys(tools)),
        consultas_marco=list(dict.fromkeys(state.get("consultas_marco", []))),
    )
    return {"resultado": resultado.model_dump()}


def nodo_finalizar(state: AgentState) -> dict:
    """
    APROBADO significa que el agente cerró el caso sin requerir revisión humana.
    Si la clasificación es una abstención o el propio candidato pide revisión,
    el estado visible debe ser REVISION_HUMANA aunque el judge haya aprobado
    la calidad de esa decisión.
    """
    candidato = state["candidato"]

    if (
        candidato.get("requiere_revision_humana")
        or candidato.get("clasificacion") == "Información insuficiente"
    ):
        return _final_common(state, "REVISION_HUMANA")

    return _final_common(state, "APROBADO")


def nodo_revision_humana(state: AgentState) -> dict:
    cand = dict(state["candidato"])
    cand["requiere_revision_humana"] = True
    if not cand.get("evidencia_suficiente"):
        cand["clasificacion"] = "Información insuficiente"
    tmp = dict(state)
    tmp["candidato"] = cand
    return _final_common(tmp, "REVISION_HUMANA")


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("agente", nodo_agente)
    workflow.add_node("clasificador", nodo_clasificador)
    workflow.add_node("validacion", nodo_validacion)
    workflow.add_node("verificador", nodo_verificador)
    workflow.add_node("finalizar", nodo_finalizar)
    workflow.add_node("revision_humana", nodo_revision_humana)

    workflow.add_edge(START, "agente")
    workflow.add_edge("agente", "clasificador")
    workflow.add_edge("clasificador", "validacion")

    workflow.add_conditional_edges(
        "validacion",
        ruta_post_validacion,
        {
            "verificador": "verificador",
            "agente": "agente",
            "revision_humana": "revision_humana",
        },
    )

    workflow.add_conditional_edges(
        "verificador",
        ruta_post_verificador,
        {
            "finalizar": "finalizar",
            "agente": "agente",
            "revision_humana": "revision_humana",
        },
    )

    workflow.add_edge("finalizar", END)
    workflow.add_edge("revision_humana", END)

    return workflow.compile()


GRAPH = build_graph()


def clasificar_cui(cui: str) -> dict:
    final_state = GRAPH.invoke(
        {
            "cui": validar_cui(cui),
            "iteracion": 0,
            "feedback": "",
            "tool_calls": [],
            "consultas_marco": [],
            "trajectory": [],
        }
    )
    return final_state
