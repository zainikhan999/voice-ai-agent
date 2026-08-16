from contextlib import asynccontextmanager
from datetime import date
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import engine, Base, SessionLocal
from app.models import Patient, SexEnum
from app.routes import patients


def seed_database():
    """Inserts 2 realistic seed patient records if the database is currently empty."""
    db = SessionLocal()
    try:
        count = db.query(Patient).count()
        if count == 0:
            print("Database is empty. Seeding initial patient records...")
            seed_patients = [
                Patient(
                    patient_id="11111111-1111-4111-a111-111111111111",
                    first_name="John",
                    last_name="Smith",
                    date_of_birth=date(1985, 4, 12),
                    sex=SexEnum.MALE,
                    phone_number="5419199216",
                    email="john.smith@example.com",
                    address_line_1="742 Evergreen Terrace",
                    address_line_2="Suite 100",
                    city="Portland",
                    state="OR",
                    zip_code="97201",
                    insurance_provider="Aetna",
                    insurance_member_id="AET12345678",
                    preferred_language="English",
                    emergency_contact_name="Mary Smith",
                    emergency_contact_phone="5035550199"
                ),
                Patient(
                    patient_id="22222222-2222-4222-a222-222222222222",
                    first_name="Maria",
                    last_name="Garcia",
                    date_of_birth=date(1992, 11, 28),
                    sex=SexEnum.FEMALE,
                    phone_number="3055550143",
                    email="maria.garcia@example.com",
                    address_line_1="1200 Ocean Drive",
                    city="Miami",
                    state="FL",
                    zip_code="33139",
                    insurance_provider="Blue Cross Blue Shield",
                    insurance_member_id="BCBS98765432",
                    preferred_language="Spanish",
                    emergency_contact_name="Carlos Garcia",
                    emergency_contact_phone="3055550188"
                )
            ]
            db.add_all(seed_patients)
            db.commit()
            print("Seed patient records added successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    try:
        Base.metadata.create_all(bind=engine)
        seed_database()
    except Exception as err:
        print(f"Startup database initialization error: {err}")
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="Voice AI Patient Registration API",
    description="Backend REST API for Vapi Voice AI Agent patient registration",
    version="1.0.0",
    lifespan=lifespan
)

# Custom Exception Handlers to guarantee consistent response envelope
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": str(exc.detail)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        field_loc = " -> ".join([str(loc) for loc in error.get("loc", []) if loc != "body"])
        msg = error.get("msg", "Invalid input")
        if field_loc:
            error_messages.append(f"[{field_loc}]: {msg}")
        else:
            error_messages.append(msg)
    
    error_str = "Validation failed: " + "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"data": None, "error": error_str}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"data": None, "error": f"Internal server error: {str(exc)}"}
    )


app.include_router(patients.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"data": {"status": "healthy", "service": "Voice AI Patient Registration System"}, "error": None}
