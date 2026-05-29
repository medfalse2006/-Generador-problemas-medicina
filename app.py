import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Configuración de la interfaz gráfica de la aplicación
st.set_page_config(
    page_title="Generador de Casos Clínicos de Élite",
    page_icon="🩺",
    layout="centered"
)

st.title("🩺 Evaluador Médico de Alto Rendimiento")
st.write("Sube una o varias clases, PDFs o guías médicas. La IA generará un banco de casos clínicos integrando antecedentes, fármacos y analíticas de laboratorio basados en tus documentos.")

# 2. Conexión segura con la API Key de Google
if "GENAI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GENAI_API_KEY"])
else:
    api_key_manual = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password")
    if api_key_manual:
        genai.configure(api_key=api_key_manual)
    else:
        st.info("Por favor, introduce tu API Key en la barra lateral para comenzar.")

# 3. Inicialización del chat y almacenamiento del texto en la sesión
if "chat_gemini" not in st.session_state:
    st.session_state["chat_gemini"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 4. Zona de carga de MÚLTIPLES archivos (PDF o TXT) tal como pide tu prompt
uploaded_files = st.file_uploader(
    "Sube tus documentos de estudio (Puedes seleccionar varios PDFs o TXT a la vez):", 
    type=["pdf", "txt"], 
    accept_multiple_files=True
)

# Función para extraer y concatenar el texto de todos los archivos subidos
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

# 5. Inicializar la conversación nativa en cuanto se detecten los archivos
if uploaded_files and st.session_state["chat_gemini"] is None:
    with st.spinner("Procesando y cruzando la información de todos los documentos..."):
        texto_completo = procesar_documentos(uploaded_files)
        
        if texto_completo.strip():
            # TU PROMPT EXACTO CONFIGURADO COMO INSTRUCCIÓN DE SISTEMA PERMANENTE
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

            # Inicializamos el modelo con tu prompt inyectado nativamente
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=PROMPT_SISTEMA
            )
            
            # Iniciamos el chat y le entregamos todos los documentos juntos en el primer turno
            st.session_state["chat_gemini"] = model.start_chat(history=[
                {
                    "role": "user",
                    "parts": [f"Aquí tienes el contenido de todos los documentos y clases cargadas para trabajar:\n\n{texto_completo}"]
                },
                {
                    "role": "model",
                    "parts": ["Entendido a la perfección. He analizado todos los documentos aportados y memorizado las reglas de diseño y formato. Estoy listo para generar el banco de casos clínicos de alto rendimiento con integración multivariable. ¿Qué temas o cuántos casos clínicos te gustaría que empiece a formular?"]
                }
            ])
            
            # Guardamos el saludo inicial en la pantalla de la app
            st.session_state["chat_history"] = [
                {"role": "assistant", "content": "¡Documentos cargados con éxito! Estoy listo para generar tus casos clínicos de alto rendimiento con formato de simulacro y solucionario oculto. ¿Qué temas específicos deseas priorizar?"}
            ]
            st.success("¡Base de datos médica procesada y lista!")
        else:
            st.error("No se pudo extraer texto legible de los archivos seleccionados.")

# 6. Renderizar el historial visual de los mensajes en la pantalla
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 7. Cuadro de texto interactivo para el usuario
if user_input := st.chat_input("Pídele el banco aquí (Ej: Genera los primeros 10 casos clínicos sobre fisiología renal)"):
    
    if st.session_state["chat_gemini"] is None:
        st.warning("Primero debes subir al menos un documento para activar el evaluador.")
    else:
        # Añadir y renderizar el mensaje de tu amigo
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
            
        # Enviar la solicitud de forma limpia al chat nativo de Gemini
        with st.chat_message("assistant"):
            with st.spinner("Analizando variables médicas y estructurando simulacro..."):
                try:
                    # La API maneja la memoria sola y aplica tus reglas estrictas de formato y diseño
                    response = st.session_state["chat_gemini"].send_message(user_input)
                    respuesta_texto = response.text
                    
                    st.write(respuesta_texto)
                    st.session_state["chat_history"].append({"role": "assistant", "content": respuesta_texto})
                except Exception as e:
                    st.error(f"Ocurrió un error en la comunicación con el servidor: {e}")
