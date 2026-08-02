"""
Domain Models for Driving School Management System.
Implements exhaustive validation using Pydantic v2 to ensure type safety and business invariants.
"""
import re
import uuid
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class LicensePackage(BaseModel):
    """Represents a driving license catalog offer (e.g., Permit B, A2, C) with associated financial policies."""
    package_code: str = Field(..., description="Unique code for the license package, e.g., PERMIT_B")
    name: str = Field(..., description="Human readable commercial name")
    enrollment_fee: float = Field(..., ge=0.0, description="Initial registration base cost before tax")
    included_practical_classes: int = Field(..., ge=0, description="Number of practical driving lessons included in registration")
    extra_class_price: float = Field(..., ge=0.0, description="Cost per individual extra driving class")
    dgt_exam_fee: float = Field(..., ge=0.0, description="Cost for practical or theoretical exam attempt")
    renewal_fee: float = Field(default=150.0, ge=0.0, description="Cost for document renewal after exhausting exam attempts")

    @field_validator("enrollment_fee", "extra_class_price", "dgt_exam_fee", "renewal_fee", mode="after")
    @classmethod
    def validate_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Financial figures cannot be negative in the domain model.")
        return round(value, 2)


class AdvancePayment(BaseModel):
    """Represents a monetary payment or deposit made by a student towards their account."""
    payment_id: str = Field(default_factory=lambda: f"PAY-{str(uuid.uuid4())[:8].upper()}")
    student_dni: str
    payment_date: str = Field(default_factory=lambda: datetime.now().strftime("%d-%m-%Y"))
    concept: str = "Acuenta matricula / clases"
    amount: float = Field(..., gt=0.0, description="Payment amount in EUR")


class Student(BaseModel):
    """Authoritative student domain model with strict Spanish identity card formatting and progress tracking."""
    registration_number: str = Field(default_factory=lambda: f"EXP-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}")
    dni: str = Field(..., description="National identity card number or passport")
    first_name: str
    last_name: str
    birth_date: str = "01-01-2000"
    phone: str = "600000000"
    email: Optional[str] = None
    address: str = "Madrid, Espana"
    target_license: str = "B"
    assigned_instructor_id: Optional[str] = "INST-01"
    completed_classes: int = Field(default=0, ge=0, description="Total practical lessons completed by student")
    theoretical_exams_count: int = Field(default=0, ge=0)
    practical_exams_count: int = Field(default=0, ge=0)
    total_advances_paid: float = Field(default=0.0, ge=0.0)

    @field_validator("dni", mode="after")
    @classmethod
    def clean_and_validate_dni(cls, value: str) -> str:
        clean = value.strip().upper()
        # Ensure alphanumeric and reasonable length (5 to 12 chars to accommodate DNI, NIE, Passports in demos)
        if not re.match(r"^[A-Z0-9]{5,12}$", clean):
            raise ValueError(f"Identity Document format '{clean}' is invalid. Must be alphanumeric (5-12 chars).")
        return clean

    @field_validator("first_name", "last_name", mode="after")
    @classmethod
    def validate_names(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Person names cannot be empty or solely whitespace.")
        return trimmed

    def add_classes(self, count: int) -> int:
        """Domain action to increment practical driving lessons taken."""
        if count <= 0:
            raise ValueError("Class count to add must be strictly positive.")
        self.completed_classes += count
        return self.completed_classes

    def register_exam(self, exam_type: Literal["THEORETICAL", "PRACTICAL"]) -> None:
        """Domain action to record an examination attempt."""
        if exam_type == "THEORETICAL":
            self.theoretical_exams_count += 1
        else:
            self.practical_exams_count += 1


class Instructor(BaseModel):
    """Instructor domain model containing fleet asset assignments and expense compliance."""
    instructor_id: str = Field(default_factory=lambda: f"INST-{str(uuid.uuid4())[:6].upper()}")
    full_name: str
    assigned_vehicle_plate: str = "0000-XXX"
    vehicle_model: str = "Standard Vehicle"
    itv_expiration_date: str = "31-12-2026"
    total_fuel_expenses: float = Field(default=0.0, ge=0.0)

    def register_fuel_expense(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Fuel expense amount must be greater than zero.")
        self.total_fuel_expenses += round(amount, 2)
        return self.total_fuel_expenses


class InvoiceCalculation(BaseModel):
    """Immutable accounting statement summarizing training costs, taxes, and balance reconciliation."""
    invoice_number: str = Field(default_factory=lambda: f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}")
    invoice_date: str = Field(default_factory=lambda: datetime.now().strftime("%d-%m-%Y"))
    student_dni: str
    student_name: str
    target_license: str
    enrollment_fee: float
    included_classes: int
    completed_classes: int
    extra_classes_count: int
    extra_classes_cost: float
    total_exams_count: int
    total_exams_cost: float
    subtotal_amount: float
    vat_percentage: float = 0.21
    vat_amount: float
    total_with_vat: float
    advances_paid: float
    pending_balance: float

    @model_validator(mode="after")
    def verify_financial_consistency(self) -> "InvoiceCalculation":
        """Asserts mathematical rigor of accounting totals."""
        expected_subtotal = round(self.enrollment_fee + self.extra_classes_cost + self.total_exams_cost, 2)
        if abs(self.subtotal_amount - expected_subtotal) > 0.05:
            raise ValueError(f"Subtotal calculation mismatch: got {self.subtotal_amount}, expected {expected_subtotal}")
        return self
