import streamlit as st
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configuración de la página
st.set_page_config(page_title="Calculadora MIP - K-Obiol EC 25", page_icon="🧪", layout="centered")

st.title("🧪 Calculadora de Mezcla: K-Obiol® EC 25")
st.caption("Herramienta para el cálculo de dosis y generación de reportes PDF de aplicación de plaguicidas.")

# Función para generar el PDF usando ReportLab
def generar_pdf(tecnico, plagas_str, tipo_aplicacion, parametro_cant, detalles_dosis, dosis_quimico_ml, dosis_agua_l, total_mezcla_l, fecha_hora):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    style_title = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1A365D'), alignment=1, spaceAfter=12)
    style_subtitle = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2B6CB0'), spaceBefore=8, spaceAfter=6)
    style_body = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#2D3748'))
    style_alert = ParagraphStyle('AlertStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#C53030'))

    # Encabezado
    story.append(Paragraph("<b>CAFÉ SOLUBLE - CONTROL DE CALIDAD E INOCUIDAD</b>", style_title))
    story.append(Paragraph("<b>BITÁCORA DE PREPARACIÓN DE MEZCLA Y APLICACIÓN DE PLAGUICIDA</b>", style_subtitle))
    story.append(Spacer(1, 10))

    # Tabla de Datos Generales
    data_gen = [
        [Paragraph("<b>Fecha y Hora:</b>", style_body), Paragraph(fecha_hora, style_body)],
        [Paragraph("<b>Técnico Responsable:</b>", style_body), Paragraph(tecnico, style_body)],
        [Paragraph("<b>Producto Utilizado:</b>", style_body), Paragraph("K-Obiol® EC 25 (Deltametrina 2.5% p/v)", style_body)],
        [Paragraph("<b>Plaga(s) Target:</b>", style_body), Paragraph(plagas_str, style_body)],
    ]
    t_gen = Table(data_gen, colWidths=[150, 380])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_gen)
    story.append(Spacer(1, 12))

    # Tabla de Parámetros del Tratamiento
    story.append(Paragraph("<b>1. Parámetros del Tratamiento</b>", style_subtitle))
    data_trat = [
        [Paragraph("<b>Modalidad de Aplicación:</b>", style_body), Paragraph(tipo_aplicacion, style_body)],
        [Paragraph("<b>Área / Volumen Tratar:</b>", style_body), Paragraph(parametro_cant, style_body)],
        [Paragraph("<b>Dosificación / Concentración:</b>", style_body), Paragraph(detalles_dosis, style_body)],
    ]
    t_trat = Table(data_trat, colWidths=[150, 380])
    t_trat.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_trat)
    story.append(Spacer(1, 12))

    # Tabla de Cantidades a Mezclar (Resaltada)
    story.append(Paragraph("<b>2. Cantidades Calculadas para la Mezcla</b>", style_subtitle))
    data_calc = [
        [Paragraph("<b>Componente</b>", style_body), Paragraph("<b>Cantidad Necesaria</b>", style_body)],
        [Paragraph("K-Obiol® EC 25 (Concentrado Químico)", style_body), Paragraph(f"<b>{dosis_quimico_ml:.2f} ml (cc)</b>", style_body)],
        [Paragraph("Agua (Diluyente)", style_body), Paragraph(f"<b>{dosis_agua_l:.2f} Litros</b>", style_body)],
        [Paragraph("<b>Volumen Total de Mezcla (Caldo)</b>", style_body), Paragraph(f"<b>{total_mezcla_l:.2f} Litros</b>", style_body)],
    ]
    t_calc = Table(data_calc, colWidths=[280, 250])
    t_calc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#EBF8FF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#A0AEC0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_calc)
    story.append(Spacer(1, 15))

    # Advertencias de Seguridad (EPI / Ficha Técnica Bayer)
    story.append(Paragraph("<b>3. Instrucciones de Seguridad y EPP Obligatorio</b>", style_subtitle))
    seguridad_text = """
    • <b>Equipo de Protección Personal:</b> Utilizar guantes de caucho nitrilo (>0.4 mm), mono de protección categoría 3 tipo 6, gafas herméticas (EN166) y protección respiratoria con filtro tipo A para vapores orgánicos (EN140).<br/>
    • <b>Precauciones:</b> Producto inflamable y tóxico para organismos acuáticos. Evitar contacto con piel/ojos e inhalación de vapores.<br/>
    • <b>Plazo de Reentrada:</b> 24 horas tras ventilación adecuada del recinto tratado.
    """
    story.append(Paragraph(seguridad_text, style_alert))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Entradas del usuario
