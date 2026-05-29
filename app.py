import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Simulador Renal e Integración Médica",
    page_icon="🩺",
    layout="wide"
)

# Estilos visuales oscuros premium
st.markdown("""
    <style>
    .main { 
        background-color: #0f172a; 
        background-image: radial-gradient(circle, rgba(13, 148, 136, 0.15) 0%, transparent 80%);
    }
    div[data-testid="stExpander"] { background-color: #1e293b; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Banner Principal
st.markdown(
    """
    <div style="background-color: #1e293b; padding: 25px; border-radius: 15px; border-left: 8px solid #0d9488; margin-bottom: 25px; text-align:center;">
        <h1 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">🩺 Plataforma de Evaluación Médica Adaptativa</h1>
        <p style="color: #38bdf8; margin: 5px 0 0 0; font-size: 15px;">Simulacros de Fisiología Renal, Aparato Excretor y Casos de Alto Rendimiento</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Cabecera gráfica con imágenes estables de banco médico
col_img1, col_img2 = st.columns(2)
with col_img1:
    st.image("https://images.unsplash.com/photo-1530026405186-ed1ea0ac7a63?auto=format&fit=crop&w=500&q=80", caption="Anatomía Macrovascular Renal")
with col_img2:
    st.image("https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&w=500&q=80", caption="Fisiología Molecular de la Nefrona")

st.markdown("---")

# 2. CONFIGURACIÓN DE LA API KEY (Google Secrets)
if "GENAI_API_KEY" in st.secrets:
    api_key = st.secrets["GENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")

if not api_key:
    st.info("Por favor, configura tu GENAI_API_KEY en Streamlit Secrets para activar la app.")
    st.stop()

client = genai.Client(api_key=api_key)

# Inicialización de estados de memoria
if "document_text" not in st.session_state:
    st.session_state["document_text"] = ""
if "resultado_simulacro" not in st.session_state:
    st.session_state["resultado_simulacro"] = ""

# 3. INTERFAZ DE CONTROL Y CONFIGURACIÓN MULTI-MODO
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown("##### 📂 1. Carga tus PDFs de Clase")
    uploaded_files = st.file_uploader("Arrastra aquí tus archivos médicos:", type=["pdf", "txt"], accept_multiple_files=True)
with c2:
    st.markdown("##### 🧠 2. Elige el Enfoque")
    tipo_examen = st.selectbox(
        "Selecciona el estilo de preguntas:",
        ["Casos Clínicos de Integración (Pro)", "Conceptos Clave y Memorísticos (Directo)"]
    )
with c3:
    st.markdown("##### 🔢 3. Extensión")
    num_preguntas = st.number_input("Cantidad de preguntas:", min_value=1, max_value=30, value=10)

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
    st.toast("¡Base de datos médica lista para procesar!", icon="✅")

st.markdown("---")

# 4. FUSIÓN DINÁMICA DE TUS DOS PROMPTS DE ÉLITE
PROMPT_SISTEMA_HIBRIDO = f"""
Eres un asistente académico de élite, experto en pedagogía médica y ciencias de la salud. Tu única función es analizar los PDFs o documentos de la clase proporcionados por el usuario y generar un BANCO DE PREGUNTAS DE OPCIÓN MÚLTIPLE (exactamente {num_preguntas} preguntas, o las que el usuario te pida), utilizando la herramienta "Grounding with Google Search" para asegurar la máxima precisión científica.

Dependiendo de la selección del alumno, moldearás el diseño de evaluación siguiendo estrictamente uno de los siguientes dos enfoques:

---
[SI EL ALUMNO PIDE: "Casos Clínicos de Integración (Pro)"]
REGLAS DE DISEÑO:
Cada caso clínico debe estar recontra detallado y obligatoriamente debe integrar:
1. ANTECEDENTES Y FÁRMACOS: El paciente debe presentar un historial médico relevante y el uso de medicamentos específicos (ej. diuréticos, antihipertensivos, AINEs, etc.) que alteren la fisiología normal.
2. PERFIL DE LABORATORIO COMPLETO: Valores séricos y urinarios pertinentes al caso (ej. electrolitos como Na+, K+, Cl-, Ca2+, gases arteriales como pH, pCO2, HCO3-, o marcadores como creatinina, urea, osmolaridad, etc.) con sus respectivas unidades de medida oficiales.
3. CORRELACIÓN MULTIVARIABLE: Las preguntas deben obligar al usuario a relacionar cómo el fármaco o la alteración estructural (histología/anatomía) explica los resultados de laboratorio y las manifestaciones clínicas del paciente (fisiopatología).

REGLA DE ORO DE FORMATO:
1. SIMULACRO LIMPIO: Presenta primero TODO el banco de casos de corrido con sus opciones (A, B, C, D). NO muestres respuestas ni resolución debajo de cada caso.
2. SOLUCIONARIO EXPLICATIVO AL FINAL: Al final de todo el mensaje, coloca una sección oculta usando <details><summary><b>🔑 SOLUCIONARIO RAZONADO (INTEGRACIÓN)</b></summary>...</details> detallando el mecanismo fisiológico integrado, sustento de internet y fuentes.

---
[SI EL ALUMNO PIDE: "Conceptos Clave y Memorísticos (Directo)"]
REGLAS DE DISEÑO:
Las preguntas deben ser directas, conceptuales y memorísticas (ej. "¿Qué molécula...?", "¿Cuál es el valor de...?", "¿Cuál es el canal responsable de...?"), basándose fielmente en el PDF de la clase pero utilizando internet para validar la precisión de las constantes biológicas o moleculares.

REGLA DE ORO DE FORMATO:
1. CUESTIONARIO LIMPIO: Presenta primero TODO el banco de preguntas de corrido, una detrás de otra, con sus opciones (A, B, C, D). Sin spoilers.
2. CLAVE DE RESPUESTAS AL FINAL: Al final de todo el mensaje, coloca una sección oculta usando <details><summary><b>🔑 HOJA DE RESPUESTAS (CORRECCIÓN)</b></summary>...</details> detallando la justificación de la clave y su respectiva fuente bibliográfica médica.
"""

# 5. BOTÓN DE DISPARO DIRECTO (REEMPLAZA AL CHAT INPUT REDUNDANTE)
st.markdown("### 🧬 Panel de Ejecución")
if st.button("🚀 Generar Simulacro Personalizado", type="primary", use_container_width=True):
    if not st.session_state["document_text"]:
        st.warning("Por favor, sube primero los documentos médicos en la zona superior.")
    else:
        with st.spinner("🧬 Cruzando datos bibliográficos y estructurando tu bloque de evaluación..."):
            try:
                contexto_peticion = (
                    f"[MODO DE EVALUACIÓN ACTIVADO POR EL ALUMNO]: {tipo_examen}\n"
                    f"Texto extraído de los PDFs cargados:\n{st.session_state['document_text']}\n\n"
                    f"Instrucción actual: Genera el bloque completo de {num_preguntas} preguntas."
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contexto_peticion,
                    config=types.GenerateContentConfig(
                        system_instruction=PROMPT_SISTEMA_HIBRIDO
                    )
                )
                
                st.session_state["resultado_simulacro"] = response.text
                
            except Exception as e:
                st.error(f"Error en los servidores de Google: {e}")

# 6. MOSTRAR EL EXAMEN IMPRESO EN PANTALLA
if st.session_state["resultado_simulacro"]:
    st.markdown("---")
    st.markdown("### 📝 TU SIMULACRO GENERADO")
    st.write(st.session_state["resultado_simulacro"])

# 7. TABLERO DE RESPUESTAS RÁPIDAS
if st.session_state["resultado_simulacro"]:
    st.markdown("---")
    st.markdown("### 🎛️ Tablero Interactivo de Respuestas")
    st.write("Comprueba rápido tus alternativas del simulacro impreso arriba:")
    
    col_check1, col_check2 = st.columns([1, 2])
    with col_check1:
        letra = st.pills("Tu alternativa:", ["A", "B", "C", "D"])
        estado = st.toggle("¿Coincide con el solucionario oculto?")
    
    with col_check2:
        if letra:
            if estado:
                st.markdown(
                    f"""
                    <div style="background-color: #dcfce7; color: #15803d; padding: 15px; border-radius: 8px; border: 2px solid #22c55e;">
                        <strong>✅ ¡Excelente! La opción {letra} es correcta.</strong> La correlación molecular está bien fijada.
                    </div>
                    """, unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #fee2e2; color: #b91c1c; padding: 15px; border-radius: 8px; border: 2px solid #ef4444;">
                        <strong>❌ La opción {letra} es incorrecta.</strong> Despliega la pestaña del solucionario arriba para repasar el fundamento clínico.
                    </div>
                    """, unsafe_allow_html=True
                )
