import streamlit as st
import math
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configuración de la página
st.set_page_config(
    page_title="Calculadora Fumigación Detia Gas (Fosfina)", 
    page_icon="💨", 
    layout="centered"
)

st.title("💨 Calculadora de Dosificación: Detia® Gas (Fosfina)")
st.caption("Fumigante a base de Fosfuro de Aluminio (57%) para granos, almacenes, silos y contenedores.")

# Función para generar el PDF técnico
def generar_pdf(tecnico, instalacion, tipo_estructura, vol_m3, plagas_str, acaros, dosis_por_m3, total_tabletas, tiempo_exposicion, tiempo_ventilacion, fecha_hora):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Estilos de ReportLab
    style_title = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=8)
    style_subtitle = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#2B6CB0'), spaceBefore=8, spaceAfter=6)
    style_body = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#2D3748'))
    style_alert = ParagraphStyle('AlertStyle', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#C53030'))

    # Encabezado
    story.append(Paragraph("<b>CONTROL DE CALIDAD E INOCUIDAD - CONTROL DE PLAGAS</b>", style_title))
    story.append(Paragraph("<b>ORDEN DE APLICACIÓN Y FUMIGACIÓN CON FOSFINA (Detia® Gas)</b>", style_subtitle))
    story.append(Spacer(1, 8))

    # Datos del Servicio
    data_gen = [
        [Paragraph("<b>Fecha y Hora:</b>", style_body), Paragraph(fecha_hora, style_body)],
        [Paragraph("<b>Técnico Certificado:</b>", style_body), Paragraph(tecnico, style_body)],
        [Paragraph("<b>Instalación / Ubicación:</b>", style_body), Paragraph(instalacion, style_body)],
        [Paragraph("<b>Producto / Ingrediente:</b>", style_body), Paragraph("Detia® Gas (Fosfuro de Aluminio 57% p/p)", style_body)],
        [Paragraph("<b>Categoría Toxicológica:</b>", style_body), Paragraph("<b>Categoría I - Extremadamente Tóxico</b>", style_body)],
        [Paragraph("<b>Plaga Objetivo:</b>", style_body), Paragraph(f"{plagas_str} {'(Incluye Ácaros +50% Dosis)' if acaros else ''}", style_body)]
    ]
    t_gen = Table(data_gen, colWidths=[150, 380])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_gen)
    story.append(Spacer(1, 10))

    # Geometría y CÁLCULO
    story.append(Paragraph("<b>1. Parámetros Cúbicos y Dosificación</b>", style_subtitle))
    data_calc = [
        [Paragraph("<b>Estructura Evaluada</b>", style_body), Paragraph(tipo_estructura, style_body)],
        [Paragraph("<b>Volumen Cúbico Calculado (m³)</b>", style_body), Paragraph(f"<b>{vol_m3:.2f} m³</b>", style_body)],
        [Paragraph("<b>Dosis Aplicada por m³</b>", style_body), Paragraph(f"{dosis_por_m3} tabletas/m³", style_body)],
        [Paragraph("<b>TOTAL TABLETAS REQUERIDAS</b>", style_body), Paragraph(f"<b>{total_tabletas} tabletas</b> (~{math.ceil(total_tabletas*3)} g de producto)", style_body)],
        [Paragraph("<b>Tiempo Mínimo de Exposición</b>", style_body), Paragraph(f"<b>{tiempo_exposicion}</b>", style_body)],
        [Paragraph("<b>Tiempo Mínimo de Ventilación</b>", style_body), Paragraph(tiempo_ventilacion, style_body)],
    ]
    t_calc = Table(data_calc, colWidths=[200, 330])
    t_calc.setStyle(TableStyle([
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#EBF8FF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#A0AEC0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_calc)
    story.append(Spacer(1, 10))

    # Protocolo de Seguridad
    story.append(Paragraph("<b>2. Protocolo Obligatorio de Seguridad y Hermetización (Ficha ANASAC)</b>", style_subtitle))
    seguridad_text = """
    • <b>Hermetización:</b> Asegurar sellado total con carpa/lona impermeable al gas o verificar cierre de válvulas en silos.<br/>
    • <b>EPP Requerido:</b> Máscara de rostro completo (Full Face) con filtro para fosfina (Tipo B, Clase 2 para gases inorgánicos). Guantes secos.<br/>
    • <b>Corrosión:</b> El gas reacciona con cobre, oro y plata. Proteger motores y paneles eléctricos.<br/>
    • <b>Desgasificación y Reingreso:</b> Ventilar según el rango establecido. No reingresar si la concentración es > 0.1 ppm.<br/>
    • <b>Disposición de Residuos:</b> Las cenizas del polvo de fosfuro de aluminio deben inactivarse según normativa local.
    """
    story.append(Paragraph(seguridad_text, style_alert))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- INTERFAZ STREAMLIT ---
st.header("1. Información General del Tratamiento")
col_a, col_b = st.columns(2)
with col_a:
    tecnico = st.text_input("Técnico Certificado Responsable:")
with col_b:
    instalacion = st.text_input("Instalación / Nombre del Cliente:")

plagas_target = st.multiselect(
    "Seleccione la(s) plaga(s) objetivo:",
    [
        "Capuchino de los granos (Rhyzopertha dominica)",
        "Gorgojo de los cereales (Sitophilus spp.)",
        "Gorgojo oxidado / Gorgojo plano (Cryptolestes ferrugineus)",
        "Tribolio de la harina (Tribolium spp.)",
        "Palomilla de los cereales (Sitotroga cerealella)",
        "Polillas de almacén (Ephestia / Plodia)",
        "Insectos de productos procesados (Tabaco, Cacao, Especias)"
    ]
)

acaros = st.checkbox("¿Se identificó presencia de Ácaros en el muestreo? (Incrementa dosis en 50% según Ficha Técnica)")

st.header("2. Selección de Estructura y Cálculo de Volumen (m³)")

tipo_est = st.selectbox(
    "Seleccione el tipo de recinto a fumigar:",
    (
        "Contenedor Marítimo (Estándar 20ft / 40ft)",
        "Silo Cilíndrico (Cono / Cilindro)",
        "Pila o Estiba Encarpada (Caja Rectangular)",
        "Local Vacío / Bodega"
    )
)

volumen_m3 = 0.0

if tipo_est == "Contenedor Marítimo (Estándar 20ft / 40ft)":
    tamano_cont = st.radio("Tamaño del Contenedor:", ("20 Pies (Aprox. 33 m³)", "40 Pies (Aprox. 67 m³)", "40 Pies High Cube (Aprox. 76 m³)", "Medida Personalizada"))
    if "20 Pies" in tamano_cont:
        volumen_m3 = 33.0
    elif "40 Pies High Cube" in tamano_cont:
        volumen_m3 = 76.0
    elif "40 Pies" in tamano_cont:
        volumen_m3 = 67.0
    else:
        largo = st.number_input("Largo (m):", min_value=0.1, value=6.0)
        ancho = st.number_input("Ancho (m):", min_value=0.1, value=2.4)
        alto = st.number_input("Alto (m):", min_value=0.1, value=2.4)
        volumen_m3 = largo * ancho * alto

elif tipo_est == "Silo Cilíndrico (Cono / Cilindro)":
    st.info("Cálculo geométrico del volumen del silo (Cilindro principal + Cono superior/inferior).")
    radio = st.number_input("Radio del Silo (m):", min_value=0.1, value=3.0)
    altura_cilindro = st.number_input("Altura de la sección cilíndrica (m):", min_value=0.1, value=8.0)
    altura_cono = st.number_input("Altura promedio del cono/tolva (m):", min_value=0.0, value=2.0)
    
    vol_cilindro = math.pi * (radio ** 2) * altura_cilindro
    vol_cono = (1.0/3.0) * math.pi * (radio ** 2) * altura_cono
    volumen_m3 = vol_cilindro + vol_cono

elif tipo_est == "Pila o Estiba Encarpada (Caja Rectangular)":
    st.info("Mida el espacio total cubierto por la carpa plástica hermética.")
    largo = st.number_input("Largo de la carpa (m):", min_value=0.1, value=5.0)
    ancho = st.number_input("Ancho de la carpa (m):", min_value=0.1, value=3.0)
    alto = st.number_input("Alto de la carpa (m):", min_value=0.1, value=2.5)
    volumen_m3 = largo * ancho * alto

elif tipo_est == "Local Vacío / Bodega":
    largo = st.number_input("Largo del local (m):", min_value=0.1, value=20.0)
    ancho = st.number_input("Ancho del local (m):", min_value=0.1, value=10.0)
    alto = st.number_input("Alto promedio (m):", min_value=0.1, value=4.0)
    volumen_m3 = largo * ancho * alto

st.metric("📦 Volumen Cúbico Total a Fumigar", f"{volumen_m3:.2f} m³")

# Parámetros Técnicos
dosis_tabletas_m3 = 0
tiempo_exp = ""
tiempo_vent = ""

if "Contenedor" in tipo_est or "Pila" in tipo_est:
    dosis_base = st.slider("Dosis recomendada (Tabletas / m³):", min_value=2, max_value=5, value=3)
    dosis_tabletas_m3 = dosis_base
    tiempo_exp = "3 a 5 días (5 a 7 días para Rhyzopertha o Cryptolestes)"
    tiempo_vent = "6 a 72 horas"

elif "Silo" in tipo_est:
    dosis_base = st.slider("Dosis recomendada para granos a granel (Tabletas / m³):", min_value=3, max_value=5, value=4)
    dosis_tabletas_m3 = dosis_base
    tiempo_exp = "Mínimo 3 días (5 a 7 días para especies resistentes/Rhyzopertha)"
    tiempo_vent = "24 horas"

elif "Local Vacío" in tipo_est:
    dosis_base = st.slider("Dosis recomendada para locales vacíos (Tabletas / m³):", min_value=1, max_value=2, value=2)
    dosis_tabletas_m3 = dosis_base
    tiempo_exp = "2 a 5 días"
    tiempo_vent = "6 a 24 horas"

# Ajuste por ácaros (+50%)
if acaros:
    dosis_tabletas_m3 = dosis_tabletas_m3 * 1.5
    tiempo_exp += " | (Aumentado a 5 - 10 días por presencia de ácaros)"

# Cálculo Final
total_tabletas = math.ceil(volumen_m3 * dosis_tabletas_m3)

# Botón para procesar y generar reporte
if st.button("🧮 Calcular y Generar Reporte PDF", type="primary"):
    if not tecnico or not instalacion or not plagas_target:
        st.error("⚠️ Complete el nombre del técnico, la instalación y seleccione al menos una plaga objetivo.")
    else:
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plagas_str = ", ".join(plagas_target)
        
        pdf_bytes = generar_pdf(
            tecnico, instalacion, tipo_est, volumen_m3, plagas_str, acaros,
            dosis_tabletas_m3, total_tabletas, tiempo_exp, tiempo_vent, fecha_hora_actual
        )
        
        st.markdown("---")
        st.success("✅ ¡Cálculo de Fosfina completado!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💊 Total Tabletas Detia Gas", f"{total_tabletas} tab")
        with col2:
            st.metric("⏳ Dosis por m³", f"{dosis_tabletas_m3} tab/m³")
        with col3:
            st.metric("⏱️ Tiempo Mínimo Exposición", tiempo_exp.split('|')[0])
            
        st.download_button(
            label="📄 Descargar Orden de Fumigación en PDF",
            data=pdf_bytes,
            file_name=f"Orden_Fumigacion_Fosfina_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
