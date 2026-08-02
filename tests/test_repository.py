"""
Unit Tests for SQLite SQLAlchemy Repository using Embedded In-Memory Storage.
Verifies automatic seeding, transactional integrity, and CRUD operations.
"""
import pytest
from src.repository.sqlite_repository import SQLiteRepository
from src.domain.models import Student


@pytest.fixture
def memory_repo() -> SQLiteRepository:
    return SQLiteRepository(db_url="sqlite:///:memory:", auto_seed=True)


def test_repository_seeding_on_initialization(memory_repo: SQLiteRepository) -> None:
    students = memory_repo.get_all_students()
    instructors = memory_repo.get_all_instructors()
    packages = memory_repo.get_all_packages()

    assert len(students) == 4
    assert len(instructors) == 3
    assert len(packages) == 3
    assert any(s.dni == "53822281G" for s in students)


def test_save_new_student_and_retrieve(memory_repo: SQLiteRepository) -> None:
    new_student = Student(
        dni="99887766X",
        first_name="Guilherma",
        last_name="Torres",
        target_license="A2"
    )
    memory_repo.save_student(new_student)

    fetched = memory_repo.get_student_by_dni("99887766X")
    assert fetched is not None
    assert fetched.first_name == "Guilherma"


def test_delete_student(memory_repo: SQLiteRepository) -> None:
    deleted = memory_repo.delete_student("53822281G")
    assert deleted is True

    assert memory_repo.get_student_by_dni("53822281G") is None


def test_reset_database_defaults(memory_repo: SQLiteRepository) -> None:
    memory_repo.delete_student("53822281G")
    assert len(memory_repo.get_all_students()) == 3

    memory_repo.reset_database_to_synthetic_defaults()
    assert len(memory_repo.get_all_students()) == 4
    assert memory_repo.get_student_by_dni("53822281G") is not None
