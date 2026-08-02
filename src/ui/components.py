"""
Reusable Streamlit UI Components and Rendering Helpers.
Implements responsive layouts, interactive tables, Pydantic modal forms, and FPDF download streams with NainDev dark design system.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from pydantic import ValidationError

from src.repository.sqlite_repository import SQLiteRepository
from src.domain.models import Student, Instructor, LicensePackage
from src.services.billing_service import BillingService
from src.services.pdf_service import generate_invoice_pdf_bytes


def render_header() -> None:
    # Inject NainDev Dark Design System styling
    st.markdown(
        """
        <style>
            /* Custom Streamlit KPI Metrics */
            [data-testid="stMetric"] {
                background-color: #0b1220 !important;
                border: 1px solid rgba(37, 99, 235, 0.25) !important;
                border-radius: 12px !important;
                padding: 16px !important;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
                transition: border-color 0.2s ease, transform 0.2s ease;
            }
            [data-testid="stMetric"]:hover {
                border-color: rgba(37, 99, 235, 0.6) !important;
                transform: translateY(-2px);
            }
            [data-testid="stMetricLabel"] p {
                color: #94a3b8 !important;
                font-weight: 500 !important;
                font-size: 0.92rem !important;
                letter-spacing: 0.02em;
            }
            [data-testid="stMetricValue"] div {
                color: #60a5fa !important;
                font-weight: 700 !important;
                font-size: 1.65rem !important;
            }
            /* Custom Tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 6px;
                background-color: #111827;
                padding: 6px;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
            .stTabs [data-baseweb="tab"] {
                height: 42px;
                border-radius: 8px;
                color: #94a3b8;
                font-weight: 500;
                padding: 0 16px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #2563eb !important;
                color: #ffffff !important;
            }
            /* Forms and Containers */
            div[data-testid="stForm"] {
                background-color: #0b1220 !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 12px !important;
                padding: 22px !important;
            }
            /* Top Navigation Bar */
            .nain-top-nav {
                background-color: #111827;
                border: 1px solid rgba(37, 99, 235, 0.2);
                padding: 10px 18px;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                font-size: 0.88rem;
                color: #94a3b8;
            }
            .nain-top-nav a {
                color: #60a5fa !important;
                text-decoration: none !important;
                font-weight: 600;
            }
            .nain-top-nav a:hover {
                text-decoration: underline !important;
            }
            .nain-header-card {
                background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
                border-left: 5px solid #2563eb;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding: 1.6rem;
                border-radius: 10px;
                margin-bottom: 1.5rem;
                box-shadow: 0 6px 16px rgba(0,0,0,0.4);
            }
        </style>
        
        <div class="nain-top-nav">
            <span>Demo Tecnológica Oficial de NainDev</span>
            <a href="https://www.naindev.com/" target="_blank">← Volver al Portafolio NainDev</a>
        </div>
        
        <div class="nain-header-card">
            <h1 style="margin:0; font-size: 2.1rem; font-family: sans-serif; color: #f8fafc; font-weight: 700;">Sistema de Gestión de Autoescuelas - NainDev</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.05rem; color: #94a3b8;">
                Plataforma Web modular construida en <b>Python 3.12 + Clean Architecture + Pydantic v2 + SQLite</b>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_admin(repo: SQLiteRepository) -> None:
    with st.sidebar:
        st.markdown("### Centro de Control Demo")
        st.info("Esta demo técnica funciona de forma autónoma con una base de datos relacional integrada sin coste de infraestructura.")
        
        st.markdown("#### Gestión de Datos Sintéticos")
        st.caption("Puedes experimentar creando, editando y borrando registros libremente. Utiliza este botón para restaurar los datos iniciales.")
        if st.button("Resetear Datos Demo Iniciales", use_container_width=True, type="secondary"):
            repo.reset_database_to_synthetic_defaults()
            st.success("Base de datos reseteada al estado original de prueba.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Especificaciones Técnicas")
        st.markdown(
            """
            - **Arquitectura:** Clean Architecture
            - **Backend:** Python 3.12 (Pydantic v2)
            - **ORM & DB:** SQLAlchemy / SQLite
            - **Reportes:** FPDF2 en memoria (Coste 0)
            - **Frontend:** Streamlit Responsive Dashboard
            """
        )
        st.caption("© 2026 - Proyecto Personal y Escaparate Técnico por Nain9Dev.")


