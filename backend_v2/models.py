from datetime import datetime, date, timezone
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class Record:
    id: Mapped[int] = mapped_column(primary_key=True)
    revision: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)

class Vehicle(Record, Base):
    __tablename__ = 'vehicles_v2'
    make: Mapped[str] = mapped_column(String(60), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price_pence: Mapped[int] = mapped_column(Integer, nullable=False)
    approved_facts: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(12), default='available', nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    __table_args__ = (CheckConstraint('price_pence >= 0 AND price_pence <= 100000000'),CheckConstraint('year >= 1900 AND year <= 2100'),CheckConstraint("status IN ('available','reserved','sold')"),CheckConstraint('revision >= 1'))

class Enquiry(Record, Base):
    __tablename__ = 'enquiries_v2'
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicles_v2.id'), nullable=False, index=True)
    customer: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(12), default='new', nullable=False)
    __table_args__ = (CheckConstraint("status IN ('new','contacted','closed')"),CheckConstraint('revision >= 1'))

class Task(Record, Base):
    __tablename__ = 'tasks_v2'
    enquiry_id: Mapped[int] = mapped_column(ForeignKey('enquiries_v2.id'), nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    note: Mapped[str] = mapped_column(String(300), default='', nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    __table_args__ = (CheckConstraint('revision >= 1'),)

class AuditEvent(Base):
    __tablename__ = 'audit_events_v2'
    id: Mapped[int] = mapped_column(primary_key=True)
    entity: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    # IDs/state only. Never store customer messages or credentials here.
