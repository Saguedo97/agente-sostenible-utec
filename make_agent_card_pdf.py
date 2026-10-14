"""Generador de PDF de una página. No es necesario para ejecutar el agente."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

OUT=Path(__file__).resolve().parent / 'docs' / 'AGENT_CARD_V2.pdf'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font_b='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DejaVu',font))
pdfmetrics.registerFont(TTFont('DejaVuBold',font_b))
W,H=1190,842
navy=HexColor('#173E37');teal=HexColor('#2F806B');light=HexColor('#EEF7F3');gray=HexColor('#5A6A67');line=HexColor('#CEDFD8')
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('Agentic Profile Card V2 - UTEC')
c.setFillColor(navy);c.rect(0,H-112,W,112,fill=1,stroke=0)
c.setFont('DejaVuBold',25);c.setFillColor(HexColor('#FFFFFF'));c.drawString(48,H-47,'AGENTIC PROFILE CARD · V2')
c.setFont('DejaVu',14);c.setFillColor(HexColor('#CFEAE1'));c.drawString(49,H-78,'Investigador de elegibilidad sostenible · Inversión pública del Perú')
c.setFont('DejaVu',9);c.setFillColor(gray)
c.drawString(48,H-136,'UTEC · Proyecto académico  |  Repositorio: Saguedo97/agente-sostenible-utec  |  Octubre 2026')
c.setFillColor(HexColor('#F8FBFA'));c.rect(34,45,W-68,H-194,fill=1,stroke=0)

cards=[
 ('01 · DOMAIN / PROBLEMA',[
  'AS-IS: CUI → consulta → clasificación. Repetir 10 o 100 CUIs es un workflow.',
  'TO-BE: investigar hipótesis normativas, evidencia ausente y condiciones pendientes.',
  '~500K proyectos históricos; 121,477 en el subconjunto 2023–2026; 423 etiquetados.'
 ]),
 ('02 · OBJECTIVES / RESULTADO',[
  'Planificar y replantear investigaciones de elegibilidad preliminar.',
  'Distinguir requisitos respaldados, incertidumbres y documentos faltantes.',
  'Entregar diagnóstico, justificación, acciones y trayectoria auditables.'
 ]),
 ('03 · AUTONOMY / REPLANNING',[
  'Supervisor LLM decide: normativa, visión, contraste experto o finalizar.',
  'El plan cambia cuando la evidencia observada lo justifica.',
  'No ejecuta siempre todas las herramientas. Límites: 6 pasos, 3 RAG, 1 visión y 1 contraste.'
 ]),
 ('04 · ENVIRONMENT / STACK',[
  'LangGraph + LangChain + OpenAI + Streamlit + SQLite local.',
  'Fuentes: 423 CUIs sin ground truth, 121K CUIs indexados, Marco 2021.',
  'RAG 8 categorías verdes; visión documental opcional; opiniones independientes.'
 ]),
 ('05 · CRITICALITY / GOVERNANCE',[
  'No certifica ni aprueba bonos o financiamiento; revisión humana indicada.',
  'Restringe páginas citadas a las recuperadas; permite abstenerse.',
  'Evita fuga de etiquetas históricas; presupuestos y controles de herramientas.'
 ]),
 ('06 · EVALUATION / ACCEPTANCE',[
  'Comparar V1 contra V2 en casos claros, ambiguos e incompletos.',
  'Medir pertinencia de tool calls, cambios de plan, latencia, costo y evidencia.',
  'Sin evidencia empírica, NO afirmar superioridad; validación humana pendiente.'
 ])
]
positions=[(48,506),(650,506),(48,289),(650,289),(48,72),(650,72)]
CW=492;CH=196
for (title, bullets),(x,y) in zip(cards,positions):
 c.setFillColor(HexColor('#FFFFFF'));c.roundRect(x,y,CW,CH,10,fill=1,stroke=0)
 c.setStrokeColor(line);c.roundRect(x,y,CW,CH,10,fill=0,stroke=1)
 c.setFillColor(light);c.roundRect(x+12,y+CH-47,CW-24,35,7,fill=1,stroke=0)
 c.setFillColor(teal);c.setFont('DejaVuBold',11.6);c.drawString(x+23,y+CH-34,title)
 current=y+CH-68
 for bullet in bullets:
  wrapped=simpleSplit(bullet,'DejaVu',10, CW-69)
  c.setFillColor(teal);c.circle(x+23,current+3,3,fill=1,stroke=0)
  c.setFillColor(navy);c.setFont('DejaVu',10)
  for j,row in enumerate(wrapped):
   c.drawString(x+36,current-j*16,row)
  current-=len(wrapped)*16+11
c.setFillColor(navy);c.setFont('DejaVuBold',9.4)
c.drawString(48,25,'ESTADO: PROTOTIPO V2 · No desplegado ni evaluado con OpenAI en esta entrega. El sistema conserva la V1 como baseline.')
c.save(); print(OUT)
