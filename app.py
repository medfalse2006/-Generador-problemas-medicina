import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader
import json
import re

# 1. CONFIGURACIÓN DE LA PÁGINA (Estilo Ancho y Clínico)
st.set_page_config(
    page_title="Evaluador Médico de Élite",
    page_icon="🩺",
    layout="wide"
)

# Estilos CSS para el fondo oscuro y las tarjetas
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    div[data-testid="stExpander"] { background-color: #1e293b; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Banner Principal con Imágenes Estéticas del Aparato Excretor
st.markdown(
    """
    <div style="background-color: #1e293b; padding: 30px; border-radius: 15px; border-left: 8px solid #0d9488; margin-bottom: 25px; text-align:center;">
        <h1 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">🩺 Sistema de Simulacros Médicos Interactivos</h1>
        <p style="color: #38bdf8; margin: 5px 0 0 0; font-size: 16px;">Anatomía Renal, Fisiología Excretora y Correlación Clínica Avanzada</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Colocamos las imágenes estéticas de riñones y nefronas en la cabecera usando columnas
col_img1, col_img2 = st.columns(2)
with col_img1:
    st.markdown("#### 🔬 Estructura Macroscópica Renal")
    st.image("https://images.unsplash.com/photo-1530026405186-ed1ea0ac7a63?auto=format&fit=crop&w=600&q=80", caption="Riñón Humano - Filtración y Perfusión Sanguínea")
with col_img2:
    st.markdown("#### 🧬 Unidad Funcional Glomerular")
    st.image("https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&w=600&q=80", caption="Microscopía de Nefrona - Complejo Tubular")

st.markdown("---")

# 2. CONFIGURACIÓN DE LA API KEY
if "GENAI_API_KEY" in st.secrets:
    api_key = st.secrets["GENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")

if not api_key:
    st.info("Por favor, introduce tu API Key para comenzar.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. CONTROL DE ESTADOS (Para que las preguntas no se borren al hacer clic)
if "document_text" not in st.session_state:
    st.session_state["document_text"] = ""
if "banco_preguntas" not in st.session_state:
    st.session_state["banco_preguntas"] = []
if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}

# 4. INTERFAZ DE SUBIDA Y CONFIGURACIÓN
c1, c2 = st.columns([2, 1])

with c1:
    uploaded_files = st.file_uploader("📂 Sube tus PDFs médicos (Clases, Guías, etc.):", type=["pdf", "txt"], accept_multiple_files=True)
with c2:
    num_preguntas = st.number_input("🔢 ¿Cuántas preguntas deseas en este simulacro?", min_value=1, max_value=20, value=5)

def extraer_texto(files):
    texto = ""
    for f in files:
        if f.name.endswith(".pdf"):
            reader = PdfReader(f)
            for page in reader.pages:
                texto += page.extract_text() or ""
        else:
            texto += f.read().decode("utf-8")
    return texto

if uploaded_files and not st.session_state["document_text"]:
    st.session_state["document_text"] = extraer_texto(uploaded_files)
    st.toast("¡Documentos médicos procesados con éxito!", icon="✅")

# Botón para detonar la generación en formato JSON estructurado
if st.button("🚀 Generar Simulacro Interactivo"):
    if not st.session_state["document_text"]:
        st.warning("Primero sube tus PDFs.")
    else:
        with st.spinner("🧬 Forjando casos clínicos y estructurando alternativas..."):
            # Prompt modificado para obligar a Gemini a responder en formato JSON limpio de programación
            PROMPT_JSON = f"""
            Eres un evaluador médico de élite. Analiza los documentos proporcionados y genera exactamente {num_preguntas} casos clínicos de integración de alto rendimiento.
            Cruza datos de: Antecedentes, Fármacos usados, y Perfil de Laboratorio completo (Valores séricos y urinarios con unidades oficiales).
            
            DEBES responder ÚNICAMENTE con un arreglo JSON puro, sin markdown, sin texto extra.
            Formato del JSON exacto:
            [
              {{
                "id": 1,
                "caso": "Paciente varón de...",
                "opciones": {{"A": "Texto A", "B": "Texto B", "C": "Texto C", "D": "Texto D"}},
                "correcta": "A",
                "porque_si": "Explicación detallada de por qué esta es la correcta basada en la fisiología renal...",
                "porque_no": "Explicación de por qué las otras alternativas son distractores erróneos..."
              }}
            ]
            
            Documento base: {st.session_state["document_text"]}
            """
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_JSON
                )
                
                # Limpiar la respuesta de posibles bloques de código de markdown ```json ... ```
                raw_text = response.text.strip()
                clean_json = re.sub(r'^```json\s*|```$', '', raw_text, flags=re.MULTILINE).strip()
                
                st.session_state["banco_preguntas"] = json.loads(clean_json)
                st.session_state["respuestas_usuario"] = {} # Resetear respuestas anteriores
                st.success("¡Simulacro construido! Responde las preguntas abajo.")
            except Exception as e:
                st.error(f"Error al estructurar las preguntas: {e}. Intenta darle al botón otra vez.")

# 5. RENDERIZADO DEL EXAMEN INTERACTIVO (Rojo / Verde dinámico)
if st.session_state["banco_preguntas"]:
    st.markdown("## 📝 EXAMEN DE INTEGRACIÓN CLÍNICA")
    
    for q in st.session_state["banco_preguntas"]:
        q_id = str(q["id"])
        
        # Tarjeta para cada caso clínico
        with st.container():
            st.markdown(f"### Caso Clínico {q_id}")
            st.info(q["caso"])
            
            # Formatear las opciones para el botón de radio
            opciones_lista = [f"A) {q['opciones']['A']}", f"B) {q['opciones']['B']}", f"C) {q['opciones']['C']}", f"D) {q['opciones']['D']}"]
            
            # Elige opción (empieza vacío para no dar la respuesta)
            opcion_elegida = st.radio(
                f"Selecciona tu respuesta para el Caso {q_id}:",
                options=["Sin responder"] + opciones_lista,
                key=f"radio_{q_id}"
            )
            
            if opcion_elegida != "Sin responder":
                letra_elegida = opcion_elegida[0] # Sacamos la 'A', 'B', 'C' o 'D'
                
                # VALIDACIÓN: ¿Es correcto o incorrecto?
                if letra_elegida == q["correcta"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #dcfce7; color: #15803d; padding: 15px; border-radius: 8px; border: 2px solid #22c55e; margin-top: 10px;">
                            <strong style="font-size: 18px;">✅ ¡CORRECTO! Marcase la opción {q['correcta']}</strong><br><br>
                            <b>Fisiopatología de la respuesta:</b> {q['porque_si']}
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div style="background-color: #fee2e2; color: #b91c1c; padding: 15px; border-radius: 8px; border: 2px solid #ef4444; margin-top: 10px;">
                            <strong style="font-size: 18px;">❌ INCORRECTO. Marcaste la {letra_elegida} (La correcta era la {q['correcta']})</strong><br><br>
                            <b>¿Por qué fallaste?:</b> {q['porque_no']}<br><br>
                            <b>Sustento Fisiológico de la clave correcta:</b> {q['porque_si']}
                        </div>
                        """, unsafe_allow_html=True
                    )
            st.markdown("<br><hr style='border-top: 1px dashed #cccccc;'><br>", unsafe_allow_html=True)
