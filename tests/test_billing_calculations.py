"""
Unit Tests for Billing Calculations and Financial Accounting Rules.
Verifies exact computation of practical package surpluses, DGT exam fees, 21% VAT, and remaining balance.
"""
import pytest
from src.domain.models import Student, LicensePackage
from src.services.billing_service import BillingService


@pytest.fixture
def sample_package() -> LicensePackage:
    return LicensePackage(
        package_code="PERMIT_B",
        name="Permiso B - Turismo",
        enrollment_fee=200.0,
        included_practical_classes=10,
        extra_class_price=30.0,
        dgt_exam_fee=95.0,
        renewal_fee=150.0
    )


def test_invoice_with_included_classes_no_extras(sample_package: LicensePackage) -> None:
    student = Student(
        dni="11111111A",
        first_name="Laura",
        last_name="Perez",
        completed_classes=8,
        theoretical_exams_count=1,
        practical_exams_count=0,
        total_advances_paid=100.0
    )
    
    invoice = BillingService.generate_invoice(student, sample_package)
    
    assert invoice.extra_classes_count == 0
    assert invoice.extra_classes_cost == 0.0
    assert invoice.total_exams_count == 1
    assert invoice.total_exams_cost == 95.0
    
    # Subtotal: 200 (matricula) + 0 (extras) + 95 (exam) = 295.0
    assert invoice.subtotal_amount == 295.0
    # VAT 21% of 295 = 61.95
    assert invoice.vat_amount == 61.95
    # Total with VAT: 356.95
    assert invoice.total_with_vat == 356.95
    # Pending: 356.95 - 100 (advance) = 256.95
    assert invoice.pending_balance == 256.95


def test_invoice_with_extra_classes(sample_package: LicensePackage) -> None:
    student = Student(
        dni="22222222B",
        first_name="Marco",
        last_name="Asensio",
        completed_classes=15,  # 5 extra classes above 10 included
        theoretical_exams_count=1,
        practical_exams_count=1,  # 2 exams total
        total_advances_paid=300.0
    )

    invoice = BillingService.generate_invoice(student, sample_package)

    assert invoice.extra_classes_count == 5
    assert invoice.extra_classes_cost == 150.0  # 5 * 30
    assert invoice.total_exams_count == 2
    assert invoice.total_exams_cost == 190.0  # 2 * 95

    # Subtotal: 200 + 150 + 190 = 540.0
    assert invoice.subtotal_amount == 540.0
    # VAT 21% of 540 = 113.40
    assert invoice.vat_amount == 113.4
    # Total with VAT: 653.40
    assert invoice.total_with_vat == 653.4
    # Pending: 653.40 - 300 = 353.40
    assert invoice.pending_balance == 353.4
