"""FastAPI REST API Gateway for NainDrive Driving School Operations.

Provides decoupled HTTP endpoints for executive reporting, student records,
deterministic financial calculations, in-memory PDF generation, and DGT exam scheduling.
"""
from decimal import Decimal
from typing import List, Literal, Optional
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.domain.exceptions import StudentNotFoundError
from src.domain.models import (
    DgtExamAppointment,
    Instructor,
    InvoiceCalculation,
    KPIDashboardSummary,
    LicensePackage,
    Student,
)
from src.services.driving_school_service import (
    DrivingSchoolService,
    create_default_service,
)

app = FastAPI(
    title="NainDrive — Driving School Management API Gateway",
    version="1.0.0",
    description=(
        "REST API for deterministic driving school accounting, student lifecycle management, "
        "and in-memory official PDF billing generation. Built on Python 3.12 and Clean Architecture."
    ),
    docs_url=None,  # We serve Scalar at /docs
    redoc_url=None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5379",
        "http://127.0.0.1:5379",
        "https://drive.naindev.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8150",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection helper
def get_service() -> DrivingSchoolService:
    return create_default_service()


# Request DTOs
class AddClassesRequest(BaseModel):
    count: int = Field(..., gt=0, description="Number of practical lessons to add")


class RegisterExamRequest(BaseModel):
    exam_type: Literal["THEORETICAL", "PRACTICAL"] = Field(..., description="Type of DGT examination")


class RecordAdvanceRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Advance payment amount in EUR")


class ScheduleDgtAppointmentRequest(BaseModel):
    exam_type: Literal["THEORETICAL", "PRACTICAL"]
    appointment_date: str = Field(..., description="Date of the exam, e.g. 15-12-2026")
    center_location: str = Field(default="Centro de Examenes DGT Madrid-Mostoles")


class RecordFuelRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Fuel expense in EUR")


# Endpoints

@app.get("/api/v1/health", tags=["Diagnostics"])
def get_health_status():
    """Health check endpoint reporting API and persistence state."""
    return {
        "service": "NainDrive API Gateway",
        "version": "1.0.0",
        "architecture": "Clean Architecture",
        "status": "Healthy",
        "transport": "HTTP / REST",
    }


@app.get("/api/v1/dashboard", response_model=KPIDashboardSummary, tags=["Dashboard"])
def get_dashboard_summary(service: DrivingSchoolService = Depends(get_service)):
    """Returns aggregated executive dashboard KPIs, accounting figures, and license distribution (REQ-010, REQ-011)."""
    return service.get_kpi_dashboard_summary()


@app.get("/api/v1/students", response_model=List[Student], tags=["Students"])
def list_students(service: DrivingSchoolService = Depends(get_service)):
    """Lists all enrolled students."""
    return service.get_all_students()


@app.get("/api/v1/students/{dni}", response_model=Student, tags=["Students"])
def get_student(dni: str, service: DrivingSchoolService = Depends(get_service)):
    """Retrieves a single student by verified DNI/NIE."""
    student = service.get_student_by_dni(dni)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")
    return student


@app.post("/api/v1/students", response_model=Student, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: Student, service: DrivingSchoolService = Depends(get_service)):
    """Enrolls a new student with strict DNI/NIE modulo 23 checksum validation (REQ-001, REQ-002)."""
    existing = service.get_student_by_dni(student.dni)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Student with DNI {student.dni} already exists.")
    return service.register_student(student)


@app.delete("/api/v1/students/{dni}", status_code=status.HTTP_204_NO_CONTENT, tags=["Students"])
def delete_student(dni: str, service: DrivingSchoolService = Depends(get_service)):
    """Deletes a student record by DNI."""
    deleted = service.delete_student(dni)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")


@app.post("/api/v1/students/{dni}/classes", response_model=Student, tags=["Student Operations"])
def add_classes(dni: str, payload: AddClassesRequest, service: DrivingSchoolService = Depends(get_service)):
    """Records completed practical driving lessons for a student (REQ-003)."""
    try:
        return service.add_student_classes(dni, payload.count)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")


@app.post("/api/v1/students/{dni}/exams", response_model=Student, tags=["Student Operations"])
def register_exam(dni: str, payload: RegisterExamRequest, service: DrivingSchoolService = Depends(get_service)):
    """Records a theoretical or practical exam attempt for a student."""
    try:
        return service.register_student_exam(dni, payload.exam_type)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")


@app.post("/api/v1/students/{dni}/advances", response_model=Student, tags=["Student Operations"])
def record_advance(dni: str, payload: RecordAdvanceRequest, service: DrivingSchoolService = Depends(get_service)):
    """Records an advance deposit payment towards the student's account (REQ-006)."""
    try:
        return service.record_student_advance(dni, payload.amount)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


@app.get("/api/v1/students/{dni}/invoice", response_model=InvoiceCalculation, tags=["Billing"])
def get_invoice(dni: str, service: DrivingSchoolService = Depends(get_service)):
    """Calculates the authoritative itemized billing statement for a student (REQ-005, REQ-008, REQ-014)."""
    try:
        return service.calculate_student_invoice(dni)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")


@app.get("/api/v1/students/{dni}/pdf", tags=["Billing"])
def download_invoice_pdf(dni: str, service: DrivingSchoolService = Depends(get_service)):
    """Generates and streams official PDF invoice documentation directly from memory without disk writes (REQ-009)."""
    try:
        invoice, pdf_bytes = service.generate_student_invoice_pdf(dni)
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")

    headers = {
        "Content-Disposition": f'attachment; filename="Factura_{invoice.student_dni}_{invoice.invoice_number}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@app.get("/api/v1/dgt/appointments", response_model=List[DgtExamAppointment], tags=["DGT Exams"])
def list_all_dgt_appointments(service: DrivingSchoolService = Depends(get_service)):
    """Lists all scheduled DGT examination appointments across all students (REQ-004)."""
    return service.get_all_dgt_appointments()


@app.get("/api/v1/students/{dni}/dgt/appointments", response_model=List[DgtExamAppointment], tags=["DGT Exams"])
def list_student_dgt_appointments(dni: str, service: DrivingSchoolService = Depends(get_service)):
    """Retrieves all DGT examination appointments for a specific student (REQ-004)."""
    return service.get_student_dgt_appointments(dni)


@app.post("/api/v1/students/{dni}/dgt/appointments", response_model=DgtExamAppointment, status_code=status.HTTP_201_CREATED, tags=["DGT Exams"])
def schedule_dgt_appointment(dni: str, payload: ScheduleDgtAppointmentRequest, service: DrivingSchoolService = Depends(get_service)):
    """Schedules and persists an official DGT exam appointment for a student (REQ-004)."""
    try:
        return service.schedule_dgt_appointment(
            dni=dni,
            exam_type=payload.exam_type,
            appointment_date=payload.appointment_date,
            center_location=payload.center_location,
        )
    except StudentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with DNI {dni} not found.")


@app.get("/api/v1/instructors", response_model=List[Instructor], tags=["Instructors & Fleet"])
def list_instructors(service: DrivingSchoolService = Depends(get_service)):
    """Lists all instructors, assigned fleet vehicles, and fuel expenses."""
    return service.get_all_instructors()


@app.post("/api/v1/instructors/{instructor_id}/fuel", response_model=Instructor, tags=["Instructors & Fleet"])
def record_fuel_expense(instructor_id: str, payload: RecordFuelRequest, service: DrivingSchoolService = Depends(get_service)):
    """Records vehicle fuel expenses attributed to an instructor."""
    try:
        return service.record_fuel_expense(instructor_id, payload.amount)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))


@app.get("/api/v1/packages", response_model=List[LicensePackage], tags=["License Packages"])
def list_packages(service: DrivingSchoolService = Depends(get_service)):
    """Lists commercial license packages and associated pricing rules."""
    return service.get_all_packages()


@app.post("/api/v1/admin/reset", tags=["Admin & Demo"])
def reset_demo_database(service: DrivingSchoolService = Depends(get_service)):
    """Resets operational database to synthetic fictional demo profiles (REQ-012)."""
    service.reset_demo_data()
    return {"status": "ok", "message": "Database reset to synthetic demo defaults."}


@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def scalar_api_docs():
    """Scalar Interactive API Documentation."""
    return HTMLResponse(
        """
        <!doctype html>
        <html>
          <head>
            <title>NainDrive API Documentation</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>
              body { margin: 0; background-color: #0b0f19; }
            </style>
          </head>
          <body>
            <script
              id="api-reference"
              data-url="/openapi.json"
              data-configuration='{"theme": "deepSpace"}'
              src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
          </body>
        </html>
        """
    )
