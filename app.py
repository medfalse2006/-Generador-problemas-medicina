import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# 1. CONFIGURACIÓN VISUAL DEL SIMULADOR "CAYETANO DARK MODE"
# Layout Wide para usar toda la pantalla
st.set_page_config(
    page_title="Evaluador Médico de Alto Rendimiento",
    page_icon="🩺",
    layout="wide"
)

# Estilos CSS avanzados para el fondo caricaturizado y las tarjetas del chat
st.markdown("""
    <style>
    /* Fondo con patrón de nefronas y riñones caricaturizados */
    .main {
        background-color: #0f172a;
        background-image: 
            url("https://www.flaticon.com/free-icons/kidney" alt="Icono de riñón caricaturizado"),
            radial-gradient(circle, rgba(13, 148, 136, 0.1) 0%, transparent 70%);
        background-blend-mode: color-dodge, normal;
        background-size: 50px 50px, cover;
    }
    
    /* Estilo para las tarjetas de usuario y asistente */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    div[data-testid="stChatMessageAssistant"] {
        background-color: #1e293b;
        border-left: 6px solid #0d9488;
    }
    div[data-testid="stChatMessageUser"] {
        background-color: #0284c7;
        border-right: 6px solid #38bdf8;
    }
    </style>
    """, unsafe_allow_html=True)

# Banner Principal Estilizado como Academia Pro
st.markdown(
    """
    <div style="background-color: #1e293b; padding: 30px; border-radius: 15px; border-left: 8px solid #0d9488; margin-bottom: 25px; text-align:center;">
        <h1 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', sans-serif;">🩺 Evaluador Médico de Alto Rendimiento</h1>
        <p style="color: #38bdf8; margin: 5px 0 0 0; font-size: 16px;">Anatomía Renal, Fisiología Excretora y Correlación Clínica Avanzada</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Colocamos las imágenes estéticas (caricaturas) de riñones y nefronas en la cabecera
col_img1, col_img2 = st.columns(2)
with col_img1:
    st.markdown("#### 🔬 Estructura Macroscópica Renal (Caricatura Pro)")
    st.image("https://googleusercontent.com/image_collection/image_retrieval/4043755377061335671", caption="Riñón Humano - Filtración y Perfusión")
with col_img2:
    st.markdown("#### 🧬 Unidad Funcional Glomerular (Nivel Caricatura)")
    st.image("https://googleusercontent.com/image_collection/image_retrieval/11846583516994929919", caption="Microscopía de Nefrona - Complejo Tubular")

st.markdown("---")

# 2. Inicialización de la API de Google
if "GENAI_API_KEY" in st.secrets:
    api_key = st.secrets["GENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")

if not api_key:
    st.info("Por favor, introduce tu API Key para comenzar.")
    st.stop()

client = genai.Client(api_key=api_key)

# Inicialización de la memoria visual del chat y el texto
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "document_text" not in st.session_state:
    st.session_state["document_text"] = ""

# 3. INTERFAZ DE SUBIDA Y CONFIGURACIÓN "A PEDIDO"
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 📂 Repositorio de Documentos Médicos")
    uploaded_files = st.file_uploader(
        "Sube tus PDFs médicos (Clases, Guías, etc.):", 
        type=["pdf", "txt"], 
        accept_multiple_files=True
    )
with c2:
    st.markdown("### 🔢 Configuración del Simulador")
    st.image("https://googleusercontent.com/image_collection/image_retrieval/9803705964126412082", caption="Icono de Simulador Renal") # Caricatura del riñón con gafas
    num_preguntas = st.number_input("¿Cuántas preguntas deseas en este simulacro?", min_value=1, max_value=20, value=10)

def procesar_documentos(files):
    texto_combinado = ""
    for file in files:
        texto_combinado += f"\n\n--- INICIO DEL DOCUMENTO: {file.name} ---\n"
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            for page in reader.pages:
                texto_combinado += page.extract_text() or ""
        elif file.name.endswith(".txt"):
            texto_combinado += file.read().decode("utf-8")
        texto_combinado += f"\n--- FIN DEL DOCUMENTO: {file.name} ---\n"
    return texto_combinado

if uploaded_files and not st.session_state["document_text"]:
    with st.spinner("🧬 Analizando y cruzando la información de todos los PDFs médicos..."):
        st.session_state["document_text"] = procesar_documentos(uploaded_files)
        # Toast para avisar visualmente
        st.toast("¡Base de datos médica procesada y lista!", icon="✅")

st.markdown("---")
st.markdown("### 💬 Simulador de Casos Clínicos Activo")

# 4. TU PROMPT INMUTABLE DE SISTEMA (No lo toques)
PROMPT_SISTEMA = """
Eres un asistente académico de élite, experto en pedagogía médica y ciencias de la salud. Tu única función es analizar MÚLTIPLES PDFs, documentos o clases proporcionados por el usuario y generar un BANCO DE CASOS CLÍNICOS DE INTEGRACIÓN DE ALTO RENDIMIENTO (mínimo 10 casos, o los que el usuario te pida), utilizando la herramienta "Grounding with Google Search" para asegurar la máxima precisión científica.

REGLAS DE DISEÑO PARA LOS CASOS CLÍNICOS:
Cada caso clínico debe estar recontra detallado y obligatoriamente debe integrar los siguientes elementos cruzando la información de los documentos aportados:
1. ANTECEDENTES Y FÁRMACOS: El paciente debe presentar un historial médico relevante y el uso de medicamentos específicos (ej. diuréticos, antihipertensivos, AINEs, etc.) que alteren la fisiología normal.
2. PERFIL DE LABORATORIO COMPLETO: Debes incluir obligatoriamente valores séricos y urinarios pertinentes al caso (ej. electrolitos como Na+, K+, Cl-, Ca2+, gases arteriales como pH, pCO2, HCO3-, o marcadores como creatinina, urea, osmolaridad, etc.) con sus respectivas unidades de medida oficiales.
3. CORRELACIÓN MULTIVARIABLE: Las preguntas deben obligar al usuario a relacionar cómo el fármaco o la alteración estructural (histología/anatomía) explica los resultados de laboratorio y las manifestations clínicas del paciente (fisiopatología).

REGLA DE ORO DE FORMATO (SIMULACRO):
1. SIMULACRO LIMPIO: Presenta primero TODO el banco de casos clínicos de corrido con sus opciones (A, B, C, D). NO muestres la respuesta correcta ni la resolución debajo del caso. 
2. SOLUCIONARIO EXPLICATIVO AL FINAL: Al final de todo el mensaje, coloca una sección oculta con las claves y la resolución razonada paso a paso.

Estructura el banco obligatoriamente en este formato:

## 🩺 SIMULACRO DE INTEGRACIÓN CLÍNICA Y LABORATORIO

1. **[Plantea el caso detallado. Ejemplo: Paciente mujer de 65 años con antecedente de insuficiencia cardíaca en tratamiento crónico con Furosemida. Acude por debilidad muscular severa. Laboratorio sérico: Na+: 132 mEq/L, K+: 2.8 mEq/L, Cl-: 90 mEq/L, pH: 7.48, HCO3-: 32 mEq/L. Laboratorio urinario: K+ urinario elevado... [Pregunta de integración que obligue a correlacionar el mecanismo del fármaco con las alteraciones iónicas séricas/urinarias y el estado ácido-base]]**
   A) [Opción A]
   B) [Opción B]
   C) [Opción C]
   D) [Opción D]

