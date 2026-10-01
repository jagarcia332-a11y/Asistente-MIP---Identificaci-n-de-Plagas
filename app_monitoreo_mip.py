import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configuración de la página
st.set_page_config(page_title="Tablero MIP - Monitoreo de Trampas", page_icon="🪰", layout="wide")

st.title("🪰 Tablero de Monitoreo MIP y Análisis de Riesgo")
st.caption("Seguimiento de trampas UV, estaciones de roedores y placas adhesivas para toma de decisiones químicas.")

# --- SIMULACIÓN Y ESTRUCTURA DE DATOS ---
if 'historial_inspecciones' not in st.session_state:
    # Datos de prueba para ilustrar tendencias y riesgos
    fechas = [datetime.now().date() - timedelta(days=i*7) for i in range(4)]
    fechas.reverse()
    
    data_demo = [
        # Semana 1 a 4
        {"Fecha": fechas[0], "Anillo": "Anillo 1 (Perímetro Exterior)", "Área": "Perímetro Barda Sur", "Tipo": "Roedores (Cebo/Impacto)", "ID": "TR-01", "Capturas/Consumo": 10, "Tipo Plaga": "Ratas"},
        {"Fecha": fechas[0], "Anillo": "Anillo 3 (Área Crítica)", "Área": "Almacén Cacao/Materia Prima", "Tipo": "Trampa UV", "ID": "UV-01", "Capturas/Consumo": 2, "Tipo Plaga": "Polillas"},
        {"Fecha": fechas[1], "Anillo": "Anillo 1 (Perímetro Exterior)", "Área": "Perímetro Barda Sur", "Tipo": "Roedores (Cebo/Impacto)", "ID": "TR-01", "Capturas/Consumo": 25, "Tipo Plaga": "Ratas"},
        {"Fecha": fechas[1], "Anillo": "Anillo 3 (Área Crítica)", "Área": "Almacén Cacao/Materia Prima", "Tipo": "Trampa UV", "ID": "UV-01", "Capturas/Consumo": 8, "Tipo Plaga": "Polillas"},
        {"Fecha": fechas[2], "Anillo": "Anillo 2 (Accesos/Muelles)", "Área": "Muelle de Recepción 2", "Tipo": "Trampa UV", "ID": "UV-02", "Capturas/Consumo": 18, "Tipo Plaga": "Moscas"},
        {"Fecha": fechas[3], "Anillo": "Anillo 3 (Área Crítica)", "Área": "Zona de Empaque", "Tipo": "Rastreros (Adhesiva)", "ID": "PA-01", "Capturas/Consumo": 5, "Tipo Plaga": "Cucarachas"},
        {"Fecha": fechas[3], "Anillo": "Anillo 3 (Área Crítica)", "Área": "Almacén Cacao/Materia Prima", "Tipo": "Trampa UV", "ID": "UV-01", "Capturas/Consumo": 15, "Tipo Plaga": "Polillas"},
    ]
    st.session_state.historial_inspecciones = pd.DataFrame(data_demo)

# --- PESTAÑAS DE LA APLICACIÓN ---
tab1, tab2, tab3 = st.tabs(["📝 Registrar Inspección", "📊 Análisis de Tendencias y Riesgo", "📄 Generar Reporte PDF"])

# ---------------------------------------------------------
# TAB 1: REGISTRO DE INSPECCIÓN
# ---------------------------------------------------------
with tab1:
    st.header("Ingreso de Monitoreo en Campo")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_insp = st.date_input("Fecha de Inspección:", datetime.now().date())
        tecnico = st.text_input("Técnico / Inspector Responsable:", "Juan Pérez")
        anillo = st.selectbox(
            "Anillo de Seguridad / Ubicación:",
            ("Anillo 1 (Perímetro Exterior)", "Anillo 2 (Accesos/Muelles)", "Anillo 3 (Área Crítica / Proceso / Almacén)")
        )
        area = st.text_input("Nombre del Área o Sector:", "Almacén General")
        
    with col2:
        tipo_dispositivo = st.selectbox(
            "Tipo de Dispositivo / Trampa:",
            ("Trampa UV (Voladores)", "Roedores (Cebo / Mecánica)", "Placa Adhesiva (Rastreros)")
        )
        id_trampa = st.text_input("Identificador de Trampa (ID):", "UV-03")
        
        plaga_detectada = st.selectbox(
            "Plaga Principal Detectada:",
            ("Moscas", "Mosquitos", "Polillas", "Ratas", "Ratones", "Cucarachas", "Escarabajos de Almacén", "Ninguna")
        )
        
        if "Roedores" in tipo_dispositivo:
            conteo = st.number_input("Consumo de Cebo (%) o Capturas Físicas:", min_value=0, max_value=100, value=10)
        else:
            conteo = st.number_input("Cantidad de Insectos Atrapados (Conteo):", min_value=0, value=5)

    if st.button("💾 Guardar Inspección", type="primary"):
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha_insp,
            "Anillo": anillo,
            "Área": area,
            "Tipo": tipo_dispositivo,
            "ID": id_trampa,
            "Capturas/Consumo": conteo,
            "Tipo Plaga": plaga_detectada
        }])
        st.session_state.historial_inspecciones = pd.concat([st.session_state.historial_inspecciones, nuevo_registro], ignore_index=True)
        st.success(f"Registro para la trampa {id_trampa} guardado correctamente.")

