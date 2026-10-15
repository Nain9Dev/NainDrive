"""
Main Streamlit Application Entry point for Driving School Management Dashboard.
Enforces Clean Architecture by acting as a dumb renderer consuming backend repository and domain services.
"""
import sys
import os
import streamlit as st

# Ensure root path is accessible when running via `streamlit run src/ui/app.py`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.services.driving_school_service import create_default_service, DrivingSchoolService
from src.ui.components import (
    render_header,
    render_kpi_dashboard,
    render_students_management,
    render_instructors_view,
    render_billing_and_pdf,
    render_sidebar_admin,
)

st.set_page_config(
    page_title="Gestión Autoescuela NainDev | Demo Arquitectura Limpia",
    page_icon="n",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_service() -> DrivingSchoolService:
    """Instantiates a singleton application service for the active Streamlit runtime."""
    return create_default_service(db_url="sqlite:///autoescuela.db")


def main() -> None:
    service = get_service()
    render_sidebar_admin(service)
    render_header()

    tab_dashboard, tab_students, tab_instructors, tab_billing = st.tabs(
        [
            "Dashboard Comercial",
            "Alumnos y Clases",
            "Instructores y Flota",
            "Facturación y Caja PDF",
        ]
    )

    with tab_dashboard:
        render_kpi_dashboard(service)

    with tab_students:
        render_students_management(service)

    with tab_instructors:
        render_instructors_view(service)

    with tab_billing:
        render_billing_and_pdf(service)


if __name__ == "__main__":
    main()

