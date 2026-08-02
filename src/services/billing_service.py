"""
Billing Engine Service.
Authoritative calculation of training packages, practical class extras, DGT examination taxes, and Spanish VAT (IVA 21%).
"""
from src.domain.models import Student, LicensePackage, InvoiceCalculation


class BillingService:
    """Provides pure financial processing decoupling pricing policies from UI rendering."""

    @staticmethod
    def generate_invoice(student: Student, package: LicensePackage) -> InvoiceCalculation:
        """Calculates itemized billing totals for a given student against their target commercial package."""
        extra_classes = max(0, student.completed_classes - package.included_practical_classes)
        extra_classes_cost = round(extra_classes * package.extra_class_price, 2)

        total_exams = student.theoretical_exams_count + student.practical_exams_count
        total_exams_cost = round(total_exams * package.dgt_exam_fee, 2)

        subtotal = round(package.enrollment_fee + extra_classes_cost + total_exams_cost, 2)
        vat_rate = 0.21
        vat_amount = round(subtotal * vat_rate, 2)
        total_with_vat = round(subtotal + vat_amount, 2)
        pending = round(total_with_vat - student.total_advances_paid, 2)

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
            vat_percentage=vat_rate,
            vat_amount=vat_amount,
            total_with_vat=total_with_vat,
            advances_paid=student.total_advances_paid,
            pending_balance=pending,
        )
