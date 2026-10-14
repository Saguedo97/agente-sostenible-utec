"""Pruebas unitarias V3 sin gastar tokens de API."""
import unittest
from unittest.mock import patch
import investigacion_v3 as v3


def tarea(id="T1", estado="pendiente", normativa=False):
    return {"id": id, "pregunta": "¿Qué exige el Marco?", "criterio_cierre": "Comparar evidencia", "requiere_normativa": normativa,
            "estado": estado, "hallazgo": "", "evidencia_ids": [], "motivo_bloqueo": ""}


class V3Tests(unittest.TestCase):
    def test_no_resolver_sin_referencia_real(self):
        a = v3.Actualizacion(tarea_id="T1", estado="resuelta", hallazgo="OK", evidencia_ids=["E99"])
        plan, avisos = v3._aplicar_actualizaciones([tarea()], [a], {"D0"}, [])
        self.assertEqual(plan[0]["estado"], "pendiente")
        self.assertTrue(avisos)

    def test_normativa_exige_pagina_recuperada(self):
        a = v3.Actualizacion(tarea_id="T1", estado="resuelta", hallazgo="OK", evidencia_ids=["D0"])
        plan, avisos = v3._aplicar_actualizaciones([tarea(normativa=True)], [a], {"D0", "E1:p35"}, [])
        self.assertEqual(plan[0]["estado"], "pendiente")
        b = v3.Actualizacion(tarea_id="T1", estado="resuelta", hallazgo="Marco visto", evidencia_ids=["E1:p35"])
        plan2, _ = v3._aplicar_actualizaciones([tarea(normativa=True)], [b], {"D0", "E1:p35"}, [])
        self.assertEqual(plan2[0]["estado"], "resuelta")

    def test_error_herramienta_no_justifica_resolucion(self):
        a = v3.Actualizacion(tarea_id="T1", estado="resuelta", hallazgo="Encontre norma", evidencia_ids=["E1"])
        plan, _ = v3._aplicar_actualizaciones([tarea()], [a], {"D0", "E1"}, [{"id": "E1", "error": "AuthError"}])
        self.assertEqual(plan[0]["estado"], "pendiente")

    def test_cierre_prohibido_con_pendientes(self):
        with self.assertRaisesRegex(ValueError, "Cierre inválido"):
            v3.finalizar({"cui": "2017723", "plan": [tarea()]})

    def test_cierre_auditado_vuelve_a_decidir(self):
        state = {"cui": "2017723", "proyecto": {"encontrado": True}, "plan": [tarea()],
                 "pasos": 1, "decisiones": 2, "cierres_rechazados": 0,
                 "contadores": {"normativa": 1, "vision": 0, "debate": 0}, "evidencia": [], "trayectoria": []}
        fake = v3.Cierre(continuar_investigando=True, razon="Falta buscar criterio", tareas_bloqueadas=[])
        with patch.object(v3, "_llamar_modelo", return_value=fake):
            res = v3.auditar_cierre(state)
        self.assertEqual(res["auditoria"]["continuar"], True)
        self.assertEqual(v3.ruta_auditoria(res), "decidir")
        self.assertEqual(res["cierres_rechazados"], 1)

    def test_cierre_bloquea_con_motivo(self):
        state = {"cui": "2017723", "proyecto": {"encontrado": True}, "plan": [tarea()],
                 "pasos": 1, "decisiones": 2, "cierres_rechazados": 0,
                 "contadores": {"normativa": 1, "vision": 0, "debate": 0}, "evidencia": [], "trayectoria": []}
        bloqueada = v3.Actualizacion(tarea_id="T1", estado="bloqueada", hallazgo="Expediente ausente", motivo_bloqueo="No se dispone del expediente")
        fake = v3.Cierre(continuar_investigando=False, razon="No hay fuente", tareas_bloqueadas=[bloqueada])
        with patch.object(v3, "_llamar_modelo", return_value=fake):
            res = v3.auditar_cierre(state)
        self.assertEqual(res["plan"][0]["estado"], "bloqueada")
        self.assertEqual(res["plan"][0]["motivo_bloqueo"], "No se dispone del expediente")
        self.assertEqual(v3.ruta_auditoria(res), "finalizar")

    def test_preguntas_nuevas_crean_replanning_trazable(self):
        state = {"cui": "2017723", "proyecto": {"encontrado": True}, "plan": [tarea()],
                 "pasos": 1, "contadores": {"normativa": 1, "vision": 0, "debate": 0},
                 "evidencia": [{"id": "E1", "tipo": "normativa", "resultados": [{"pagina": 35, "texto": "Agua"}]}], "trayectoria": []}
        fake = v3.Reflexion(que_aprendi="Dos criterios posibles", estrategia_cambiada=True,
                            motivo_cambio="Hay ambigüedad", nuevas_tareas=[v3.PreguntaPlan(pregunta="¿Existe tratamiento de aguas residuales?", criterio_cierre="Leer componentes")])
        with patch.object(v3, "_llamar_modelo", return_value=fake):
            res = v3.reflexionar(state)
        self.assertEqual(len(res["plan"]), 2)
        self.assertTrue(res["trayectoria"][-1]["estrategia_cambiada"])
        self.assertEqual(res["trayectoria"][-1]["nuevas_tareas"], 1)

    def test_no_permite_cierre_si_auditor_omite_pendientes(self):
        state = {"cui": "2017723", "proyecto": {"encontrado": True}, "plan": [tarea()],
                 "pasos": 1, "decisiones": 2, "cierres_rechazados": 0,
                 "contadores": {"normativa": 1, "vision": 0, "debate": 0}, "evidencia": [], "trayectoria": []}
        fake = v3.Cierre(continuar_investigando=False, razon="Creo que basta", tareas_bloqueadas=[])
        with patch.object(v3, "_llamar_modelo", return_value=fake):
            res = v3.auditar_cierre(state)
        self.assertTrue(res["auditoria"]["continuar"])
        self.assertTrue(res["trayectoria"][-1]["veto_cierre"])
        self.assertEqual(res["plan"][0]["estado"], "pendiente")

    def test_modelo_no_puede_ejecutar_una_tarea_inexistente(self):
        state = {"cui": "2017723", "proyecto": {"encontrado": True}, "plan": [tarea()],
                 "pasos": 1, "decisiones": 1, "contadores": {"normativa": 0, "vision": 0, "debate": 0},
                 "evidencia": [], "trayectoria": []}
        fake = v3.Decision(accion="normativa", tarea_id="T99", objetivo="Buscar", motivo="Verificar criterio")
        with patch.object(v3, "_llamar_modelo", return_value=fake):
            res = v3.decidir(state)
        self.assertEqual(res["decision"]["accion"], "finalizar")

    def test_cierre_limites_explica_pendientes(self):
        state = {"cui": "2017723", "proyecto": {"encontrado": True}, "plan": [tarea()],
                 "pasos": v3.MAX_PASOS, "decisiones": 9, "trayectoria": []}
        with patch.object(v3, "_llamar_modelo", side_effect=AssertionError("No API")):
            res = v3.auditar_cierre(state)
        self.assertEqual(res["plan"][0]["estado"], "bloqueada")
        self.assertIn("Límite", res["motivo_cierre"])

    def test_ciclo_completo_simulado(self):
        state = {"cui": "2017723"}
        ficha = {"encontrado": True, "cui": "2017723", "proyecto": {"NOMBRE_INVERSION": "Saneamiento"}}
        with patch.object(v3.base, "consultar_proyecto_v2", return_value=ficha):
            state.update(v3.cargar(state))
        plan_falso = v3.PlanInicial(tareas=[
            v3.PreguntaPlan(pregunta="¿Qué exige Marco?", criterio_cierre="Consultar página", requiere_normativa=True),
            v3.PreguntaPlan(pregunta="¿Hay expediente?", criterio_cierre="Evaluar disponibilidad")
        ])
        with patch.object(v3, "_llamar_modelo", return_value=plan_falso):
            state.update(v3.planificar(state))
        decision1 = v3.Decision(accion="normativa", tarea_id="T1", objetivo="Consultar norma", motivo="Verificar norma", consulta="saneamiento")
        with patch.object(v3, "_llamar_modelo", return_value=decision1):
            state.update(v3.decidir(state))
        self.assertEqual(v3.ruta_decision(state), "normativa")
        def fake_norm(st):
            return v3.base._registro_herramienta(st, "normativa", {
                "tipo": "normativa", "query": "agua", "resultados": [{"pagina": 35, "texto": "Tratamiento"}]})
        with patch.object(v3.base, "consultar_normativa", side_effect=fake_norm):
            state.update(v3.normativa(state))
        self.assertEqual(state["evidencia"][-1]["id"], "E1")
        reflexion = v3.Reflexion(que_aprendi="El Marco describe saneamiento", actualizaciones=[
            v3.Actualizacion(tarea_id="T1", estado="resuelta", hallazgo="Criterio recuperado", evidencia_ids=["E1:p35"])
        ])
        with patch.object(v3, "_llamar_modelo", return_value=reflexion):
            state.update(v3.reflexionar(state))
        self.assertEqual(state["plan"][0]["estado"], "resuelta")
        self.assertEqual(state["plan"][1]["estado"], "pendiente")
        dec2 = v3.Decision(accion="finalizar", objetivo="Diagnóstico preliminar", motivo="Expediente fuera de alcance")
        with patch.object(v3, "_llamar_modelo", return_value=dec2):
            state.update(v3.decidir(state))
        cierre = v3.Cierre(continuar_investigando=False, razon="Expediente no disponible", tareas_bloqueadas=[
            v3.Actualizacion(tarea_id="T2", estado="bloqueada", hallazgo="Ausencia de expediente", motivo_bloqueo="No es una herramienta local")
        ])
        with patch.object(v3, "_llamar_modelo", return_value=cierre):
            state.update(v3.auditar_cierre(state))
        self.assertEqual(v3.ruta_auditoria(state), "finalizar")
        with patch.object(v3.base, "finalizar", return_value={"diagnostico": {"requiere_revision_humana": True}, "trayectoria": state["trayectoria"]}):
            state.update(v3.finalizar(state))
        self.assertEqual([t["estado"] for t in state["plan"]], ["resuelta", "bloqueada"])
        self.assertEqual(state["diagnostico"]["version_motor"], "V3 - planning/reflection")

    def test_no_se_fuerza_investigacion_si_todo_resuelto(self):
        state = {"plan": [tarea(estado="resuelta")], "trayectoria": []}
        with patch.object(v3, "_llamar_modelo", side_effect=AssertionError("No API")):
            res = v3.auditar_cierre(state)
        self.assertFalse(res["auditoria"]["continuar"])

if __name__ == '__main__':
    unittest.main()
