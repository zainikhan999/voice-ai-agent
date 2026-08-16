from datetime import date, datetime
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models import SexEnum
from app import validators

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard response envelope required across all endpoints."""
    data: Optional[T] = None
    error: Optional[str] = None


class PatientBase(BaseModel):
    first_name: str = Field(..., json_schema_extra={"example": "Jane"})
    last_name: str = Field(..., json_schema_extra={"example": "Doe"})
    date_of_birth: date = Field(..., json_schema_extra={"example": "1990-05-15"})
    sex: SexEnum = Field(..., json_schema_extra={"example": "Female"})
    phone_number: str = Field(..., json_schema_extra={"example": "(541) 919-9216"})
    email: Optional[str] = Field(None, json_schema_extra={"example": "jane.doe@example.com"})
    address_line_1: str = Field(..., json_schema_extra={"example": "123 Health Ave"})
    address_line_2: Optional[str] = Field(None, json_schema_extra={"example": "Apt 4B"})
    city: str = Field(..., json_schema_extra={"example": "Portland"})
    state: str = Field(..., json_schema_extra={"example": "OR"})
    zip_code: str = Field(..., json_schema_extra={"example": "97201"})
    insurance_provider: Optional[str] = Field(None, json_schema_extra={"example": "Blue Cross"})
    insurance_member_id: Optional[str] = Field(None, json_schema_extra={"example": "BC12345678"})
    preferred_language: Optional[str] = Field("English", json_schema_extra={"example": "English"})
    emergency_contact_name: Optional[str] = Field(None, json_schema_extra={"example": "John Doe"})
    emergency_contact_phone: Optional[str] = Field(None, json_schema_extra={"example": "5419199216"})

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        return validators.validate_name(v, "First name")

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        return validators.validate_name(v, "Last name")

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validators.validate_and_normalize_phone(v)

    @field_validator("state")
    @classmethod
    def validate_st(cls, v: str) -> str:
        return validators.validate_state(v)

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: str) -> str:
        return validators.validate_zip_code(v)

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        return validators.validate_date_of_birth(v)

    @field_validator("email")
    @classmethod
    def validate_em(cls, v: Optional[str]) -> Optional[str]:
        return validators.validate_email(v)

    @field_validator("insurance_member_id")
    @classmethod
    def validate_mem_id(cls, v: Optional[str]) -> Optional[str]:
        return validators.validate_insurance_member_id(v)

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_em_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and v.strip():
            return validators.validate_and_normalize_phone(v)
        return None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[SexEnum] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validators.validate_name(v, "First name")
        return v

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validators.validate_name(v, "Last name")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validators.validate_and_normalize_phone(v)
        return v

    @field_validator("state")
    @classmethod
    def validate_st(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validators.validate_state(v)
        return v

    @field_validator("zip_code")
    @classmethod
    def validate_zip(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validators.validate_zip_code(v)
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            return validators.validate_date_of_birth(v)
        return v

    @field_validator("email")
    @classmethod
    def validate_em(cls, v: Optional[str]) -> Optional[str]:
        return validators.validate_email(v)

    @field_validator("insurance_member_id")
    @classmethod
    def validate_mem_id(cls, v: Optional[str]) -> Optional[str]:
        return validators.validate_insurance_member_id(v)

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_em_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and v.strip():
            return validators.validate_and_normalize_phone(v)
        return None


class PatientResponse(PatientBase):
    patient_id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
