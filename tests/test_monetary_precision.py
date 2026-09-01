"""Monetary precision tests.

Spanish invoicing rounds half away from zero. Python's built-in `round` rounds half to
even, and binary floating point cannot represent most decimal amounts exactly, so the
two disagree on the boundary. On a single line the difference is one cent; across an
invoice it accumulates and the stated total stops matching the sum of its parts.

These tests pin the boundary cases that a float implementation gets wrong.
"""
from decimal import Decimal

import pytest

from src.domain.models import LicensePackage, Student
from src.services.billing_service import BillingService


@pytest.fixture
def half_cent_package() -> LicensePackage:
    """Chosen so the tax lands exactly on a half-cent boundary.

    Enrollment 200.50 plus five extra lessons at 30.00 gives a taxable base of 350.50.
    21 percent of 350.50 is 73.605 exactly: the case where rounding mode decides the
    result.
    """
    return LicensePackage(
        package_code="PERMIT_B",
        name="Permiso B - Turismo",
        enrollment_fee=Decimal("200.50"),
        included_practical_classes=10,
        extra_class_price=Decimal("30.00"),
        dgt_exam_fee=Decimal("95.00"),
    )


def test_tax_on_half_cent_boundary_rounds_up(half_cent_package: LicensePackage) -> None:
    """73.605 must become 73.61, not 73.60."""
    student = Student(
        dni="12345678Z",
        first_name="Laura",
        last_name="Perez",
        completed_classes=15,
    )

    invoice = BillingService.generate_invoice(student, half_cent_package)

    assert invoice.subtotal_amount == Decimal("350.50")
    assert invoice.vat_amount == Decimal("73.61")
    assert invoice.total_with_vat == Decimal("424.11")


def test_total_equals_sum_of_its_parts(half_cent_package: LicensePackage) -> None:
    """The stated total must reconcile exactly, with no tolerance."""
    student = Student(
        dni="87654321X",
        first_name="Marco",
        last_name="Asensio",
        completed_classes=23,
        theoretical_exams_count=2,
        practical_exams_count=1,
    )

    invoice = BillingService.generate_invoice(student, half_cent_package)

    parts = (
        invoice.enrollment_fee
        + invoice.extra_classes_cost
        + invoice.total_exams_cost
    )
    assert invoice.subtotal_amount == parts
    assert invoice.total_with_vat == invoice.subtotal_amount + invoice.vat_amount


def test_amounts_are_decimal_not_float(half_cent_package: LicensePackage) -> None:
    """A float amount anywhere in the chain reintroduces the drift."""
    student = Student(dni="11111111H", first_name="Ana", last_name="Pastor", completed_classes=12)

    invoice = BillingService.generate_invoice(student, half_cent_package)

    for field in (
        "enrollment_fee",
        "extra_classes_cost",
        "total_exams_cost",
        "subtotal_amount",
        "vat_amount",
        "total_with_vat",
        "advances_paid",
        "pending_balance",
    ):
        value = getattr(invoice, field)
        assert isinstance(value, Decimal), f"{field} is {type(value).__name__}, expected Decimal"


def test_amounts_are_quantised_to_two_places(half_cent_package: LicensePackage) -> None:
    """No amount may carry more than two decimal places once stored."""
    student = Student(
        dni="22222222J",
        first_name="Sara",
        last_name="Gomez",
        completed_classes=17,
        total_advances_paid=Decimal("99.99"),
    )

    invoice = BillingService.generate_invoice(student, half_cent_package)

    for field in ("subtotal_amount", "vat_amount", "total_with_vat", "pending_balance"):
        value = getattr(invoice, field)
        assert -value.as_tuple().exponent <= 2, f"{field} carries more than two decimals"


def test_advance_larger_than_total_yields_negative_balance(
    half_cent_package: LicensePackage,
) -> None:
    """An overpayment is a credit, not a clamped zero. Silently clamping would hide
    money owed back to the student."""
    student = Student(
        dni="33333333P",
        first_name="Luis",
        last_name="Ramos",
        completed_classes=10,
        total_advances_paid=Decimal("500.00"),
    )

    invoice = BillingService.generate_invoice(student, half_cent_package)

    assert invoice.pending_balance < Decimal("0")
