import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database with StaticPool so all connections share the same memory DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["error"] is None
    assert data["data"]["status"] == "healthy"


def test_create_patient_success():
    payload = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "date_of_birth": "1995-08-20",
        "sex": "Female",
        "phone_number": "(541) 919-9216",
        "email": "alice.johnson@example.com",
        "address_line_1": "456 Oak Street",
        "city": "Portland",
        "state": "OR",
        "zip_code": "97202",
        "insurance_provider": "Kaiser",
        "insurance_member_id": "K12345",
        "preferred_language": "English"
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 201
    res = response.json()
    assert res["error"] is None
    patient = res["data"]
    assert patient["first_name"] == "Alice"
    assert patient["phone_number"] == "5419199216"  # normalized
    assert patient["patient_id"] is not None


def test_create_patient_validation_failure():
    # Future DOB and bad ZIP
    payload = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "date_of_birth": "2050-01-01",  # Invalid: future date
        "sex": "Female",
        "phone_number": "123",  # Invalid: not 10 digits
        "address_line_1": "456 Oak Street",
        "city": "Portland",
        "state": "INVALID_STATE",  # Invalid US state
        "zip_code": "ABC"  # Invalid zip code
    }
    response = client.post("/patients", json=payload)
    assert response.status_code == 422
    res = response.json()
    assert res["data"] is None
    assert "Validation failed" in res["error"]


def test_check_existing_patient():
    # Create patient first
    payload = {
        "first_name": "Bob",
        "last_name": "Marley",
        "date_of_birth": "1980-01-01",
        "sex": "Male",
        "phone_number": "5419199216",
        "address_line_1": "100 Jam Rock Way",
        "city": "Eugene",
        "state": "OR",
        "zip_code": "97401"
    }
    client.post("/patients", json=payload)

    # Check match with formatted phone number
    check_resp = client.get("/patients/check?phone_number=(541) 919-9216")
    assert check_resp.status_code == 200
    res = check_resp.json()
    assert res["error"] is None
    assert res["data"] is not None
    assert res["data"]["first_name"] == "Bob"

    # Check non-matching phone number
    no_match_resp = client.get("/patients/check?phone_number=5031112222")
    assert no_match_resp.status_code == 200
    res2 = no_match_resp.json()
    assert res2["error"] is None
    assert res2["data"] is None


def test_update_patient():
    payload = {
        "first_name": "Charlie",
        "last_name": "Brown",
        "date_of_birth": "1999-03-10",
        "sex": "Male",
        "phone_number": "5035559999",
        "address_line_1": "1 Peanuts Lane",
        "city": "Seattle",
        "state": "WA",
        "zip_code": "98101"
    }
    create_res = client.post("/patients", json=payload).json()
    patient_id = create_res["data"]["patient_id"]

    # Partial update
    update_payload = {
        "address_line_1": "2 Peanuts Blvd",
        "insurance_provider": "Medicare"
    }
    update_res = client.put(f"/patients/{patient_id}", json=update_payload)
    assert update_res.status_code == 200
    res = update_res.json()
    assert res["data"]["address_line_1"] == "2 Peanuts Blvd"
    assert res["data"]["insurance_provider"] == "Medicare"


def test_soft_delete_patient():
    payload = {
        "first_name": "David",
        "last_name": "Smith",
        "date_of_birth": "1975-06-15",
        "sex": "Male",
        "phone_number": "5035557777",
        "address_line_1": "55 Main St",
        "city": "Salem",
        "state": "OR",
        "zip_code": "97301"
    }
    create_res = client.post("/patients", json=payload).json()
    patient_id = create_res["data"]["patient_id"]

    # Delete patient
    del_res = client.delete(f"/patients/{patient_id}")
    assert del_res.status_code == 200
    assert del_res.json()["error"] is None

    # Get by ID should now return 404
    get_res = client.get(f"/patients/{patient_id}")
    assert get_res.status_code == 404
    assert get_res.json()["error"] == f"Patient with ID '{patient_id}' not found."

    # Check endpoint should also return data: null
    check_res = client.get("/patients/check?phone_number=5035557777")
    assert check_res.json()["data"] is None
