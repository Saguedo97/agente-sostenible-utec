from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


Categoria = Literal[
    "Edificios verdes",
    "Energía renovable",
    "Eficiencia energética",
    "Transporte bajo en carbono",
    "Gestión eficiente y resiliente de aguas y aguas residuales",
    "Gestión sostenible de recursos naturales, uso de suelos y áreas marinas protegidas",
    "Agricultura sostenible",
    "Manejo sostenible de residuos",
    "No aplica",
    "Información insuficiente",
]


class MarcoLogicoExtract(BaseModel):
    encontrado: bool = True
    objetivo: str | None = None
    problema_central: str | None = None
    componentes: list[str] = Field(default_factory=list)
    actividades: list[str] = Field(default_factory=list)
    beneficiarios: str | None = None
    brecha_o_necesidad: str | None = None
    observaciones: list[str] = Field(default_factory=list)


class ClasificacionPropuesta(BaseModel):
    cui: str
    clasificacion: Categoria
    criterio_principal: str | None = None
    paginas_marco: list[int] = Field(default_factory=list)
    evidencia_proyecto: list[str] = Field(default_factory=list)
    evidencia_brechas: list[str] = Field(default_factory=list)
    evidencia_marco: list[str] = Field(default_factory=list)
    evidencia_marco_logico: list[str] = Field(default_factory=list)
    justificacion: str
    evidencia_suficiente: bool
    requiere_revision_humana: bool


class VeredictoVerificador(BaseModel):
    aprobado: bool
    categoria_sustentada: bool
    evidencia_suficiente: bool
    problemas: list[str] = Field(default_factory=list)
    feedback_para_agente: str = ""


class ResultadoFinal(BaseModel):
    cui: str
    clasificacion: Categoria
    criterio_principal: str | None = None
    paginas_marco: list[int] = Field(default_factory=list)
    evidencia_proyecto: list[str] = Field(default_factory=list)
    evidencia_brechas: list[str] = Field(default_factory=list)
    evidencia_marco: list[str] = Field(default_factory=list)
    evidencia_marco_logico: list[str] = Field(default_factory=list)
    justificacion: str
    evidencia_suficiente: bool
    requiere_revision_humana: bool
    estado: Literal["APROBADO", "REVISION_HUMANA"]
    iteraciones: int
    herramientas_utilizadas: list[str] = Field(default_factory=list)
    consultas_marco: list[str] = Field(default_factory=list)