def render_kpi_dashboard(repo: SQLiteRepository) -> None:
    st.subheader("Panel Ejecutivo y Balance Contable")
    students = repo.get_all_students()
    instructors = repo.get_all_instructors()

    total_gross = 0.0
    total_vat = 0.0
    total_pending = 0.0
    completed_lessons_sum = 0

    license_counts: Dict[str, int] = {"Permiso B": 0, "Permiso A2": 0, "Permiso C": 0, "Otros": 0}

    for s in students:
        pkg = repo.get_package_by_code_or_type(s.target_license)
        inv = BillingService.generate_invoice(s, pkg)
        total_gross += inv.subtotal_amount
        total_vat += inv.vat_amount
        total_pending += inv.pending_balance
        completed_lessons_sum += s.completed_classes

        if "A2" in s.target_license.upper():
            license_counts["Permiso A2"] += 1
        elif "C" in s.target_license.upper():
            license_counts["Permiso C"] += 1
        elif "B" in s.target_license.upper():
            license_counts["Permiso B"] += 1
        else:
            license_counts["Otros"] += 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ingresos Brutos Facturables", f"{total_gross:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with col2:
        st.metric("IVA Legal Recaudable (21%)", f"{total_vat:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with col3:
        st.metric("Saldo Pendiente de Cobro", f"{total_pending:,.2f} €".replace(",", "X").replace(".", ",").replace("X", "."))
    with col4:
        st.metric("Total Clases Prácticas", f"{completed_lessons_sum} impartidas")

    st.markdown("---")
    col_chart, col_quick = st.columns([2, 1])
    with col_chart:
        st.markdown("#### Distribución de Alumnos por Tipo de Permiso")
        df_chart = pd.DataFrame(
            {"Tipo de Carnet": list(license_counts.keys()), "Alumnos Activos": list(license_counts.values())}
        )
        st.bar_chart(df_chart, x="Tipo de Carnet", y="Alumnos Activos", color="#2563EB")

    with col_quick:
        st.markdown("#### Resumen Operativo")
        st.write(f"**Total Alumnos Matriculados:** {len(students)}")
        st.write(f"**Instructores en Plantilla:** {len(instructors)}")
        avg_lessons = (completed_lessons_sum / len(students)) if students else 0
        st.write(f"**Promedio Clases por Alumno:** {avg_lessons:.1f}")


def render_students_management(repo: SQLiteRepository) -> None:
    st.subheader("Directorio de Alumnos y Gestión de Clases")
    
    tab_list, tab_add, tab_operate = st.tabs(["Directorio General", "Inscribir Nuevo Alumno", "Registro de Clases y Exámenes"])

    with tab_list:
        students = repo.get_all_students()
        if not students:
            st.warning("No hay alumnos registrados actualmente en la base de datos.")
        else:
            data = [
                {
                    "Expediente": s.registration_number,
                    "DNI / NIF": s.dni,
                    "Nombre Completo": f"{s.first_name} {s.last_name}",
                    "Teléfono": s.phone,
                    "Permiso": s.target_license,
                    "Clases Dadas": s.completed_classes,
                    "Exámenes Teóricos": s.theoretical_exams_count,
                    "Exámenes Prácticos": s.practical_exams_count,
                    "Anticipo Abonado": f"{s.total_advances_paid:.2f} €",
                }
                for s in students
            ]
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_add:
        st.markdown("#### Formulario de Matriculación con Validación Pydantic")
        with st.form("new_student_form"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                input_dni = st.text_input("DNI / NIF (Ej: 12345678X)*", max_chars=12).strip()
                input_first = st.text_input("Nombre*").strip()
                input_last = st.text_input("Apellidos*").strip()
            with col_d2:
                input_phone = st.text_input("Teléfono de Contacto", value="600111222")
                input_license = st.selectbox("Permiso Objetivo", ["B - Turismo", "A2 - Motocicleta", "C - Camión Rígido"])
                input_advance = st.number_input("Anticipo Inicial en €", min_value=0.0, max_value=2000.0, step=10.0, value=100.0)

            submitted = st.form_submit_button("Inscribir Alumno en Base de Datos", use_container_width=True)
            if submitted:
                license_code = "B" if "B" in input_license else ("A2" if "A2" in input_license else "C")
                try:
                    new_student = Student(
                        dni=input_dni,
                        first_name=input_first,
                        last_name=input_last,
                        phone=input_phone,
                        target_license=license_code,
                        total_advances_paid=float(input_advance),
                    )
                    repo.save_student(new_student)
                    st.success(f"Alumno {new_student.first_name} matriculado con éxito (Expediente {new_student.registration_number}).")
                    st.rerun()
                except ValidationError as ve:
                    for error in ve.errors():
                        st.error(f"Error de validación en campo '{error['loc'][0]}': {error['msg']}")

    with tab_operate:
        students = repo.get_all_students()
        if not students:
            st.info("Inscribe alumnos para gestionar sus clases.")
            return

        options_map = {f"{s.dni} - {s.first_name} {s.last_name} ({s.completed_classes} clases)": s.dni for s in students}
        selected_label = st.selectbox("Selecciona Alumno para Registrar Operación:", list(options_map.keys()))
        selected_dni = options_map[selected_label]
        target_student = repo.get_student_by_dni(selected_dni)

        if target_student:
            col_o1, col_o2, col_o3 = st.columns(3)
            with col_o1:
                st.markdown("##### Impartir Clases Prácticas")
                added_classes = st.number_input("Nº de Clases Realizadas", min_value=1, max_value=20, value=2)
                if st.button("Añadir Clases Prácticas", use_container_width=True):
                    target_student.add_classes(int(added_classes))
                    repo.save_student(target_student)
                    st.success(f"Sumadas {added_classes} clases al expediente de {target_student.first_name}.")
                    st.rerun()
            
            with col_o2:
                st.markdown("##### Convocatorias Examen DGT")
                exam_type = st.radio("Tipo de Examen Realizado:", ["Teórico", "Práctico de Circulación"], horizontal=True)
                if st.button("Registrar Convocatoria Examen", use_container_width=True):
                    code = "THEORETICAL" if "Teórico" in exam_type else "PRACTICAL"
                    target_student.register_exam(code)
                    repo.save_student(target_student)
                    st.success(f"Registrada convocatoria de examen {exam_type.lower()} para {target_student.first_name}.")
                    st.rerun()

            with col_o3:
                st.markdown("##### Registrar Nuevo Anticipo / A cuenta")
                extra_pay = st.number_input("Importe Entregado (€)", min_value=10.0, max_value=1000.0, step=20.0, value=50.0)
                if st.button("Añadir Pago a Cuenta", use_container_width=True):
                    target_student.total_advances_paid += round(float(extra_pay), 2)
                    repo.save_student(target_student)
                    st.success(f"Añadido cobro a cuenta de {extra_pay:.2f} €.")
                    st.rerun()


def render_instructors_view(repo: SQLiteRepository) -> None:
    st.subheader("Plantilla de Instructores y Flota de Vehículos")
    instructors = repo.get_all_instructors()
    if not instructors:
        st.warning("No hay instructores registrados.")
        return

    data = [
        {
            "ID Instructor": i.instructor_id,
            "Nombre del Docente": i.full_name,
            "Matrícula Asignada": i.assigned_vehicle_plate,
            "Modelo Vehículo / Categoría": i.vehicle_model,
            "Caducidad ITV": i.itv_expiration_date,
            "Gastos Combustible": f"{i.total_fuel_expenses:.2f} €",
        }
        for i in instructors
    ]
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_billing_and_pdf(repo: SQLiteRepository) -> None:
    st.subheader("Motor de Facturación Oficial y Descarga PDF (1-Clic)")
    st.write("Calcula automáticamente bonos de clases incluidas, importes adicionales, tasas oficiales DGT y aplicación de IVA fiscal de España.")

    students = repo.get_all_students()
    if not students:
        st.info("No hay alumnos en la base de datos para generar facturación.")
        return

    options_map = {f"{s.first_name} {s.last_name} | DNI: {s.dni} | Permiso: {s.target_license}": s.dni for s in students}
    selected_label = st.selectbox("Selecciona Alumno para previsualizar cuenta contable y generar factura:", list(options_map.keys()))
    selected_dni = options_map[selected_label]
    
    student = repo.get_student_by_dni(selected_dni)
    if not student:
        return

    pkg = repo.get_package_by_code_or_type(student.target_license)
    invoice = BillingService.generate_invoice(student, pkg)

    st.markdown("---")
    col_summary, col_action = st.columns([2, 1])
    
    with col_summary:
        st.markdown(f"#### Cuenta de Resultados para **{invoice.student_name}**")
        st.caption(f"Número de Factura de Referencia: `{invoice.invoice_number}` | Fecha: `{invoice.invoice_date}`")
        
        breakdown_df = pd.DataFrame(
            [
                {"Concepto Contable": "Matrícula Curso (Base y Clases Incluidas)", "Unidades / Detalle": f"{invoice.included_classes} clases incluidas", "Importe Bruto": f"{invoice.enrollment_fee:.2f} €"},
                {"Concepto Contable": "Clases Prácticas Extra", "Unidades / Detalle": f"{invoice.extra_classes_count} extra impartidas", "Importe Bruto": f"{invoice.extra_classes_cost:.2f} €"},
                {"Concepto Contable": "Tasas y Tramitaciones de Examen DGT", "Unidades / Detalle": f"{invoice.total_exams_count} convocatoria(s)", "Importe Bruto": f"{invoice.total_exams_cost:.2f} €"},
                {"Concepto Contable": "---", "Unidades / Detalle": "SUBTOTAL BRUTO", "Importe Bruto": f"{invoice.subtotal_amount:.2f} €"},
                {"Concepto Contable": "---", "Unidades / Detalle": "IVA LEGAL (21%)", "Importe Bruto": f"{invoice.vat_amount:.2f} €"},
                {"Concepto Contable": "---", "Unidades / Detalle": "TOTAL CON IMPUESTOS", "Importe Bruto": f"{invoice.total_with_vat:.2f} €"},
                {"Concepto Contable": "---", "Unidades / Detalle": "ANTICIPOS / ABONADOS", "Importe Bruto": f"- {invoice.advances_paid:.2f} €"},
            ]
        )
        st.table(breakdown_df)
        st.markdown(f"### Saldo Pendiente a Pagar: `{invoice.pending_balance:.2f} €`")

    with col_action:
        st.markdown("#### Emisión Documental PDF")
        st.info(
            "El documento se genera en tiempo real y en memoria usando `FPDF2`, protegiendo el almacenamiento y manteniendo el coste en cero."
        )
        
        pdf_bytes = generate_invoice_pdf_bytes(invoice)
        
        st.download_button(
            label="DESCARGAR FACTURA OFICIAL EN PDF",
            data=pdf_bytes,
            file_name=f"Factura_{invoice.student_dni}_{invoice.invoice_number}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
        st.success("Listo para su verificación y presentación ante empresas o clientes.")