2. **[Siguiente caso clínico con fármacos y analítica de laboratorio...]**
   A) ...
   B) ...

---

## 🔑 SOLUCIONARIO RAZONADO (INTEGRACIÓN)
<details>
<summary><b>👁️ CLIC AQUÍ PARA REVISAR EL RAZONAMIENTO CLÍNICO</b></summary>

### Resolución Paso a Paso:

* **Caso 1:** Clave **[X]**.
  - *Mecanismo Fisiológico Integrado:* Explica de forma minuciosa la correlación. (Ej: "La furosemida inhibe el cotransportador Na+/K+/2Cl- en la rama ascendente gruesa de Henle [Documento 1]. Esto bloquea la reabsorción de estos iones, explicando la pérdida de Cl- y Na+ en la analítica urinaria. La mayor llegada de flujo al túbulo colector preliminar estimula la secreción de K+ e H+, lo que desencadena la hipopotasemia severa (2.8 mEq/L) y la alcalosis metabólica evidenciada en el pH de 7.48 [Documento 2]...").
  - *Sustento de Internet:* [Aporte de Google Search que valide las constantes o guías clínicas].
  - *Fuentes integradas:* [Manuales o guías oficiales].

* **Caso 2:** Clave **[X]**.
  - *Mecanismo Fisiológico Integrado:* [...]
</details>
"""

# 5. Renderizar el historial visual en la pantalla
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. Cuadro de chat e interacción directa
if user_input := st.chat_input(f"Pídele los problemas aquí (Ej: Genera los primeros {num_preguntas} casos clínicos sobre fisiología renal)"):
    
    if not st.session_state["document_text"]:
        st.warning("Por favor, sube primero los documentos para poder procesar la información.")
    else:
        # Añadir mensaje del usuario a la pantalla
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # Llamada directa al modelo estable
        with st.chat_message("assistant"):
            with st.spinner("🧬 Analizando variables médicas..."):
                try:
                    # Armando el historial del chat para enviarlo de golpe en el formato de la nueva API
                    contexto_peticion = (
                        f"Documentos base cargados:\n{st.session_state['document_text']}\n\n"
                        f"Historial previo de la conversación:\n{st.session_state['chat_history']}\n\n"
                        f"Nueva instrucción del alumno: {user_input}"
                    )
                    
                    # Llamada usando la sintaxis ultra estable de la nueva API y el modelo gemini-2.5-flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contexto_peticion,
                        config=types.GenerateContentConfig(
                            system_instruction=PROMPT_SISTEMA
                        )
                    )
                    
                    respuesta_texto = response.text
                    st.write(respuesta_texto)
                    st.session_state["chat_history"].append({"role": "assistant", "content": respuesta_texto})
                    
                except Exception as e:
                    st.error(f"Ocurrió un error crítico en el servidor de Google: {e}")
