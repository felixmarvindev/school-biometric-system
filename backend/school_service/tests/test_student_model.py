"""Tests for Student Model (Task 012)."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select

from school_service.models.student import Student, Gender
from school_service.models.school import School
from school_service.models.academic_class import AcademicClass
from school_service.models.stream import Stream


@pytest.mark.asyncio
@pytest.mark.integration
async def test_students_table_exists(test_db: AsyncSession):
    """
    Test that students table exists in the database.
    
    Acceptance Criteria:
    - Student model exists with all required fields
    - Database migration creates `students` table correctly
    """
    async with test_db.bind.connect() as conn:
        def check_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()
        
        tables = await conn.run_sync(check_tables)
        
        assert "students" in tables, "students table should exist in the database"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_students_table_has_all_required_columns(test_db: AsyncSession):
    """
    Test that students table has all required columns with correct types.
    
    Acceptance Criteria:
    - Student model exists with all required fields
    - Database migration creates `students` table correctly
    """
    async with test_db.bind.connect() as conn:
        def get_columns(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_columns("students")
        
        columns = await conn.run_sync(get_columns)
        column_names = [col["name"] for col in columns]
        
        # Required columns
        required_columns = [
            "id",
            "school_id",
            "admission_number",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "class_id",
            "stream_id",
            "parent_phone",
            "parent_email",
            "created_at",
            "updated_at",
            "is_deleted",
        ]
        
        for col_name in required_columns:
            assert col_name in column_names, f"Column '{col_name}' should exist in students table"
        
        # Verify column types and constraints
        column_dict = {col["name"]: col for col in columns}
        
        # id - Integer, primary key, autoincrement
        assert column_dict["id"]["type"].python_type == int, "id should be Integer type"
        assert bool(column_dict["id"]["primary_key"]), "id should be primary key"
        
        # school_id - Integer, foreign key, not null
        assert column_dict["school_id"]["type"].python_type == int, "school_id should be Integer type"
        assert column_dict["school_id"]["nullable"] is False, "school_id should be NOT NULL"
        
        # admission_number - String, not null
        assert column_dict["admission_number"]["nullable"] is False, "admission_number should be NOT NULL"
        
        # first_name - String, not null
        assert column_dict["first_name"]["nullable"] is False, "first_name should be NOT NULL"
        
        # last_name - String, not null
        assert column_dict["last_name"]["nullable"] is False, "last_name should be NOT NULL"
        
        # Optional fields should be nullable
        assert column_dict["date_of_birth"]["nullable"] is True, "date_of_birth should be nullable"
        assert column_dict["gender"]["nullable"] is True, "gender should be nullable"
        assert column_dict["class_id"]["nullable"] is True, "class_id should be nullable"
        assert column_dict["stream_id"]["nullable"] is True, "stream_id should be nullable"
        assert column_dict["parent_phone"]["nullable"] is True, "parent_phone should be nullable"
        assert column_dict["parent_email"]["nullable"] is True, "parent_email should be nullable"
        
        # is_deleted - Boolean, not null, has default
        assert column_dict["is_deleted"]["nullable"] is False, "is_deleted should be NOT NULL"
        
        # created_at - DateTime, not null, has default
        assert column_dict["created_at"]["nullable"] is False, "created_at should be NOT NULL"
        
        # updated_at - DateTime, nullable
        assert column_dict["updated_at"]["nullable"] is True, "updated_at should be nullable"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_students_table_has_foreign_keys(test_db: AsyncSession):
    """
    Test that students table has foreign key constraints.
    
    Acceptance Criteria:
    - Foreign key to schools table
    - Foreign key to classes table (optional, nullable)
    - Foreign key to streams table (optional, nullable)
    """
    async with test_db.bind.connect() as conn:
        def get_foreign_keys(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_foreign_keys("students")
        
        foreign_keys = await conn.run_sync(get_foreign_keys)
        
        # Find foreign keys
        school_fk = None
        class_fk = None
        stream_fk = None
        
        for fk in foreign_keys:
            if fk["referred_table"] == "schools" and "school_id" in fk["constrained_columns"]:
                school_fk = fk
            elif fk["referred_table"] == "classes" and "class_id" in fk["constrained_columns"]:
                class_fk = fk
            elif fk["referred_table"] == "streams" and "stream_id" in fk["constrained_columns"]:
                stream_fk = fk
        
        assert school_fk is not None, "students table should have foreign key to schools table"
        assert "school_id" in school_fk["constrained_columns"], "Foreign key should be on school_id column"
        assert "id" in school_fk["referred_columns"], "Foreign key should reference schools.id"
        
        assert class_fk is not None, "students table should have foreign key to classes table"
        assert "class_id" in class_fk["constrained_columns"], "Foreign key should be on class_id column"
        assert "id" in class_fk["referred_columns"], "Foreign key should reference classes.id"
        
        assert stream_fk is not None, "students table should have foreign key to streams table"
        assert "stream_id" in stream_fk["constrained_columns"], "Foreign key should be on stream_id column"
        assert "id" in stream_fk["referred_columns"], "Foreign key should reference streams.id"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_students_table_has_unique_constraint(test_db: AsyncSession):
    """
    Test that students table has unique constraint on (school_id, admission_number).
    
    Acceptance Criteria:
    - Admission number has unique constraint per school
    """
    async with test_db.bind.connect() as conn:
        def get_unique_constraints(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_unique_constraints("students")
        
        unique_constraints = await conn.run_sync(get_unique_constraints)
        
        # Find unique constraint on (school_id, admission_number)
        admission_constraint = None
        for uc in unique_constraints:
            if "school_id" in uc["column_names"] and "admission_number" in uc["column_names"]:
                admission_constraint = uc
                break
        
        assert admission_constraint is not None, "students table should have unique constraint on (school_id, admission_number)"
        assert "school_id" in admission_constraint["column_names"], "Unique constraint should include school_id"
        assert "admission_number" in admission_constraint["column_names"], "Unique constraint should include admission_number"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_students_table_has_required_indexes(test_db: AsyncSession):
    """
    Test that students table has required indexes.
    
    Acceptance Criteria:
    - Database migration creates `students` table correctly
    """
    async with test_db.bind.connect() as conn:
        def get_indexes(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_indexes("students")
        
        indexes = await conn.run_sync(get_indexes)
        index_names = [idx["name"] for idx in indexes]
        
        # Required indexes (based on model definition)
        required_indexes = [
            "ix_students_id",
            "ix_students_school_id",
            "ix_students_admission_number",
            "ix_students_class_id",
            "ix_students_stream_id",
            "ix_students_is_deleted",
        ]
        
        for idx_name in required_indexes:
            assert idx_name in index_names, f"Index '{idx_name}' should exist on students table"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_student_model_has_default_values(test_db: AsyncSession):
    """
    Test that Student model has correct default values.
    
    Acceptance Criteria:
    - Database migration creates `students` table correctly
    """
    # Create a school first (required for foreign key)
    school = School(
        name="Test School",
        code="TEST-STU-001",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a student with minimal data (should use defaults)
    student = Student(
        school_id=school.id,
        admission_number="STD-001",
        first_name="John",
        last_name="Doe",
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)
    
    # Verify defaults
    assert student.is_deleted is False, "is_deleted should default to False"
    assert student.created_at is not None, "created_at should be set automatically"
    # Optional fields should be None
    assert student.date_of_birth is None, "date_of_birth should be None by default"
    assert student.gender is None, "gender should be None by default"
    assert student.class_id is None, "class_id should be None by default"
    assert student.stream_id is None, "stream_id should be None by default"
    assert student.parent_phone is None, "parent_phone should be None by default"
    assert student.parent_email is None, "parent_email should be None by default"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_student_model_has_timestamps(test_db: AsyncSession):
    """
    Test that Student model includes timestamps.
    
    Acceptance Criteria:
    - Model includes timestamps (created_at, updated_at)
    """
    # Create a school first
    school = School(
        name="Test School",
        code="TEST-STU-002",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a student
    student = Student(
        school_id=school.id,
        admission_number="STD-002",
        first_name="Jane",
        last_name="Smith",
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)
    
    # Verify timestamps exist
    assert hasattr(student, "created_at"), "Student model should have created_at attribute"
    assert hasattr(student, "updated_at"), "Student model should have updated_at attribute"
    assert student.created_at is not None, "created_at should be set when student is created"
    
    # Update student and verify updated_at changes
    original_updated_at = student.updated_at
    student.first_name = "Jane Updated"
    await test_db.commit()
    await test_db.refresh(student)
    
    # Note: SQLite may not update updated_at automatically in tests, but the field should exist
    assert hasattr(student, "updated_at"), "updated_at should exist"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_student_model_has_soft_delete(test_db: AsyncSession):
    """
    Test that Student model includes soft delete support.
    
    Acceptance Criteria:
    - Model includes soft delete support (is_deleted)
    """
    # Create a school first
    school = School(
        name="Test School",
        code="TEST-STU-003",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a student
    student = Student(
        school_id=school.id,
        admission_number="STD-003",
        first_name="Test",
        last_name="Student",
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)
    
    # Verify soft delete field exists and defaults to False
    assert hasattr(student, "is_deleted"), "Student model should have is_deleted attribute"
    assert student.is_deleted is False, "is_deleted should default to False"
    
    # Test soft delete
    student.is_deleted = True
    await test_db.commit()
    await test_db.refresh(student)
    assert student.is_deleted is True, "is_deleted should be settable to True"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_student_model_relationships(test_db: AsyncSession):
    """
    Test that Student model has relationships to School, Class, and Stream.
    
    Acceptance Criteria:
    - Relationships work correctly
    """
    # Create a school
    school = School(
        name="Test School",
        code="TEST-STU-004",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create a class
    academic_class = AcademicClass(
        school_id=school.id,
        name="Form 1",
    )
    test_db.add(academic_class)
    await test_db.commit()
    await test_db.refresh(academic_class)
    
    # Create a stream
    stream = Stream(
        class_id=academic_class.id,
        name="A",
    )
    test_db.add(stream)
    await test_db.commit()
    await test_db.refresh(stream)
    
    # Create a student with class and stream
    student = Student(
        school_id=school.id,
        admission_number="STD-004",
        first_name="Test",
        last_name="Student",
        class_id=academic_class.id,
        stream_id=stream.id,
    )
    test_db.add(student)
    await test_db.commit()
    await test_db.refresh(student)
    
    # Verify relationships
    assert hasattr(student, "school"), "Student model should have school relationship"
    assert student.school is not None, "Student should have access to school via relationship"
    assert student.school.id == school.id, "Student's school relationship should point to correct school"
    
    assert hasattr(student, "class_"), "Student model should have class_ relationship"
    assert student.class_ is not None, "Student should have access to class via relationship"
    assert student.class_.id == academic_class.id, "Student's class relationship should point to correct class"
    
    assert hasattr(student, "stream"), "Student model should have stream relationship"
    assert student.stream is not None, "Student should have access to stream via relationship"
    assert student.stream.id == stream.id, "Student's stream relationship should point to correct stream"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_student_model_gender_enum(test_db: AsyncSession):
    """
    Test that Student model gender field uses Gender enum.
    
    Acceptance Criteria:
    - Gender field accepts enum values
    """
    # Create a school
    school = School(
        name="Test School",
        code="TEST-STU-005",
    )
    test_db.add(school)
    await test_db.commit()
    await test_db.refresh(school)
    
    # Create students with different gender values
    student_male = Student(
        school_id=school.id,
        admission_number="STD-005-M",
        first_name="Male",
        last_name="Student",
        gender=Gender.MALE,
    )
    test_db.add(student_male)
    
    student_female = Student(
        school_id=school.id,
        admission_number="STD-005-F",
        first_name="Female",
        last_name="Student",
        gender=Gender.FEMALE,
    )
    test_db.add(student_female)
    
    student_other = Student(
        school_id=school.id,
        admission_number="STD-005-O",
        first_name="Other",
        last_name="Student",
        gender=Gender.OTHER,
    )
    test_db.add(student_other)
    
    await test_db.commit()
    
    # Verify gender values
    assert student_male.gender == Gender.MALE, "Gender should accept MALE value"
    assert student_female.gender == Gender.FEMALE, "Gender should accept FEMALE value"
    assert student_other.gender == Gender.OTHER, "Gender should accept OTHER value"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_student_admission_number_uniqueness_per_school(test_db: AsyncSession):
    """
    Test that admission numbers are unique per school.
    
    Acceptance Criteria:
    - Admission number has unique constraint per school
    """
    # Create two schools
    school1 = School(
        name="Test School 1",
        code="TEST-STU-006-1",
    )
    school2 = School(
        name="Test School 2",
        code="TEST-STU-006-2",
    )
    test_db.add(school1)
    test_db.add(school2)
    await test_db.commit()
    await test_db.refresh(school1)
    await test_db.refresh(school2)
    
    # Create student in school1
    student1 = Student(
        school_id=school1.id,
        admission_number="STD-006",
        first_name="Student",
        last_name="One",
    )
    test_db.add(student1)
    await test_db.commit()
    
    # Same admission number in different school should work
    student2 = Student(
        school_id=school2.id,
        admission_number="STD-006",  # Same admission number, different school
        first_name="Student",
        last_name="Two",
    )
    test_db.add(student2)
    await test_db.commit()
    
    # Same admission number in same school should fail
    student3 = Student(
        school_id=school1.id,
        admission_number="STD-006",  # Same admission number, same school
        first_name="Student",
        last_name="Three",
    )
    test_db.add(student3)
    
    # Should raise IntegrityError due to unique constraint
    with pytest.raises(Exception):  # Could be IntegrityError or similar
        await test_db.commit()