# ---------------------------------------------------------
# TAB 2: ANÁLISIS DE TENDENCIAS Y MATRIZ DE DECISIÓN
# ---------------------------------------------------------
with tab2:
    st.header("Análisis de Tendencias y Evaluación de Aplicación Química")
    
    df = st.session_state.historial_inspecciones.copy()
    
    if not df.empty:
        # Filtros de búsqueda
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_anillo = st.multiselect("Filtrar por Anillo:", df["Anillo"].unique(), default=df["Anillo"].unique())
        with col_f2:
            filtro_tipo = st.multiselect("Filtrar por Tipo de Trampa:", df["Tipo"].unique(), default=df["Tipo"].unique())
            
        df_filtrado = df[(df["Anillo"].isin(filtro_anillo)) & (df["Tipo"].isin(filtro_tipo))]
        
        # 1. Gráfica de Tendencia
        st.subheader("📈 Tendencia de Capturas / Actividad por Fecha")
        df_tendencia = df_filtrado.groupby(["Fecha", "Tipo Plaga"])["Capturas/Consumo"].sum().reset_index()
        
        if not df_tendencia.empty:
            st.line_chart(df_tendencia, x="Fecha", y="Capturas/Consumo", color="Tipo Plaga")
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados.")
            
        st.markdown("---")
        
        # 2. Matriz de Decisiones MIP (Aplicación Química vs Medidas Físicas)
        st.subheader("🤖 Matriz de Toma de Decisiones y Diagnóstico de Riesgo")
        
        # Agrupación por Área para evaluar riesgo
        riesgo_area = df_filtrado.groupby(["Área", "Anillo", "Tipo Plaga"])["Capturas/Consumo"].sum().reset_index()
        
        def evaluar_accion(row):
            capturas = row["Capturas/Consumo"]
            anillo = row["Anillo"]
            plaga = row["Tipo Plaga"]
            
            # Criterios MIP
            if "Área Crítica" in anillo:
                if capturas > 10:
                    return "🔴 RIESGO ALTO: Requiere Inspección Inmediata y Aplicación Química Focalizada / Aspersión Localizada."
                elif capturas > 3:
                    return "🟡 RIESGO MODERADO: Reforzar Limpieza, Revisar Hermetización y Mantenimiento de Trampa."
                else:
                    return "🟢 BAJO RIESGO: Mantener Control Preventivo."
            elif "Accesos" in anillo:
                if capturas > 15:
                    return "🔴 RIESGO ALTO: Evaluar Nebulización / Aplicación de Barrera Química Externa."
                else:
                    return "🟢 BAJO RIESGO: Revisar Cortinas de Aire y Sellado de Puertas."
            else: # Perímetro Exterior
                if capturas > 30:
                    return "🟡 ATENCIÓN EXTERNA: Incrementar Frecuencia de Reposición de Cebos / Trampas de Pista."
                else:
                    return "🟢 CONTROL PERIMETRAL ADECUADO: Monitoreo Normal."

        riesgo_area["Recomendación MIP"] = riesgo_area.apply(evaluar_accion, axis=1)
        
        st.dataframe(riesgo_area, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: GENERACIÓN DE REPORTE PDF
# ---------------------------------------------------------
with tab3:
    st.header("Exportación de Diagnóstico MIP")
    st.write("Genera una bitácora formal con la matriz de decisión para respaldar auditorías de calidad (GFSI, BPM, HACCP).")
    
    if st.button("📄 Generar Informe PDF de Monitoreo", type="primary"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, textColor=colors.HexColor('#1A365D'), alignment=1)
        sub_style = ParagraphStyle('SubTitle', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#2B6CB0'))
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=8.5, leading=11)

        story.append(Paragraph("<b>REPORTE DE DIAGNÓSTICO MIP Y TOMA DE DECISIONES</b>", title_style))
        story.append(Spacer(1, 10))
        
        data_pdf = [["Área", "Anillo", "Plaga", "Conteo Total", "Diagnóstico / Acción Requerida"]]
        for _, r in riesgo_area.iterrows():
            data_pdf.append([
                Paragraph(str(r["Área"]), body_style),
                Paragraph(str(r["Anillo"]), body_style),
                Paragraph(str(r["Tipo Plaga"]), body_style),
                Paragraph(str(r["Capturas/Consumo"]), body_style),
                Paragraph(str(r["Recomendación MIP"]), body_style)
            ])
            
        t = Table(data_pdf, colWidths=[90, 100, 70, 60, 210])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        doc.build(story)
        buffer.seek(0)
        
        st.download_button(
            label="📥 Descargar Diagnóstico en PDF",
            data=buffer,
            file_name=f"Reporte_MIP_Riesgo_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
