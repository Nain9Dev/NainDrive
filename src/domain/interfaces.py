"""Domain repository interfaces and ports for driving school management.

Enforces Dependency Inversion Principle (DIP): Application services depend strictly
on this abstract protocol, completely isolating persistence technologies (SQLite, PostgreSQL, etc.).
"""

from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

from src.domain.models import DgtExamAppointment, Instructor, LicensePackage, Student


@runtime_checkable
class IDrivingSchoolRepository(Protocol):
    """Abstract repository port defining persistence operations for the domain."""

    def get_all_students(self) -> List[Student]:
        """Retrieves all registered students."""
        ...

    def get_student_by_dni(self, dni: str) -> Optional[Student]:
        """Finds a student by their unique national identity document."""
        ...

    def save_student(self, student: Student) -> Student:
        """Persists or updates student state."""
        ...

    def delete_student(self, dni: str) -> bool:
        """Deletes a student record by DNI."""
        ...

    def get_all_instructors(self) -> List[Instructor]:
        """Retrieves all driving school instructors."""
        ...

    def save_instructor(self, instructor: Instructor) -> Instructor:
        """Persists or updates instructor state and fuel expense logs."""
        ...

    def get_all_packages(self) -> List[LicensePackage]:
        """Retrieves all commercial driving license packages."""
        ...

    def get_package_by_code_or_type(self, target_license: str) -> LicensePackage:
        """Finds a commercial offer matching the requested license code or type."""
        ...

    def save_dgt_appointment(self, appointment: DgtExamAppointment) -> DgtExamAppointment:
        """Persists a new or updated DGT examination booking."""
        ...

    def get_dgt_appointments_by_student(self, dni: str) -> List[DgtExamAppointment]:
        """Retrieves exam bookings for a specific student."""
        ...

    def get_all_dgt_appointments(self) -> List[DgtExamAppointment]:
        """Retrieves all scheduled DGT examination bookings across the school."""
        ...

    def reset_database_to_synthetic_defaults(self) -> None:
        """Resets the persistence store to the initial synthetic demonstration state."""
        ...
