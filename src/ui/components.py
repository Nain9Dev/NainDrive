"""Reusable Streamlit UI Components for Driving School Management Dashboard.

Acts strictly as a presentation renderer consuming DrivingSchoolService,
enforcing ADR-0003: zero repository imports and zero financial arithmetic in the UI layer.
"""
from typing import Dict
from decimal import Decimal
import pandas as pd
from pydantic import ValidationError
import streamlit as st

from src.domain.models import Student
from src.services.driving_school_service import DrivingSchoolService


def render_header() -> None:
    st.markdown(
        """
        <style>
            [data-testid="stMetric"] { background-color: #0b1220 !important; border: 1px solid rgba(37,99,235,0.25) !important; border-radius: 12px !important; padding: 14px !important; }
            [data-testid="stMetricLabel"] p { color: #94a3b8 !important; }
            [data-testid="stMetricValue"] div { color: #60a5fa !important; font-weight: 700 !important; }
            .stTabs [data-baseweb="tab-list"] { background-color: #111827; padding: 6px; border-radius: 10px; }
            .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: #fff !important; }
            .nain-header-card { background: linear-gradient(135deg, #0f172a 0%, #111827 100%); border-left: 5px solid #2563eb; padding: 1.4rem; border-radius: 10px; margin-bottom: 1.25rem; }
        </style>
        <div class="nain-header-card">
            <h1 style="margin:0; font-size: 1.9rem; color: #f8fafc; font-weight: 700;">NainDrive — Gestión de Autoescuela</h1>
            <p style="margin: 0.4rem 0 0 0; color: #94a3b8;">Plataforma de gestión y facturación determinista en Python 3.12 + Clean Architecture.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_admin(service: DrivingSchoolService) -> None:
    with st.sidebar:
        st.markdown("### Centro de Control Demo")
        st.info("Base de datos relacional SQLite con perfiles sintéticos y facturación determinista.")
        if st.button("Resetear Datos Demo Iniciales", use_container_width=True, type="secondary"):
            service.reset_demo_data()
            st.success("Base de datos reseteada al estado original.")
            st.rerun()
        st.markdown("---")
        st.caption("© 2026 NainDev · Plataforma Tecnológica NainDrive")


def render_kpi_dashboard(service: DrivingSchoolService) -> None:
    st.subheader("Panel Ejecutivo y Balance Contable")
    kpi = service.get_kpi_dashboard_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ingresos Brutos Facturables", f"{kpi.total_gross:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with col2:
        st.metric("IVA Legal Recaudable (21%)", f"{kpi.total_vat:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with col3:
        st.metric("Saldo Pendiente de Cobro", f"{kpi.total_pending:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with col4:
        st.metric("Total Clases Prácticas", f"{kpi.completed_lessons_sum} impartidas")

    st.markdown("---")
    col_chart, col_quick = st.columns([2, 1])
    with col_chart:
        st.markdown("#### Distribución de Alumnos por Tipo de Permiso")
        df_chart = pd.DataFrame(
            {"Tipo de Carnet": list(kpi.license_distribution.keys()), "Alumnos Activos": list(kpi.license_distribution.values())}
        )
        st.bar_chart(df_chart, x="Tipo de Carnet", y="Alumnos Activos", color="#2563EB")
    with col_quick:
        st.markdown("#### Resumen Operativo")
        st.write(f"**Total Alumnos Matriculados:** {kpi.total_students}")
        st.write(f"**Instructores en Plantilla:** {kpi.total_instructors}")
        st.write(f"**Promedio Clases por Alumno:** {kpi.average_lessons_per_student:.1f}")


def render_students_management(service: DrivingSchoolService) -> None:
    st.subheader("Directorio de Alumnos y Gestión de Clases")
    tab_list, tab_add, tab_operate = st.tabs(["Directorio General", "Inscribir Nuevo Alumno", "Registro de Clases y Exámenes"])

    with tab_list:
        students = service.get_all_students()
        if not students:
            st.warning("No hay alumnos registrados.")
            return
        data = [
            {"Expediente": s.registration_number, "DNI": s.dni, "Nombre": f"{s.first_name} {s.last_name}", "Teléfono": s.phone, "Permiso": s.target_license, "Clases": s.completed_classes, "Teóricos": s.theoretical_exams_count, "Prácticos": s.practical_exams_count, "Anticipo": f"{s.total_advances_paid:.2f} €"}
            for s in students
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with tab_add:
        st.markdown("#### Formulario de Matriculación")
        with st.form("new_student_form"):
            c1, c2 = st.columns(2)
            with c1:
                input_dni = st.text_input("DNI / NIE (Ej: 12345678Z)*", max_chars=12).strip()
                input_first = st.text_input("Nombre*").strip()
                input_last = st.text_input("Apellidos*").strip()
            with c2:
                input_phone = st.text_input("Teléfono", value="600111222")
                input_license = st.selectbox("Permiso Objetivo", ["B - Turismo", "A2 - Motocicleta", "C - Camión"])
                input_advance = st.number_input("Anticipo Inicial en €", min_value=0.0, max_value=2000.0, step=10.0, value=100.0)
            if st.form_submit_button("Inscribir Alumno", use_container_width=True):
                code = "B" if "B" in input_license else ("A2" if "A2" in input_license else "C")
                try:
                    s = Student(dni=input_dni, first_name=input_first, last_name=input_last, phone=input_phone, target_license=code, total_advances_paid=Decimal(str(input_advance)))
                    service.register_student(s)
                    st.success(f"Alumno {s.first_name} matriculado correctamente.")
                    st.rerun()
                except ValidationError as ve:
                    for err in ve.errors():
                        st.error(f"Error en '{err['loc'][0]}': {err['msg']}")

    with tab_operate:
        students = service.get_all_students()
        if not students:
            st.info("Inscribe alumnos primero.")
            return
        options = {f"{s.dni} - {s.first_name} {s.last_name}": s.dni for s in students}
        sel_label = st.selectbox("Selecciona Alumno:", list(options.keys()))
        dni = options[sel_label]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("##### Impartir Clases")
            cls_count = st.number_input("Nº Clases", min_value=1, max_value=20, value=2)
            if st.button("Añadir Clases", use_container_width=True):
                service.add_student_classes(dni, int(cls_count))
                st.success("Clases añadidas.")
                st.rerun()
        with c2:
            st.markdown("##### Exámenes DGT")
            ex_type = st.radio("Tipo:", ["Teórico", "Práctico"], horizontal=True)
            if st.button("Registrar Convocatoria", use_container_width=True):
                service.register_student_exam(dni, "THEORETICAL" if ex_type == "Teórico" else "PRACTICAL")
                st.success("Convocatoria registrada.")
                st.rerun()
        with c3:
            st.markdown("##### Pago a Cuenta")
            pay = st.number_input("Importe (€)", min_value=10.0, max_value=1000.0, step=20.0, value=50.0)
            if st.button("Añadir Pago", use_container_width=True):
                service.record_student_advance(dni, Decimal(str(pay)))
                st.success("Anticipo registrado.")
                st.rerun()


def render_instructors_view(service: DrivingSchoolService) -> None:
    st.subheader("Plantilla de Instructores y Flota de Vehículos")
    instructors = service.get_all_instructors()
    if not instructors:
        st.warning("No hay instructores.")
        return
    data = [
        {"ID": i.instructor_id, "Nombre": i.full_name, "Matrícula": i.assigned_vehicle_plate, "Vehículo": i.vehicle_model, "ITV": i.itv_expiration_date, "Combustible": f"{i.total_fuel_expenses:.2f} €"}
        for i in instructors
    ]
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)


def render_billing_and_pdf(service: DrivingSchoolService) -> None:
    st.subheader("Motor de Facturación Oficial y Descarga PDF (1-Clic)")
    students = service.get_all_students()
    if not students:
        st.info("No hay alumnos para facturar.")
        return
    options = {f"{s.first_name} {s.last_name} | DNI: {s.dni}": s.dni for s in students}
    sel_label = st.selectbox("Selecciona Alumno para Factura:", list(options.keys()))
    dni = options[sel_label]
    invoice, pdf_bytes = service.generate_student_invoice_pdf(dni)

    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"#### Factura: **{invoice.student_name}** (`{invoice.invoice_number}`)")
        table_data = [
            {"Concepto": "Matrícula", "Detalle": f"{invoice.included_classes} clases", "Importe": f"{invoice.enrollment_fee:.2f} €"},
            {"Concepto": "Clases Extra", "Detalle": f"{invoice.extra_classes_count} extra", "Importe": f"{invoice.extra_classes_cost:.2f} €"},
            {"Concepto": "Tasas DGT", "Detalle": f"{invoice.total_exams_count} exámenes", "Importe": f"{invoice.total_exams_cost:.2f} €"},
            {"Concepto": "SUBTOTAL BRUTO", "Detalle": "Base imponible", "Importe": f"{invoice.subtotal_amount:.2f} €"},
            {"Concepto": "IVA (21%)", "Detalle": "Impuesto legal", "Importe": f"{invoice.vat_amount:.2f} €"},
            {"Concepto": "TOTAL CON IVA", "Detalle": "Total devengado", "Importe": f"{invoice.total_with_vat:.2f} €"},
            {"Concepto": "ANTICIPOS", "Detalle": "Abonos previos", "Importe": f"- {invoice.advances_paid:.2f} €"},
        ]
        st.table(pd.DataFrame(table_data))
        st.markdown(f"### Saldo Pendiente: `{invoice.pending_balance:.2f} €`")
    with c2:
        st.markdown("#### Descarga Documento PDF")
        st.download_button(
            label="DESCARGAR FACTURA EN PDF",
            data=pdf_bytes,
            file_name=f"Factura_{invoice.student_dni}_{invoice.invoice_number}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
