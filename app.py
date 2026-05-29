import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader

# 1. Configuración visual
st.set_page_config(
    page_title="Generador de Casos Clínicos de Élite",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 Evaluador Médico de Alto Rendimiento")
st.write("Sube tus documentos médicos. La IA generará un banco de casos clínicos integrando antecedentes, fármacos y analíticas.")

# 2. Inicialización del Cliente de la API de Google (Nuevo método oficial)
if "GENAI_API_KEY" in st.secrets:
    api_key = st.secrets["GENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")

if not api_key:
    st.info("Por favor, introduce tu API Key para comenzar.")
    st.stop()

# Inicializamos el cliente moderno
client = genai.Client(api_key=api_key)

# 3. Inicialización de la memoria visual del chat
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "document_text" not in st.session_state:
    st.session_state["document_text"] = ""

# 4. Cargador de archivos múltiples
uploaded_files = st.file_uploader(
    "Sube tus documentos de estudio (PDF o TXT):", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)

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
    with st.spinner("Analizando y procesando base de datos médica..."):
        st.session_state["document_text"] = procesar_documentos(uploaded_files)
        st.success("¡Documentos cargados con éxito! Ya puedes pedir tus casos clínicos abajo.")

# 5. TU PROMPT CONFIGURADO COMO INSTRUCCIÓN DE SISTEMA
PROMPT_SISTEMA = """
Eres un asistente académico de élite, experto en pedagogía médica y ciencias de la salud. Tu única función es analizar MÚLTIPLES PDFs, documentos o clases proporcionados por el usuario y generar un BANCO DE CASOS CLÍNICOS DE INTEGRACIÓN DE ALTO RENDIMIENTO (mínimo 10 casos, o los que el usuario te pida), utilizando la herramienta "Grounding with Google Search" para asegurar la máxima precisión científica.

REGLAS DE DISEÑO PARA LOS CASOS CLÍNICOS:
Cada caso clínico debe estar recontra detallado y obligatoriamente debe integrar los siguientes elementos cruzando la información de los documentos aportados:
1. ANTECEDENTES Y FÁRMACOS: El paciente debe presentar un historial médico relevante y el uso de medicamentos específicos (ej. diuréticos, antihipertensivos, AINEs, etc.) que alteren la fisiología normal.
2. PERFIL DE LABORATORIO COMPLETO: Debes incluir obligatoriamente valores séricos y urinarios pertinentes al caso (ej. electrolitos como Na+, K+, Cl-, Ca2+, gases arteriales como pH, pCO2, HCO3-, o marcadores como creatinina, urea, osmolaridad, etc.) con sus respectivas unidades de medida oficiales.
3. CORRELACIÓN MULTIVARIABLE: Las preguntas deben obligar al usuario a relacionar cómo el fármaco o la alteración estructural (histología/anatomía) explica los resultados de laboratorio y las manifestaciones clínicas del paciente (fisiopatología).

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

# 6. Mostrar el historial visual en la pantalla
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 7. Cuadro de chat e interacción directa
if user_input := st.chat_input("Pídele el simulacro aquí (Ej: Genera 10 casos clínicos sobre fisiología renal)"):
    
    if not st.session_state["document_text"]:
        st.warning("Por favor, sube primero los documentos para poder procesar la información.")
    else:
        # Añadir mensaje del usuario a la pantalla
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # Llamada directa al modelo estable
        with st.chat_message("assistant"):
            with st.spinner("Procesando variables médicas..."):
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
                    st.error(f"Error crítico en el servidor de Google: {e}")
