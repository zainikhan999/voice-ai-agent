import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, String, Date, DateTime, Enum, Text
from app.database import Base


class SexEnum(str, enum.Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    DECLINE_TO_ANSWER = "Decline to Answer"


def generate_uuid():
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(String(36), primary_key=True, default=generate_uuid)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(Enum(SexEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    phone_number = Column(String(10), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    insurance_provider = Column(String(100), nullable=True)
    insurance_member_id = Column(String(50), nullable=True)
    preferred_language = Column(String(50), nullable=True, default="English")
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(10), nullable=True)
    created_at = Column(DateTime, nullable=False, default=get_utc_now)
    updated_at = Column(DateTime, nullable=False, default=get_utc_now, onupdate=get_utc_now)
    deleted_at = Column(DateTime, nullable=True, index=True)
