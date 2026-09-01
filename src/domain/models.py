"""
Domain Models for Driving School Management System.
Implements exhaustive validation using Pydantic v2 to ensure type safety and business invariants.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.identity import validate_identity_document
from src.domain.money import MoneyInput, to_money


class LicensePackage(BaseModel):
    """Represents a driving license catalog offer (e.g., Permit B, A2, C) with associated financial policies."""
    package_code: str = Field(..., description="Unique code for the license package, e.g., PERMIT_B")
    name: str = Field(..., description="Human readable commercial name")
    enrollment_fee: Decimal = Field(..., ge=0, description="Initial registration base cost before tax")
    included_practical_classes: int = Field(..., ge=0, description="Number of practical driving lessons included in registration")
    extra_class_price: Decimal = Field(..., ge=0, description="Cost per individual extra driving class")
    dgt_exam_fee: Decimal = Field(..., ge=0, description="Cost for practical or theoretical exam attempt")
    renewal_fee: Decimal = Field(default=Decimal("150.00"), ge=0, description="Cost for document renewal after exhausting exam attempts")

    @field_validator("enrollment_fee", "extra_class_price", "dgt_exam_fee", "renewal_fee", mode="before")
    @classmethod
    def quantise_amount(cls, value: MoneyInput) -> Decimal:
        """Stores every price as a two-place Decimal, whatever the caller passed."""
        return to_money(value)


class AdvancePayment(BaseModel):
    """Represents a monetary payment or deposit made by a student towards their account."""
    payment_id: str = Field(default_factory=lambda: f"PAY-{str(uuid.uuid4())[:8].upper()}")
    student_dni: str
    payment_date: str = Field(default_factory=lambda: datetime.now().strftime("%d-%m-%Y"))
    concept: str = "Acuenta matricula / clases"
    amount: Decimal = Field(..., gt=0, description="Payment amount in EUR")

    @field_validator("amount", mode="before")
    @classmethod
    def quantise_amount(cls, value: MoneyInput) -> Decimal:
        return to_money(value)


class Student(BaseModel):
    """Authoritative student domain model with strict Spanish identity card formatting and progress tracking."""
    registration_number: str = Field(default_factory=lambda: f"EXP-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}")
    dni: str = Field(..., description="Spanish DNI or NIE, checksum verified")
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
    total_advances_paid: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("total_advances_paid", mode="before")
    @classmethod
    def quantise_advances(cls, value: MoneyInput) -> Decimal:
        return to_money(value)

    @field_validator("dni", mode="after")
    @classmethod
    def clean_and_validate_dni(cls, value: str) -> str:
        """Rejects any document whose control letter does not match the checksum.

        Delegating to the domain module keeps a single authoritative implementation:
        the same rule applies to imports, seeds and the interface.
        """
        return validate_identity_document(value)

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
    total_fuel_expenses: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("total_fuel_expenses", mode="before")
    @classmethod
    def quantise_expenses(cls, value: MoneyInput) -> Decimal:
        return to_money(value)

    def register_fuel_expense(self, amount: MoneyInput) -> Decimal:
        expense = to_money(amount)
        if expense <= 0:
            raise ValueError("Fuel expense amount must be greater than zero.")
        self.total_fuel_expenses = to_money(self.total_fuel_expenses + expense)
        return self.total_fuel_expenses


class InvoiceCalculation(BaseModel):
    """Immutable accounting statement summarizing training costs, taxes, and balance reconciliation."""
    invoice_number: str = Field(default_factory=lambda: f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}")
    invoice_date: str = Field(default_factory=lambda: datetime.now().strftime("%d-%m-%Y"))
    student_dni: str
    student_name: str
    target_license: str
    enrollment_fee: Decimal
    included_classes: int
    completed_classes: int
    extra_classes_count: int
    extra_classes_cost: Decimal
    total_exams_count: int
    total_exams_cost: Decimal
    subtotal_amount: Decimal
    vat_percentage: Decimal = Decimal("0.21")
    vat_amount: Decimal
    total_with_vat: Decimal
    advances_paid: Decimal
    pending_balance: Decimal

    @model_validator(mode="after")
    def verify_financial_consistency(self) -> "InvoiceCalculation":
        """Asserts the stated totals reconcile exactly.

        No tolerance. With Decimal arithmetic the parts add up to the total or the
        calculation is wrong; a tolerance would only hide the drift it was masking
        when these amounts were floats.
        """
        expected_subtotal = self.enrollment_fee + self.extra_classes_cost + self.total_exams_cost
        if self.subtotal_amount != expected_subtotal:
            raise ValueError(
                f"Subtotal mismatch: stated {self.subtotal_amount}, parts add to {expected_subtotal}"
            )
        expected_total = self.subtotal_amount + self.vat_amount
        if self.total_with_vat != expected_total:
            raise ValueError(
                f"Total mismatch: stated {self.total_with_vat}, base plus tax is {expected_total}"
            )
        return self
