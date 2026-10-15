"""Integration tests for FastAPI REST Gateway endpoints."""
from decimal import Decimal
import pytest
from starlette.testclient import TestClient

from src.api.main import app, get_service
from src.repository.sqlite_repository import SQLiteRepository
from src.services.driving_school_service import DrivingSchoolService


@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "api_test.db"
    repo = SQLiteRepository(db_url=f"sqlite:///{test_db}", auto_seed=True)
    service = DrivingSchoolService(repo)

    app.dependency_overrides[get_service] = lambda: service
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client: TestClient):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "NainDrive API Gateway"
    assert data["status"] == "Healthy"


def test_dashboard_kpis(client: TestClient):
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total_students"] == 4
    assert Decimal(str(data["total_gross"])) > 0
    assert "Permiso B" in data["license_distribution"]


def test_students_crud_and_validation(client: TestClient):
    # List students
    res = client.get("/api/v1/students")
    assert res.status_code == 200
    assert len(res.json()) == 4

    # Get single student
    res = client.get("/api/v1/students/53822281G")
    assert res.status_code == 200
    assert res.json()["first_name"] == "Alvaro"

    # Reject invalid DNI checksum
    bad_student = {
        "dni": "12345678A",  # Invalid checksum
        "first_name": "Test",
        "last_name": "User",
        "target_license": "B",
    }
    res = client.post("/api/v1/students", json=bad_student)
    assert res.status_code == 422

    # Accept valid DNI checksum
    good_student = {
        "dni": "12345678Z",  # Valid checksum
        "first_name": "Valentin",
        "last_name": "Gomez",
        "target_license": "B",
        "total_advances_paid": 120.0,
    }
    res = client.post("/api/v1/students", json=good_student)
    assert res.status_code == 201
    assert res.json()["dni"] == "12345678Z"


def test_student_operations(client: TestClient):
    dni = "53822281G"

    # Add classes
    res = client.post(f"/api/v1/students/{dni}/classes", json={"count": 3})
    assert res.status_code == 200
    assert res.json()["completed_classes"] == 17

    # Record advance
    res = client.post(f"/api/v1/students/{dni}/advances", json={"amount": 75.50})
    assert res.status_code == 200
    assert Decimal(str(res.json()["total_advances_paid"])) == Decimal("325.50")


def test_invoice_calculation_and_pdf(client: TestClient):
    dni = "53822281G"

    # Get invoice
    res = client.get(f"/api/v1/students/{dni}/invoice")
    assert res.status_code == 200
    inv = res.json()
    assert inv["student_dni"] == dni
    assert Decimal(str(inv["subtotal_amount"])) > 0
    assert Decimal(str(inv["vat_amount"])) > 0
    assert Decimal(str(inv["total_with_vat"])) == Decimal(str(inv["subtotal_amount"])) + Decimal(str(inv["vat_amount"]))

    # Download PDF
    res = client.get(f"/api/v1/students/{dni}/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")


def test_dgt_appointments_endpoints(client: TestClient):
    dni = "11223344B"

    # Schedule appointment
    appointment_data = {
        "exam_type": "THEORETICAL",
        "appointment_date": "29-12-2026",
        "center_location": "Centro de Examenes DGT Madrid-Mostoles",
    }
    res = client.post(f"/api/v1/students/{dni}/dgt/appointments", json=appointment_data)
    assert res.status_code == 201
    assert res.json()["appointment_date"] == "29-12-2026"

    # List appointments for student
    res = client.get(f"/api/v1/students/{dni}/dgt/appointments")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_scalar_docs_html(client: TestClient):
    res = client.get("/docs")
    assert res.status_code == 200
    assert "api-reference" in res.text
