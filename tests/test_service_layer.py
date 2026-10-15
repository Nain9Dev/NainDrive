"""Service Layer Tests for DrivingSchoolService.

Tests cover:
- REQ-010: Dashboard financial and operational figure preparation (T-001, T-002)
- REQ-011: Dashboard calculations are strictly read-only
- REQ-009: In-memory PDF invoice generation produces byte streams with zero disk writes (T-014)
- REQ-004: DGT exam appointment scheduling and retrieval (T-015)
"""
import os
from decimal import Decimal
import pytest

from src.repository.sqlite_repository import SQLiteRepository
from src.services.driving_school_service import DrivingSchoolService
from src.domain.models import Student, DgtExamAppointment


@pytest.fixture
def service(tmp_path) -> DrivingSchoolService:
    db_file = tmp_path / "test_service.db"
    repo = SQLiteRepository(db_url=f"sqlite:///{db_file}", auto_seed=True)
    return DrivingSchoolService(repo)


def test_kpi_dashboard_summary_calculation(service: DrivingSchoolService):
    """REQ-010: Calculates projected gross, VAT, outstanding balance, and license distribution."""
    summary = service.get_kpi_dashboard_summary()

    assert summary.total_students == 4
    assert summary.total_instructors == 3
    assert summary.completed_lessons_sum == (14 + 5 + 12 + 3)
    assert summary.total_gross > Decimal("0.00")
    assert summary.total_vat > Decimal("0.00")
    assert summary.total_pending > Decimal("0.00")

    # License distribution mapping
    assert summary.license_distribution["Permiso B"] == 2  # Alvaro & Sofia
    assert summary.license_distribution["Permiso A2"] == 1  # Lucia
    assert summary.license_distribution["Permiso C"] == 1  # David


def test_kpi_dashboard_is_read_only(service: DrivingSchoolService):
    """REQ-011: Dashboard calculation does not alter persisted database records."""
    students_before = service.get_all_students()
    instructors_before = service.get_all_instructors()

    # Call summary multiple times
    _ = service.get_kpi_dashboard_summary()
    _ = service.get_kpi_dashboard_summary()

    students_after = service.get_all_students()
    instructors_after = service.get_all_instructors()

    assert len(students_before) == len(students_after)
    assert [s.completed_classes for s in students_before] == [s.completed_classes for s in students_after]
    assert len(instructors_before) == len(instructors_after)


def test_in_memory_pdf_generation_returns_bytes_without_disk_writes(service: DrivingSchoolService, monkeypatch):
    """REQ-009 / T-014: Produces valid PDF bytes in memory and writes nothing to the filesystem."""
    files_created = []

    original_open = open

    def tracking_open(file, *args, **kwargs):
        # Allow reading font/system files, but track any file writes
        mode = args[0] if len(args) > 0 else kwargs.get("mode", "r")
        if "w" in mode or "a" in mode or "x" in mode:
            files_created.append(str(file))
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", tracking_open)

    invoice, pdf_bytes = service.generate_student_invoice_pdf("53822281G")

    assert invoice.student_dni == "53822281G"
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500  # Valid PDF binary length
    assert pdf_bytes.startswith(b"%PDF")  # Standard PDF magic header
    assert len(files_created) == 0, f"Unexpected disk writes during PDF generation: {files_created}"


def test_dgt_exam_appointment_storage_and_retrieval(service: DrivingSchoolService):
    """REQ-004 / T-015: Schedules and retrieves DGT exam appointments against a student."""
    dni = "11223344B"  # Lucia Jimenez

    appointment = service.schedule_dgt_appointment(
        dni=dni,
        exam_type="PRACTICAL",
        appointment_date="18-12-2026",
        center_location="Centro de Examenes DGT Alcala",
    )

    assert appointment.student_dni == dni
    assert appointment.exam_type == "PRACTICAL"
    assert appointment.appointment_date == "18-12-2026"
    assert appointment.status == "SCHEDULED"

    # Retrieve from repository via service
    appointments = service.get_student_dgt_appointments(dni)
    matching = [a for a in appointments if a.appointment_id == appointment.appointment_id]
    assert len(matching) == 1
    assert matching[0].center_location == "Centro de Examenes DGT Alcala"


def test_student_lifecycle_actions_via_service(service: DrivingSchoolService):
    """Verifies lesson increments and advance payments through application service."""
    dni = "78901234X"  # Sofia Alvarez (starts with 3 classes, 100 EUR advance)

    updated = service.add_student_classes(dni, 5)
    assert updated.completed_classes == 8

    updated = service.record_student_advance(dni, Decimal("150.00"))
    assert updated.total_advances_paid == Decimal("250.00")

    updated = service.register_student_exam(dni, "THEORETICAL")
    assert updated.theoretical_exams_count == 1
