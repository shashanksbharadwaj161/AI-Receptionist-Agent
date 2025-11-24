import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    owner_name = Column(String, nullable=True)
    owner_phone = Column(String, nullable=True)
    timezone = Column(String, nullable=False, default="Asia/Kolkata")
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    config = relationship("FacilityConfig", back_populates="facility", uselist=False, cascade="all, delete")
    courts = relationship("Court", back_populates="facility", cascade="all, delete")


class FacilityConfig(Base):
    __tablename__ = "facility_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    open_hours = Column(JSONB, nullable=False)
    slot_minutes = Column(Integer, nullable=False, default=60)
    max_courts = Column(Integer, nullable=False, default=1)
    pricing_rules = Column(JSONB, nullable=True)
    google_calendar_mode = Column(String, nullable=False, default="single_calendar")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    facility = relationship("Facility", back_populates="config")


class Court(Base):
    __tablename__ = "courts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    calendar_id = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    facility = relationship("Facility", back_populates="courts")
    bookings = relationship("Booking", back_populates="court")


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("facility_id", "phone"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="customer")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    court_id = Column(UUID(as_uuid=True), ForeignKey("courts.id", ondelete="SET NULL"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String, nullable=False, default="confirmed")
    google_event_id = Column(String, nullable=True)
    price = Column(Numeric, nullable=True)
    source = Column(String, nullable=False, default="phone_ai")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="bookings")
    court = relationship("Court", back_populates="bookings")
    facility = relationship("Facility")


class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id = Column(UUID(as_uuid=True), ForeignKey("facilities.id", ondelete="CASCADE"), nullable=False)
    caller_phone = Column(String, nullable=True)
    started_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    ended_at = Column(TIMESTAMP(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    outcome = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    facility = relationship("Facility")
