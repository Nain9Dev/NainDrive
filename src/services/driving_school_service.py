"""Application Service Layer for Driving School Operations.

Encapsulates business orchestration, transaction coordination, and figure preparation,
strictly enforcing ADR-0003 so presentation layers (UI or REST API) never touch persistence directly.
"""
from decimal import Decimal
from typing import Dict, List, Literal, Optional, Tuple

from src.domain.exceptions import StudentNotFoundError
from src.domain.models import (
    DgtExamAppointment,
    Instructor,
    InvoiceCalculation,
    KPIDashboardSummary,
    LicensePackage,
    Student,
)
from src.domain.money import to_money
from src.repository.sqlite_repository import SQLiteRepository
from src.services.billing_service import BillingService
from src.services.pdf_service import generate_invoice_pdf_bytes


class DrivingSchoolService:
    """Authoritative application service for driving school workflows and reporting."""

    def __init__(self, repository: SQLiteRepository):
        self._repo = repository

    def get_kpi_dashboard_summary(self) -> KPIDashboardSummary:
        """Aggregates executive accounting and operational figures without mutating state (REQ-010, REQ-011)."""
        students = self._repo.get_all_students()
        instructors = self._repo.get_all_instructors()

        total_gross = Decimal("0.00")
        total_vat = Decimal("0.00")
        total_pending = Decimal("0.00")
        completed_lessons_sum = 0

        license_counts: Dict[str, int] = {
            "Permiso B": 0,
            "Permiso A2": 0,
            "Permiso C": 0,
            "Otros": 0,
        }

        for s in students:
            pkg = self._repo.get_package_by_code_or_type(s.target_license)
            inv = BillingService.generate_invoice(s, pkg)
            total_gross += inv.subtotal_amount
            total_vat += inv.vat_amount
            total_pending += inv.pending_balance
            completed_lessons_sum += s.completed_classes

            target = s.target_license.upper()
            if "A2" in target:
                license_counts["Permiso A2"] += 1
            elif "C" in target:
                license_counts["Permiso C"] += 1
            elif "B" in target:
                license_counts["Permiso B"] += 1
            else:
                license_counts["Otros"] += 1

        total_students = len(students)
        avg_lessons = (
            round(completed_lessons_sum / total_students, 2)
            if total_students > 0
            else 0.0
        )

        return KPIDashboardSummary(
            total_gross=total_gross,
            total_vat=total_vat,
            total_pending=total_pending,
            completed_lessons_sum=completed_lessons_sum,
            license_distribution=license_counts,
            total_students=total_students,
            total_instructors=len(instructors),
            average_lessons_per_student=avg_lessons,
        )

    def get_all_students(self) -> List[Student]:
        return self._repo.get_all_students()

    def get_student_by_dni(self, dni: str) -> Optional[Student]:
        return self._repo.get_student_by_dni(dni)

    def register_student(self, student: Student) -> Student:
        """Registers a new student, verifying persistence and license package assignment (REQ-001, REQ-002)."""
        return self._repo.save_student(student)

    def delete_student(self, dni: str) -> bool:
        return self._repo.delete_student(dni)

    def add_student_classes(self, dni: str, count: int) -> Student:
        """Records completed practical driving lessons for a student (REQ-003)."""
        student = self._repo.get_student_by_dni(dni)
        if not student:
            raise StudentNotFoundError(f"Student with DNI {dni} not found.")
        student.add_classes(count)
        return self._repo.save_student(student)

    def register_student_exam(
        self, dni: str, exam_type: Literal["THEORETICAL", "PRACTICAL"]
    ) -> Student:
        """Registers an exam attempt against the student profile."""
        student = self._repo.get_student_by_dni(dni)
        if not student:
            raise StudentNotFoundError(f"Student with DNI {dni} not found.")
        student.register_exam(exam_type)
        return self._repo.save_student(student)

    def record_student_advance(self, dni: str, amount: Decimal) -> Student:
        """Records an advance payment from a student towards their account (REQ-006)."""
        deposit = to_money(amount)
        if deposit <= Decimal("0.00"):
            raise ValueError("Advance payment must be strictly positive.")
        student = self._repo.get_student_by_dni(dni)
        if not student:
            raise StudentNotFoundError(f"Student with DNI {dni} not found.")
        student.total_advances_paid = to_money(student.total_advances_paid + deposit)
        return self._repo.save_student(student)

    def get_all_instructors(self) -> List[Instructor]:
        return self._repo.get_all_instructors()

    def register_instructor(self, instructor: Instructor) -> Instructor:
        return self._repo.save_instructor(instructor)

    def record_fuel_expense(self, instructor_id: str, amount: Decimal) -> Instructor:
        """Records a vehicle fuel expense under an instructor."""
        instructors = self._repo.get_all_instructors()
        target = next((i for i in instructors if i.instructor_id == instructor_id), None)
        if not target:
            raise ValueError(f"Instructor with ID {instructor_id} not found.")
        target.register_fuel_expense(amount)
        return self._repo.save_instructor(target)

    def get_all_packages(self) -> List[LicensePackage]:
        return self._repo.get_all_packages()

    def get_package_for_license(self, target_license: str) -> LicensePackage:
        return self._repo.get_package_by_code_or_type(target_license)

    def calculate_student_invoice(self, dni: str) -> InvoiceCalculation:
        """Authoritatively calculates the deterministic billing statement for a student."""
        student = self._repo.get_student_by_dni(dni)
        if not student:
            raise StudentNotFoundError(f"Student with DNI {dni} not found.")
        pkg = self._repo.get_package_by_code_or_type(student.target_license)
        return BillingService.generate_invoice(student, pkg)

    def generate_student_invoice_pdf(self, dni: str) -> Tuple[InvoiceCalculation, bytes]:
        """Generates an in-memory PDF accounting invoice stream without disk writes (REQ-009)."""
        invoice = self.calculate_student_invoice(dni)
        pdf_bytes = generate_invoice_pdf_bytes(invoice)
        return invoice, pdf_bytes

    def schedule_dgt_appointment(
        self,
        dni: str,
        exam_type: Literal["THEORETICAL", "PRACTICAL"],
        appointment_date: str,
        center_location: str = "Centro de Examenes DGT Madrid-Mostoles",
    ) -> DgtExamAppointment:
        """Schedules and persists an official DGT examination appointment (REQ-004)."""
        student = self._repo.get_student_by_dni(dni)
        if not student:
            raise StudentNotFoundError(f"Student with DNI {dni} not found.")
        appointment = DgtExamAppointment(
            student_dni=student.dni,
            exam_type=exam_type,
            appointment_date=appointment_date,
            center_location=center_location,
            status="SCHEDULED",
        )
        return self._repo.save_dgt_appointment(appointment)

    def get_student_dgt_appointments(self, dni: str) -> List[DgtExamAppointment]:
        """Retrieves all scheduled DGT appointments for a student (REQ-004)."""
        return self._repo.get_dgt_appointments_by_student(dni)

    def get_all_dgt_appointments(self) -> List[DgtExamAppointment]:
        return self._repo.get_all_dgt_appointments()

    def reset_demo_data(self) -> None:
        """Restores the database to default fictional demonstration profiles (REQ-012)."""
        self._repo.reset_database_to_synthetic_defaults()


def create_default_service(db_url: str = "sqlite:///autoescuela.db") -> DrivingSchoolService:
    """Convenience factory creating a ready-to-use DrivingSchoolService instance."""
    repo = SQLiteRepository(db_url=db_url, auto_seed=True)
    return DrivingSchoolService(repo)

