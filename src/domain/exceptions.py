"""
Domain exceptions for Driving School management system.
Defines custom error types to maintain explicit error handling across the Clean Architecture boundaries.
"""


class DrivingSchoolDomainException(Exception):
    """Base exception class for all domain-related errors in the driving school platform."""

    pass


class StudentNotFoundError(DrivingSchoolDomainException):
    """Raised when an operation is requested for a student ID or DNI that does not exist in the repository."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Student with identifier '{identifier}' was not found.")
        self.identifier = identifier


class InstructorNotFoundError(DrivingSchoolDomainException):
    """Raised when an instructor is not found in the persistent store."""

    def __init__(self, identifier: str) -> None:
        super().__init__(
            f"Instructor with identifier '{identifier}' was not found."
        )
        self.identifier = identifier


class InvalidIdentityCardError(DrivingSchoolDomainException):
    """Raised when an identity card number (DNI/NIF/NIE) fails domain validation rules."""

    def __init__(self, dni: str, reason: str) -> None:
        super().__init__(f"Invalid ID format for '{dni}': {reason}")
        self.dni = dni
        self.reason = reason


class NegativeFinancialAmountError(DrivingSchoolDomainException):
    """Raised when a calculation or input attempts to assign a negative monetary value to an invoice or payment."""

    def __init__(self, field: str, amount: float) -> None:
        super().__init__(
            f"Monetary amount for '{field}' cannot be negative. Got: {amount:.2f}€"
        )
        self.field = field
        self.amount = amount


class DuplicateEntityError(DrivingSchoolDomainException):
    """Raised when attempting to register a student or instructor with an identity card that already exists."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        super().__init__(
            f"An entity of type '{entity_type}' with ID '{identifier}' already exists."
        )
        self.entity_type = entity_type
        self.identifier = identifier
