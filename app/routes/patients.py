import os
import json
from datetime import datetime, timezone, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Patient
from app.schemas import PatientCreate, PatientUpdate, PatientResponse, APIResponse
from app.validators import validate_and_normalize_phone

router = APIRouter(prefix="/patients", tags=["Patients"])

# Ensure logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
CALL_LOG_PATH = os.path.join(LOGS_DIR, "calls.log")


def log_call_activity(action: str, patient_data: dict):
    """Logs patient creation and update activities with UTC timestamp to logs/calls.log."""
    try:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "payload": patient_data
        }
        with open(CALL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")
    except Exception as e:
        print(f"Error writing to calls.log: {e}")


@router.get("/check", response_model=APIResponse[Optional[PatientResponse]])
def check_existing_patient(
    phone_number: str = Query(..., description="10-digit US phone number to check"),
    db: Session = Depends(get_db)
):
    """
    Voice agent duplicate check endpoint.
    Checks if a non-deleted patient already exists with the given phone number.
    Returns patient record if found, or data: null if no match.
    """
    try:
        normalized_phone = validate_and_normalize_phone(phone_number)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )

    patient = db.query(Patient).filter(
        Patient.phone_number == normalized_phone,
        Patient.deleted_at.is_(None)
    ).first()

    if patient:
        return APIResponse(data=PatientResponse.model_validate(patient), error=None)
    
    return APIResponse(data=None, error=None)


@router.get("", response_model=APIResponse[List[PatientResponse]])
def list_patients(
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    date_of_birth: Optional[date] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
    phone_number: Optional[str] = Query(None, description="Filter by phone number"),
    db: Session = Depends(get_db)
):
    """
    List all active (non-deleted) patients.
    Supports optional query filters: last_name, date_of_birth, phone_number.
    """
    query = db.query(Patient).filter(Patient.deleted_at.is_(None))

    if last_name:
        query = query.filter(Patient.last_name.ilike(f"%{last_name.strip()}%"))
    if date_of_birth:
        query = query.filter(Patient.date_of_birth == date_of_birth)
    if phone_number:
        try:
            norm_phone = validate_and_normalize_phone(phone_number)
            query = query.filter(Patient.phone_number == norm_phone)
        except ValueError:
            query = query.filter(Patient.phone_number.like(f"%{phone_number}%"))

    patients = query.order_by(Patient.created_at.desc()).all()
    results = [PatientResponse.model_validate(p) for p in patients]
    return APIResponse(data=results, error=None)


@router.get("/{patient_id}", response_model=APIResponse[PatientResponse])
def get_patient_by_id(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve single non-deleted patient by patient_id (UUID)."""
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at.is_(None)
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )

    return APIResponse(data=PatientResponse.model_validate(patient), error=None)


@router.post("", response_model=APIResponse[PatientResponse], status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new patient record.
    Validates input fields, saves to database, and logs call to logs/calls.log.
    """
    patient = Patient(
        first_name=patient_in.first_name,
        last_name=patient_in.last_name,
        date_of_birth=patient_in.date_of_birth,
        sex=patient_in.sex,
        phone_number=patient_in.phone_number,
        email=patient_in.email,
        address_line_1=patient_in.address_line_1,
        address_line_2=patient_in.address_line_2,
        city=patient_in.city,
        state=patient_in.state,
        zip_code=patient_in.zip_code,
        insurance_provider=patient_in.insurance_provider,
        insurance_member_id=patient_in.insurance_member_id,
        preferred_language=patient_in.preferred_language or "English",
        emergency_contact_name=patient_in.emergency_contact_name,
        emergency_contact_phone=patient_in.emergency_contact_phone
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    patient_resp = PatientResponse.model_validate(patient)
    log_call_activity("CREATE_PATIENT", patient_resp.model_dump(mode="json"))

    return APIResponse(data=patient_resp, error=None)


@router.put("/{patient_id}", response_model=APIResponse[PatientResponse])
def update_patient(
    patient_id: str,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update existing patient (supports partial updates).
    Updates updated_at timestamp, saves to database, and logs to logs/calls.log.
    """
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at.is_(None)
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )

    update_data = patient_in.model_dump(exclude_unset=True)
    if not update_data:
        return APIResponse(data=PatientResponse.model_validate(patient), error=None)

    for field, value in update_data.items():
        setattr(patient, field, value)

    patient.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(patient)

    patient_resp = PatientResponse.model_validate(patient)
    log_call_activity("UPDATE_PATIENT", patient_resp.model_dump(mode="json"))

    return APIResponse(data=patient_resp, error=None)


@router.delete("/{patient_id}", response_model=APIResponse[dict])
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete patient record by setting deleted_at timestamp.
    """
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at.is_(None)
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )

    patient.deleted_at = datetime.now(timezone.utc)
    db.commit()

    log_call_activity("DELETE_PATIENT", {"patient_id": patient_id, "deleted_at": patient.deleted_at.isoformat()})

    return APIResponse(
        data={"message": f"Patient '{patient_id}' soft deleted successfully."},
        error=None
    )
