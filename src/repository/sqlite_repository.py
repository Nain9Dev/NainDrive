"""
SQLAlchemy Transacion Repository and Embedded SQLite Driver.
Provides relational data persistence, clean domain mapping, and automatic seeding of synthetic demo accounts.
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table
from sqlalchemy.sql import select, insert, update, delete

from src.domain.models import Student, Instructor, LicensePackage
from src.domain.exceptions import StudentNotFoundError

metadata = MetaData()

students_table = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("registration_number", String(50), nullable=False),
    Column("dni", String(20), unique=True, index=True, nullable=False),
    Column("first_name", String(100), nullable=False),
    Column("last_name", String(100), nullable=False),
    Column("phone", String(50), default="600000000"),
    Column("target_license", String(20), default="B"),
    Column("assigned_instructor_id", String(50), default="INST-01"),
    Column("completed_classes", Integer, default=0),
    Column("theoretical_exams_count", Integer, default=0),
    Column("practical_exams_count", Integer, default=0),
    Column("total_advances_paid", Float, default=0.0),
)

instructors_table = Table(
    "instructors",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("instructor_id", String(50), unique=True, index=True, nullable=False),
    Column("full_name", String(200), nullable=False),
    Column("assigned_vehicle_plate", String(20), nullable=False),
    Column("vehicle_model", String(100), nullable=False),
    Column("itv_expiration_date", String(50), nullable=False),
    Column("total_fuel_expenses", Float, default=0.0),
)

packages_table = Table(
    "license_packages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("package_code", String(50), unique=True, index=True, nullable=False),
    Column("name", String(200), nullable=False),
    Column("enrollment_fee", Float, nullable=False),
    Column("included_practical_classes", Integer, nullable=False),
    Column("extra_class_price", Float, nullable=False),
    Column("dgt_exam_fee", Float, nullable=False),
    Column("renewal_fee", Float, default=150.0),
)


class SQLiteRepository:
    """Repository implementation providing transactional access and domain conversions."""

    def __init__(self, db_url: str = "sqlite:///autoescuela.db", auto_seed: bool = True):
        self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        metadata.create_all(self.engine)
        if auto_seed:
            self._ensure_synthetic_seed_data()

    def _ensure_synthetic_seed_data(self) -> None:
        """Populates realistic demo figures if the database tables are completely empty."""
        with self.engine.begin() as conn:
            package_count = conn.execute(select(packages_table)).first()
            if package_count is None:
                default_packages = [
                    {
                        "package_code": "PERMIT_B",
                        "name": "Permiso B - Turismo (Manual / Automático)",
                        "enrollment_fee": 195.00,
                        "included_practical_classes": 10,
                        "extra_class_price": 32.50,
                        "dgt_exam_fee": 94.05,
                        "renewal_fee": 150.00,
                    },
                    {
                        "package_code": "PERMIT_A2",
                        "name": "Permiso A2 - Motocicletas hasta 35kW",
                        "enrollment_fee": 150.00,
                        "included_practical_classes": 5,
                        "extra_class_price": 28.00,
                        "dgt_exam_fee": 94.05,
                        "renewal_fee": 150.00,
                    },
                    {
                        "package_code": "PERMIT_C",
                        "name": "Permiso C - Camión Rígido Profesional",
                        "enrollment_fee": 350.00,
                        "included_practical_classes": 8,
                        "extra_class_price": 55.00,
                        "dgt_exam_fee": 94.05,
                        "renewal_fee": 180.00,
                    },
                ]
                conn.execute(insert(packages_table), default_packages)

            instructor_count = conn.execute(select(instructors_table)).first()
            if instructor_count is None:
                default_instructors = [
                    {
                        "instructor_id": "INST-01",
                        "full_name": "NainDev Mendoza Vallejo",
                        "assigned_vehicle_plate": "1234-BBC",
                        "vehicle_model": "SEAT León 2.0 TDI FR",
                        "itv_expiration_date": "01-08-2027",
                        "total_fuel_expenses": 450.50,
                    },
                    {
                        "instructor_id": "INST-02",
                        "full_name": "Carlos García Torrijos",
                        "assigned_vehicle_plate": "5678-LMN",
                        "vehicle_model": "Yamaha MT-07 ABS",
                        "itv_expiration_date": "15-11-2026",
                        "total_fuel_expenses": 180.20,
                    },
                    {
                        "instructor_id": "INST-03",
                        "full_name": "Elena Rostropovich",
                        "assigned_vehicle_plate": "9012-KLP",
                        "vehicle_model": "Volvo FL6 Camión Rígido",
                        "itv_expiration_date": "30-04-2027",
                        "total_fuel_expenses": 890.00,
                    },
                ]
                conn.execute(insert(instructors_table), default_instructors)

            student_count = conn.execute(select(students_table)).first()
            if student_count is None:
                default_students = [
                    {
                        "registration_number": "EXP-2026-001",
                        "dni": "53822281G",
                        "first_name": "Alvaro",
                        "last_name": "Morata Lopez",
                        "phone": "612345678",
                        "target_license": "B",
                        "assigned_instructor_id": "INST-01",
                        "completed_classes": 14,
                        "theoretical_exams_count": 1,
                        "practical_exams_count": 1,
                        "total_advances_paid": 250.00,
                    },
                    {
                        "registration_number": "EXP-2026-002",
                        "dni": "11223344B",
                        "first_name": "Lucia",
                        "last_name": "Jimenez Diaz",
                        "phone": "698765432",
                        "target_license": "A2",
                        "assigned_instructor_id": "INST-02",
                        "completed_classes": 5,
                        "theoretical_exams_count": 1,
                        "practical_exams_count": 0,
                        "total_advances_paid": 150.00,
                    },
                    {
                        "registration_number": "EXP-2026-003",
                        "dni": "44556677C",
                        "first_name": "David",
                        "last_name": "Rodriguez Fernandez",
                        "phone": "655443322",
                        "target_license": "C",
                        "assigned_instructor_id": "INST-03",
                        "completed_classes": 12,
                        "theoretical_exams_count": 2,
                        "practical_exams_count": 1,
                        "total_advances_paid": 500.00,
                    },
                    {
                        "registration_number": "EXP-2026-004",
                        "dni": "78901234Z",
                        "first_name": "Sofia",
                        "last_name": "Alvarez Castillo",
                        "phone": "677889900",
                        "target_license": "B",
                        "assigned_instructor_id": "INST-01",
                        "completed_classes": 3,
                        "theoretical_exams_count": 0,
                        "practical_exams_count": 0,
                        "total_advances_paid": 100.00,
                    },
                ]
                conn.execute(insert(students_table), default_students)

    def get_all_students(self) -> List[Student]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(students_table)).mappings().all()
            return [Student(**row) for row in rows]

    def get_student_by_dni(self, dni: str) -> Optional[Student]:
        clean_dni = dni.strip().upper()
        with self.engine.connect() as conn:
            row = conn.execute(select(students_table).where(students_table.c.dni == clean_dni)).mappings().first()
            if row:
                return Student(**row)
        return None

    def save_student(self, student: Student) -> Student:
        with self.engine.begin() as conn:
            existing = conn.execute(select(students_table).where(students_table.c.dni == student.dni)).first()
            data = student.model_dump()
            if existing:
                conn.execute(update(students_table).where(students_table.c.dni == student.dni).values(**data))
            else:
                conn.execute(insert(students_table), data)
        return student

    def delete_student(self, dni: str) -> bool:
        clean_dni = dni.strip().upper()
        with self.engine.begin() as conn:
            result = conn.execute(delete(students_table).where(students_table.c.dni == clean_dni))
            return result.rowcount > 0

    def get_all_instructors(self) -> List[Instructor]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(instructors_table)).mappings().all()
            return [Instructor(**row) for row in rows]

    def save_instructor(self, instructor: Instructor) -> Instructor:
        with self.engine.begin() as conn:
            existing = conn.execute(select(instructors_table).where(instructors_table.c.instructor_id == instructor.instructor_id)).first()
            data = instructor.model_dump()
            if existing:
                conn.execute(update(instructors_table).where(instructors_table.c.instructor_id == instructor.instructor_id).values(**data))
            else:
                conn.execute(insert(instructors_table), data)
        return instructor

    def get_all_packages(self) -> List[LicensePackage]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(packages_table)).mappings().all()
            return [LicensePackage(**row) for row in rows]

    def get_package_by_code_or_type(self, target_license: str) -> LicensePackage:
        """Finds a matching commercial offer for a license type (e.g., B -> PERMIT_B). Defaults to Permit B."""
        target = target_license.strip().upper()
        packages = self.get_all_packages()
        for p in packages:
            if target in p.package_code or f"PERMISO {target}" in p.name.upper() or target == p.package_code:
                return p
        # Default fallback to Permit B if custom code is unmatched
        return packages[0] if packages else LicensePackage(
            package_code="PERMIT_B", name="Permiso B Default", enrollment_fee=195.0, included_practical_classes=10, extra_class_price=32.50, dgt_exam_fee=94.05
        )

    def reset_database_to_synthetic_defaults(self) -> None:
        """Clears current operational data and re-seeds original demonstration profiles."""
        with self.engine.begin() as conn:
            conn.execute(delete(students_table))
            conn.execute(delete(instructors_table))
            conn.execute(delete(packages_table))
        self._ensure_synthetic_seed_data()
