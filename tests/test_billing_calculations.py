"""
Unit Tests for Billing Calculations and Financial Accounting Rules.
Verifies exact computation of practical package surpluses, DGT exam fees, 21% VAT, and remaining balance.
"""
from decimal import Decimal

import pytest
from src.domain.models import Student, LicensePackage
from src.services.billing_service import BillingService


@pytest.fixture
def sample_package() -> LicensePackage:
    return LicensePackage(
        package_code="PERMIT_B",
        name="Permiso B - Turismo",
        enrollment_fee=Decimal("200.00"),
        included_practical_classes=10,
        extra_class_price=Decimal("30.00"),
        dgt_exam_fee=Decimal("95.00"),
        renewal_fee=Decimal("150.00")
    )


def test_invoice_with_included_classes_no_extras(sample_package: LicensePackage) -> None:
    student = Student(
        dni="11111111H",
        first_name="Laura",
        last_name="Perez",
        completed_classes=8,
        theoretical_exams_count=1,
        practical_exams_count=0,
        total_advances_paid=Decimal("100.00")
    )
    
    invoice = BillingService.generate_invoice(student, sample_package)
    
    assert invoice.extra_classes_count == 0
    assert invoice.extra_classes_cost == Decimal("0.00")
    assert invoice.total_exams_count == 1
    assert invoice.total_exams_cost == Decimal("95.00")
    
    # Subtotal: 200 (matricula) + 0 (extras) + 95 (exam) = 295.0
    assert invoice.subtotal_amount == Decimal("295.00")
    # VAT 21% of 295 = 61.95
    assert invoice.vat_amount == Decimal("61.95")
    # Total with VAT: 356.95
    assert invoice.total_with_vat == Decimal("356.95")
    # Pending: 356.95 - 100 (advance) = 256.95
    assert invoice.pending_balance == Decimal("256.95")


def test_invoice_with_extra_classes(sample_package: LicensePackage) -> None:
    student = Student(
        dni="22222222J",
        first_name="Marco",
        last_name="Asensio",
        completed_classes=15,  # 5 extra classes above 10 included
        theoretical_exams_count=1,
        practical_exams_count=1,  # 2 exams total
        total_advances_paid=Decimal("300.00")
    )

    invoice = BillingService.generate_invoice(student, sample_package)

    assert invoice.extra_classes_count == 5
    assert invoice.extra_classes_cost == Decimal("150.00")  # 5 * 30
    assert invoice.total_exams_count == 2
    assert invoice.total_exams_cost == Decimal("190.00")  # 2 * 95

    # Subtotal: 200 + 150 + 190 = 540.0
    assert invoice.subtotal_amount == Decimal("540.00")
    # VAT 21% of 540 = 113.40
    assert invoice.vat_amount == Decimal("113.40")
    # Total with VAT: 653.40
    assert invoice.total_with_vat == Decimal("653.40")
    # Pending: 653.40 - 300 = 353.40
    assert invoice.pending_balance == Decimal("353.40")
