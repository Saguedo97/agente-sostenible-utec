from __future__ import annotations

import streamlit as st

from graph import clasificar_cui

st.set_page_config(
    page_title="Agente de Clasificación Sostenible",
    layout="wide",
)

st.title("Agente de Clasificación Sostenible")
st.caption(
    "Clasificación preliminar de proyectos públicos contra el Marco del Bono "
    "Sostenible del Perú 2021."
)

cui = st.text_input("CUI", value="2017723")

if st.button("Clasificar proyecto", type="primary"):
    with st.spinner("El agente está recopilando y verificando evidencia..."):
        try:
            state = clasificar_cui(cui)
            r = state["resultado"]

            st.subheader(r["clasificacion"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Estado", r["estado"])
            c2.metric("Iteraciones", r["iteraciones"])
            c3.metric(
                "Evidencia suficiente",
                "Sí" if r["evidencia_suficiente"] else "No",
            )

            st.markdown("### Justificación")
            st.write(r["justificacion"])

            st.markdown("### Criterio normativo")
            st.write(r["criterio_principal"] or "—")
            st.write("Páginas del Marco:", r["paginas_marco"])

            with st.expander("Evidencia del proyecto"):
                st.write(r["evidencia_proyecto"])
                st.write(r["evidencia_brechas"])

            with st.expander("Evidencia normativa"):
                st.write(r["evidencia_marco"])

            with st.expander("Marco lógico"):
                st.write(r["evidencia_marco_logico"])

            with st.expander("Trayectoria auditable"):
                st.json(state.get("trajectory", []))
                st.write("Herramientas:", r["herramientas_utilizadas"])
                st.write("Consultas RAG:", r["consultas_marco"])

            if r["requiere_revision_humana"]:
                st.warning("Este caso requiere revisión humana.")
        except Exception as e:
            st.error(str(e))
