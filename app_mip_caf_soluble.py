import streamlit as st
from PIL import Image
from google import genai

# Configuración de la página
st.set_page_config(
    page_title="MIP Assistant - Café Soluble",
    page_icon="🪲",
    layout="centered"
)

# Título e Introducción
st.title("🪲 Asistente MIP - Identificación de Plagas")
st.caption("Herramienta basada en Gemini para control de calidad e inocuidad alimentaria en Café Soluble")

# Configuración de API Key de Gemini
api_key = st.sidebar.text_input("Ingrese su Gemini API Key", type="password")

if not api_key:
    st.info("Por favor, ingrese su API Key en la barra lateral para activar el análisis con Gemini.", icon="🔑")
    st.markdown("""
    ---
    ### ¿Cómo funciona esta herramienta?
    1. **Captura:** Tome una foto directa desde la cámara de su celular/laptop o suba una imagen de la muestra.
    2. **Contexto:** Indique la zona de la planta (bodega, empaque, exterior).
    3. **Análisis Multimodal:** Gemini analiza la morfología del insecto (énfasis en **Coleópteros** y **Lepidópteros**).
    4. **Diagnóstico y Protocolo:** Obtenga la identificación, nivel de riesgo y las acciones correctivas del plan MIP al instante.
    """)
    st.stop()

# Inicialización del cliente oficial de Google GenAI
client = genai.Client(api_key=api_key)

# Selector de fuente de imagen (Cámara o Archivo)
st.subheader("1. Captura o Selección de Muestra")
opcion_imagen = st.radio("Seleccione el método de entrada:", ("Cargar imagen desde archivo", "Cámara en vivo"))

imagen_input = None

if opcion_imagen == "Cámara en vivo":
    foto_camara = st.camera_input("Tome una foto clara del insecto o trampa")
    if foto_camara:
        imagen_input = Image.open(foto_camara)
else:
    archivo_subido = st.file_uploader("Suba una imagen (JPG, PNG)", type=["jpg", "jpeg", "png"])
    if archivo_subido:
        imagen_input = Image.open(archivo_subido)

# Procesamiento cuando hay una imagen disponible
if imagen_input:
    st.image(imagen_input, caption="Muestra seleccionada para inspección", use_container_width=True)
    
    st.subheader("2. Contexto de Ubicación")
    ubicacion = st.selectbox(
        "Área de hallazgo en planta:",
        [
            "Bodega de Materia Prima (Café Oro / Granos)",
            "Línea de Molienda / Extracción",
            "Línea de Envasado / Empaque",
            "Bodega de Producto Terminado",
            "Estaciones / Trampas de Luz Exterior",
            "Otra área"
        ]
    )
    
    notas_adicionales = st.text_input(
        "Observaciones o hallazgos adicionales (opcional):",
        placeholder="Ej: Encontrado en trampa adhesiva #8, presencia de restos de producto acumulado..."
    )

    # Botón de ejecución
    if st.button("🔍 Diagnosticar Plaga con Gemini", type="primary", use_container_width=True):
        with st.spinner("Buscando modelo disponible y analizando muestra..."):
            
            prompt_mip = f"""
            Actúa como un Entomólogo Senior y Especialista en Manejo Integrado de Plagas (MIP) para la industria alimentaria, específicamente para procesamiento y empaque de café soluble.
            
            Analiza minuciosamente la imagen adjunta. Identifica si corresponde a un insecto o evidencia de plaga de almacén.
            Presta especial atención a los órdenes entomológicos comunes en esta industria:
            - **Coleópteros** (gorgojos, escarabajos de granos/almacén como Sitophilus, Lasioderma, Tribolium, Cryptolestes, Hypothenemus hampei).
            - **Lepidópteros** (polillas de almacén como Plodia interpunctella, Ephestia kuehniella, larvas, sedas/capullos).
            
            Información contextual proporcionada:
            - Área de la planta: {ubicacion}
            - Observaciones del inspector: {notas_adicionales}
            
            Genera un informe técnico estructurado exactamente en los siguientes puntos en formato Markdown:
            
            ### 1. Identificación Entomológica
            - **Especie / Nombre probable:** (Nombre científico y común)
            - **Orden y Familia:**
            - **Nivel de Certeza del Diagnóstico Visual:** [Alto / Medio / Bajo]
            
            ### 2. Evaluación de Riesgo Inocuidad
            - **Nivel de Riesgo:** 🔴 ALTO / 🟡 MEDIO / 🟢 BAJO
            - **Impacto potencial:** (Explicar brevemente si ataca producto final, empaque, materia prima o si es fauna nociva de paso).
            
            ### 3. Protocolo de Acción Inmediata (MIP)
            - **Exclusión y Limpieza:**
            - **Manejo Físico / Químico / Control de Trampas:**
            - **Revisión de Perímetro:**
            
            ### 4. Resumen para la Bitácora de Auditoría (BPM / HACCP)
            Un párrafo conciso redactado formalmente para ser copiado en el reporte diario de calidad.
            """

            try:
                # 1. Obtener la lista de modelos activos en la cuenta del usuario
                modelos_activos = []
                for m in client.models.list():
                    # Filtrar solo modelos que soporten generación de contenido (multimodal)
                    nombre = m.name.replace("models/", "")
                    if "flash" in nombre or "pro" in nombre:
                        modelos_activos.append(nombre)

                # Si por alguna razón la lista falla, dejamos un respaldo manual
                if not modelos_activos:
                    modelos_activos = ["gemini-2.5-flash", "gemini-2.0-flash"]

                exito = False
                error_log = []

                # 2. Intentar la consulta con el primer modelo válido encontrado
                for mod_name in modelos_activos:
                    try:
                        response = client.models.generate_content(
                            model=mod_name,
                            contents=[imagen_input, prompt_mip]
                        )
                        st.success(f"Análisis completado exitosamente (usando modelo: `{mod_name}`)!")
                        st.markdown("---")
                        st.markdown(response.text)
                        exito = True
                        break
                    except Exception as e:
                        error_log.append(f"{mod_name}: {str(e)}")

                if not exito:
                    st.error("No se pudo procesar la solicitud con los modelos disponibles.")
                    st.write("Detalle del error:", error_log)

            except Exception as e_general:
                st.error(f"Error al listar o conectar con los modelos de Gemini: {str(e_general)}")