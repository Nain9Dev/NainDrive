"""Billing engine.

Authoritative calculation of enrollment, extra practical lessons, DGT examination fees
and Spanish `IVA` (value-added tax). Every amount is a Decimal quantised once, at the
point it is produced, so the stated total always equals the sum of its parts.
"""
from decimal import Decimal

from src.domain.models import Student, LicensePackage, InvoiceCalculation
from src.domain.money import apply_rate, multiply, to_money

# Spanish standard `IVA` rate. Driving school tuition may qualify for a different rate
# depending on the licence type; see docs/11-open-questions.md Q-001.
STANDARD_VAT_RATE = Decimal("0.21")


class BillingService:
    """Pure financial processing, decoupled from persistence and rendering."""

    @staticmethod
    def generate_invoice(student: Student, package: LicensePackage) -> InvoiceCalculation:
        """Calculates the itemised invoice for a student against their package."""
        extra_classes = max(0, student.completed_classes - package.included_practical_classes)
        extra_classes_cost = multiply(package.extra_class_price, extra_classes)

        total_exams = student.theoretical_exams_count + student.practical_exams_count
        total_exams_cost = multiply(package.dgt_exam_fee, total_exams)

        subtotal = to_money(package.enrollment_fee + extra_classes_cost + total_exams_cost)
        vat_amount = apply_rate(subtotal, STANDARD_VAT_RATE)
        total_with_vat = to_money(subtotal + vat_amount)

        # An overpayment yields a negative balance: money owed back to the student.
        # Clamping it to zero would silently lose a refund.
        pending = to_money(total_with_vat - student.total_advances_paid)

        return InvoiceCalculation(
            student_dni=student.dni,
            student_name=f"{student.first_name} {student.last_name}",
            target_license=package.name,
            enrollment_fee=package.enrollment_fee,
            included_classes=package.included_practical_classes,
            completed_classes=student.completed_classes,
            extra_classes_count=extra_classes,
            extra_classes_cost=extra_classes_cost,
            total_exams_count=total_exams,
            total_exams_cost=total_exams_cost,
            subtotal_amount=subtotal,
            vat_percentage=STANDARD_VAT_RATE,
            vat_amount=vat_amount,
            total_with_vat=total_with_vat,
            advances_paid=student.total_advances_paid,
            pending_balance=pending,
        )
