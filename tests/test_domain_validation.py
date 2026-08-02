"""
Unit Tests for Domain Model Validations and Invariants.
Verifies rejection of invalid identity codes, empty names, and negative financial values.
"""
import pytest
from pydantic import ValidationError
from src.domain.models import Student, LicensePackage, Instructor, AdvancePayment


def test_valid_student_creation() -> None:
    student = Student(
        dni="12345678A",
        first_name="Carlos",
        last_name="Alcaraz",
        phone="611223344",
        target_license="B"
    )
    assert student.dni == "12345678A"
    assert student.completed_classes == 0


def test_invalid_dni_format_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(
            dni="NO_VALIDO_MAS_LARGO",
            first_name="John",
            last_name="Doe",
        )


def test_empty_student_name_raises_error() -> None:
    with pytest.raises(ValidationError):
        Student(
            dni="12345678B",
            first_name="   ",
            last_name="Gomez"
        )


def test_license_package_negative_fees_rejected() -> None:
    with pytest.raises(ValidationError):
        LicensePackage(
            package_code="INVALID_B",
            name="Permiso Erroneo",
            enrollment_fee=-50.0,
            included_practical_classes=10,
            extra_class_price=30.0,
            dgt_exam_fee=90.0
        )


def test_add_classes_domain_action() -> None:
    student = Student(dni="87654321Z", first_name="Ana", last_name="Pastor")
    total = student.add_classes(5)
    assert total == 5
    assert student.completed_classes == 5

    with pytest.raises(ValueError):
        student.add_classes(-2)


def test_advance_payment_strictly_positive() -> None:
    with pytest.raises(ValidationError):
        AdvancePayment(student_dni="12345678A", amount=0.0)