st.header("1. Datos de la Aplicación")
tecnico = st.text_input("Nombre del Técnico que aplica:")

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

dosis_quimico_ml = 0.0
dosis_agua_l = 0.0
total_mezcla_l = 0.0
detalles_dosis = ""
parametro_cant = ""

if tipo_aplicacion == "Tratamiento de Superficies (por m²)":
    st.info("K-Obiol EC 25 se aplica sobre paredes en la limpieza de locales vacíos antes del almacenaje.")
    area_m2 = st.number_input("Ingrese el área a tratar (en metros cuadrados - m²):", min_value=1.0, value=100.0)
    tipo_superficie = st.selectbox("Tipo de superficie:", ("No porosa (metal, chapa, etc.)", "Porosa (hormigón, cemento, etc.)"))
    nivel_dosis = st.selectbox("Seleccione el nivel de dosis (ml por 100 m²):", (40, 50, 60))
    
    if st.button("Calcular Dosis para Superficie", type="primary"):
        proporcion = area_m2 / 100.0
        dosis_quimico_ml = nivel_dosis * proporcion
        if "No porosa" in tipo_superficie:
            total_mezcla_l = 5.0 * proporcion
            dosis_agua_l = total_mezcla_l - (dosis_quimico_ml / 1000.0)
        else:
            total_mezcla_l = 10.0 * proporcion
            dosis_agua_l = total_mezcla_l - (dosis_quimico_ml / 1000.0)
            
        detalles_dosis = f"{nivel_dosis} ml de producto por cada 100 m² en superficie {tipo_superficie.lower()}."
        parametro_cant = f"{area_m2:.2f} m²"

elif tipo_aplicacion == "Tratamiento de Granos de Cereales (por Toneladas)":
    st.info("Aplicación directa sobre el cereal diluido en agua (1 a 2 L de producto en 100 L de agua para 100 Tons).")
    toneladas = st.number_input("Ingrese el volumen de grano a tratar (en Toneladas):", min_value=1.0, value=100.0)
    
    col1, col2 = st.columns(2)
    with col1:
        zona = st.selectbox("Zona climática:", ("Cálida", "Fría"))
    with col2:
        tiempo_proteccion = st.selectbox("Tiempo de protección deseado:", ("3 meses", "6 meses", "12 meses"))
    
    if st.button("Calcular Dosis para Granos", type="primary"):
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
        dosis_agua_l = 1.0 * toneladas
        total_mezcla_l = dosis_agua_l + (dosis_quimico_ml / 1000.0)
        detalles_dosis = f"{cc_por_ton} cc de producto por tonelada (Zona {zona} - Protección {tiempo_proteccion})."
        parametro_cant = f"{toneladas:.2f} Toneladas"

# Generación del Reporte PDF
if dosis_quimico_ml > 0 and tecnico and plagas_target:
    st.markdown("---")
    st.header("3. Reporte Generado")
    
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plagas_str = ", ".join(plagas_target)
    
    # Generar el archivo PDF en memoria
    pdf_bytes = generar_pdf(
        tecnico, plagas_str, tipo_aplicacion, parametro_cant, 
        detalles_dosis, dosis_quimico_ml, dosis_agua_l, total_mezcla_l, fecha_hora_actual
    )
    
    st.success("¡Cálculo realizado exitosamente! El informe formal en PDF está listo para descargar.")
    
    # Vista previa rápida en la interfaz
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("🧪 K-Obiol® EC 25", f"{dosis_quimico_ml:.2f} ml")
    with col_b:
        st.metric("💧 Agua requerida", f"{dosis_agua_l:.2f} L")
    
    # Botón de Descarga directa en PDF
    st.download_button(
        label="📄 Descargar Reporte en PDF",
        data=pdf_bytes,
        file_name=f"Reporte_KObiol_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
elif dosis_quimico_ml > 0:
    st.warning("⚠️ Por favor, ingrese el nombre del técnico y seleccione al menos una plaga objetivo para generar el reporte.")
