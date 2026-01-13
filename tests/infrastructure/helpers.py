"""Helper classes and fixtures for infrastructure tests.

This module provides test entities that mimic the structure of real domain aggregates
to allow testing infrastructure components (Repositories, UoW) without coupling
to specific domain entities that might change or be deleted.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self

from sqlmodel import Field, SQLModel
from ulid import ULID

from app.core.result import Err, Ok, Result
from app.domain.interfaces import IAuditable, IValueObject
from app.domain.value_objects.version import Version
from app.infrastructure.orm_mapping import register_orm_mapping


# --- Value Object Stub ---
@dataclass(frozen=True)
class TestId(IValueObject[str]):
    """Test ID value object."""

    value: str

    @classmethod
    def from_primitive(cls, value: str) -> Result[Self, ValueError]:
        if not value:
            return Err(ValueError("Value cannot be empty"))
        return Ok(cls(value))

    def to_primitive(self) -> str:
        return self.value

    @classmethod
    def generate(cls) -> Result[Self, ValueError]:
        return Ok(cls(str(ULID())))


# --- Field-based Entity (mimics User) ---
@dataclass
class TestEntity(IAuditable):
    """Test entity using public fields (like User)."""

    id: TestId
    name: str
    email: str
    version: Version = field(default_factory=lambda: Version.from_primitive(0).unwrap())
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, name: str, email: str) -> "TestEntity":
        return cls(
            id=TestId.generate().unwrap(),
            name=name,
            email=email,
        )

    def change_email(self, new_email: str) -> "TestEntity":
        # Simulate immutability by returning new instance with updated field
        return TestEntity(
            id=self.id,
            name=self.name,
            email=new_email,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class TestEntityORM(SQLModel, table=True):
    """ORM mapping for TestEntity."""

    __tablename__ = "test_entities"  # type: ignore[reportAssignmentType]

    id: str = Field(primary_key=True)
    name: str
    email: str
    version: int = Field(default=0)
    created_at: datetime
    updated_at: datetime


# --- Property-based Entity (mimics Team) ---
@dataclass
class TestPropertyEntity(IAuditable):
    """Test entity using underscore attributes and properties (like Team)."""

    _id: TestId
    _name: str
    _description: str | None = None
    _version: Version = field(
        default_factory=lambda: Version.from_primitive(0).unwrap()
    )
    _created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, name: str, description: str | None = None) -> "TestPropertyEntity":
        return cls(
            _id=TestId.generate().unwrap(),
            _name=name,
            _description=description,
        )

    @property
    def id(self) -> TestId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def version(self) -> Version:
        return self._version

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        self._updated_at = value

    def change_name(self, new_name: str) -> "TestPropertyEntity":
        return TestPropertyEntity(
            _id=self._id,
            _name=new_name,
            _description=self._description,
            _version=self._version,
            _created_at=self._created_at,
            _updated_at=self._updated_at,
        )


class TestPropertyEntityORM(SQLModel, table=True):
    """ORM mapping for TestPropertyEntity."""

    __tablename__: Any = "test_property_entities"

    id: str = Field(primary_key=True)
    name: str
    description: str | None = None
    version: int = Field(default=0)
    created_at: datetime
    updated_at: datetime


def register_test_mappings() -> None:
    """Register ORM mappings for test entities."""
    register_orm_mapping(TestEntity, TestEntityORM)
    register_orm_mapping(TestPropertyEntity, TestPropertyEntityORM)
