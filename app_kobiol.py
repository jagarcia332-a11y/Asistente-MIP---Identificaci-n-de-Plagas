import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Calculadora MIP - K-Obiol EC 25", page_icon="🧪", layout="centered")

st.title("🧪 Calculadora de Mezcla: K-Obiol® EC 25")
st.caption("Herramienta para el cálculo de dosis y generación de reportes de aplicación de plaguicidas.")

# Entradas del usuario
st.header("1. Datos de la Aplicación")
tecnico = st.text_input("Nombre del Técnico que aplica:")

# Lista de plagas extraída de la ficha técnica K-Obiol
plagas_target = st.multiselect(
    "Seleccione la(s) plaga(s) objetivo:",
    [
        "Gorgojos de los cereales (Sitophilus spp.)",
        "Capuchino de los granos (Rhizoperta dominica)",
        "Carcoma grande de los granos (Tenebroides mauritanicus)",
        "Carcoma dentada (Orizaephilus surinamensis)",
        "Tribolios de los cereales (Tribolium spp.)",
        "Gusano de la harina (Tenebrio molitor)",
        "Palomilla de los cereales (Sitotroga cerealella)",
        "Tinea granella",
        "Palomilla mediterránea de la harina (Ephestia kuehniella)",
        "Polilla bandeada (Plodia interpunctella)"
    ]
)

tipo_aplicacion = st.radio(
    "Seleccione el tipo de tratamiento:",
    ("Tratamiento de Superficies (por m²)", "Tratamiento de Granos de Cereales (por Toneladas)")
)

st.header("2. Parámetros del Área / Volumen")

# Variables para los cálculos
dosis_quimico_ml = 0.0
dosis_agua_l = 0.0
total_mezcla_l = 0.0
detalles_dosis = ""
area_m2 = 0.0
toneladas = 0.0

# Lógica según el tipo de aplicación
if tipo_aplicacion == "Tratamiento de Superficies (por m²)":
    st.info("K-Obiol EC 25 se aplica sobre paredes en el momento de la limpieza de locales vacíos antes del almacenaje.")
    
    area_m2 = st.number_input("Ingrese el área a tratar (en metros cuadrados - m²):", min_value=1.0, value=100.0)
    
    tipo_superficie = st.selectbox(
        "Tipo de superficie:",
        ("No porosa (metal, chapa, etc.)", "Porosa (hormigón, cemento, etc.)")
    )
    
    # Rango de dosis: 40 a 60 ml por 100 m2
    nivel_dosis = st.selectbox("Seleccione el nivel de dosis (ml por 100 m²):", (40, 50, 60))
    
    if st.button("Calcular Dosis para Superficie", type="primary"):
        proporcion = area_m2 / 100.0
        dosis_quimico_ml = nivel_dosis * proporcion
        
        # Cálculo de agua y mezcla total según porosidad (5L/100m² para no porosas, 10L/100m² para porosas)
        if "No porosa" in tipo_superficie:
            total_mezcla_l = 5.0 * proporcion
            dosis_agua_l = total_mezcla_l - (dosis_quimico_ml / 1000.0)
        else:
            total_mezcla_l = 10.0 * proporcion
            dosis_agua_l = total_mezcla_l - (dosis_quimico_ml / 1000.0)
            
        detalles_dosis = f"{nivel_dosis} ml de producto por cada 100 m² en superficie {tipo_superficie.lower()}."

elif tipo_aplicacion == "Tratamiento de Granos de Cereales (por Toneladas)":
    st.info("Aplicación directa sobre el cereal diluido en agua (1 a 2 L de producto en 100 L de agua para 100 Tons).")
    
    toneladas = st.number_input("Ingrese el volumen de grano a tratar (en Toneladas):", min_value=1.0, value=100.0)
    
    col1, col2 = st.columns(2)
    with col1:
        zona = st.selectbox("Zona climática:", ("Cálida", "Fría"))
    with col2:
        tiempo_proteccion = st.selectbox("Tiempo de protección deseado:", ("3 meses", "6 meses", "12 meses"))
    
    if st.button("Calcular Dosis para Granos", type="primary"):
        # Lógica de dosis por zona y meses según ficha técnica
        cc_por_ton = 0
        if zona == "Cálida":
            if tiempo_proteccion == "12 meses": cc_por_ton = 20
            elif tiempo_proteccion == "6 meses": cc_por_ton = 15
            elif tiempo_proteccion == "3 meses": cc_por_ton = 10
        elif zona == "Fría":
            if tiempo_proteccion == "12 meses": cc_por_ton = 15
            elif tiempo_proteccion == "6 meses": cc_por_ton = 10
            elif tiempo_proteccion == "3 meses": 
                st.warning("No hay dosis específica para 3 meses en zona fría; aplicando dosis mínima de 10 cc/ton.")
                cc_por_ton = 10
        
        dosis_quimico_ml = cc_por_ton * toneladas
        dosis_agua_l = 1.0 * toneladas  # Proporción estándar: 1 L de agua por tonelada
        total_mezcla_l = dosis_agua_l + (dosis_quimico_ml / 1000.0)
        
        detalles_dosis = f"{cc_por_ton} cc de producto por tonelada (Zona {zona} - Protección {tiempo_proteccion})."

# Generación del Reporte de Aplicación
if dosis_quimico_ml > 0 and tecnico and plagas_target:
    st.markdown("---")
    st.header("3. Reporte de Aplicación")
    
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plagas_str = ", ".join(plagas_target)
    
    reporte_md = f"""
### 📄 BITÁCORA DE CONTROL DE PLAGAS - PREPARACIÓN DE MEZCLA
**Fecha y Hora:** {fecha_hora_actual}
**Técnico Responsable:** {tecnico}
**Producto Utilizado:** K-Obiol® EC 25 (Deltametrina 2.5% p/v)
**Plaga(s) Target:** {plagas_str}

**--- TIPO DE TRATAMIENTO ---**
* **Modalidad:** {tipo_aplicacion}
* **Volumen/Área a tratar:** {area_m2 if 'Superficies' in tipo_aplicacion else toneladas} {'m²' if 'Superficies' in tipo_aplicacion else 'Toneladas'}
* **Concentración Recomendada:** {detalles_dosis}

**--- CANTIDADES PARA LA MEZCLA ---**
* 🧪 **K-Obiol® EC 25 (Químico):** {dosis_quimico_ml:.2f} ml (cc)
* 💧 **Agua a utilizar:** {dosis_agua_l:.2f} Litros
* 🔄 **Volumen Total de Mezcla (Caldo):** {total_mezcla_l:.2f} Litros

**Instrucciones de Seguridad (Bayer):**
* Usar guantes de caucho nitrilo (>0.4 mm), mono estándar y protección respiratoria para vapores (filtro Tipo A conforme EN140).
* Mantener alejado del calor y chispas. Nocivo en caso de ingestión o inhalación. Plazo de reentrada: 24 horas tras ventilación adecuada.
    """
    
    st.success("Cálculo realizado con éxito.")
    st.markdown(reporte_md)
    
    # Botón para descargar el reporte como archivo .txt para compartir
    st.download_button(
        label="📥 Descargar Reporte para Compartir",
        data=reporte_md,
        file_name=f"Reporte_KObiol_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )
elif dosis_quimico_ml > 0:
    st.warning("⚠️ Por favor, ingrese el nombre del técnico y seleccione al menos una plaga objetivo para generar el reporte.")
