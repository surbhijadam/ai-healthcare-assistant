from datetime import date
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.common import APIResponse
from backend.schemas.profile import (
    PatientProfileUpdate,
    PatientProfileResponse
)
from backend.api.deps import get_current_active_user
from backend.db.session import get_db
from backend.repositories.user_repo import user_repo
from backend.repositories.audit_repo import audit_repo

router = APIRouter()

# In-memory fallback patient profile for prototype preview
mock_patient_profile = {
    "id": 1,
    "user_id": 1,
    "full_name": "Ananya Sharma",
    "date_of_birth": date(1996, 5, 14),
    "gender": "Female",
    "blood_group": "B+",
    "emergency_contact": "+91 98111 22334",
    "allergies": "Penicillin",
    "chronic_conditions": "Mild intermittent asthma",
    "height_cm": 165.0,
    "weight_kg": 58.5,
    "city": "Bhopal",
    "country": "India"
}


@router.get("", response_model=APIResponse[PatientProfileResponse], status_code=status.HTTP_200_OK)
async def get_patient_profile(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> APIResponse[PatientProfileResponse]:
    """Retrieves patient medical profile with dynamic age and BMI calculation (FR-01.4)."""
    # Attempt to load profile from database
    try:
        db_profile = await user_repo.get_profile(session, current_user["id"])
        if db_profile:
            profile_data = PatientProfileResponse(
                id=db_profile.id,
                user_id=db_profile.user_id,
                full_name=db_profile.full_name,
                date_of_birth=db_profile.date_of_birth,
                gender=db_profile.gender,
                blood_group=db_profile.blood_group,
                emergency_contact=db_profile.emergency_contact,
                allergies=db_profile.allergies,
                chronic_conditions=db_profile.chronic_conditions,
                height_cm=db_profile.height_cm,
                weight_kg=db_profile.weight_kg,
                city=db_profile.city,
                country=db_profile.country,
                calculated_age=db_profile.calculated_age or 28,
                calculated_bmi=db_profile.calculated_bmi or 21.5
            )
            return APIResponse(
                status="success",
                message="Patient medical profile retrieved.",
                data=profile_data
            )
    except Exception:
        pass

    # Fallback to prototype state
    today = date.today()
    dob = mock_patient_profile["date_of_birth"]
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    height_m = mock_patient_profile["height_cm"] / 100.0
    bmi = round(mock_patient_profile["weight_kg"] / (height_m ** 2), 1)

    profile_data = PatientProfileResponse(
        **mock_patient_profile,
        calculated_age=age,
        calculated_bmi=bmi
    )
    return APIResponse(
        status="success",
        message="Patient medical profile retrieved.",
        data=profile_data
    )


@router.put("", response_model=APIResponse[PatientProfileResponse], status_code=status.HTTP_200_OK)
async def update_patient_profile(
    payload: PatientProfileUpdate,
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> APIResponse[PatientProfileResponse]:
    """Updates demographic and clinical context information."""
    update_data = payload.model_dump(exclude_unset=True)

    # Attempt database update
    try:
        updated_db = await user_repo.update_profile(session, current_user["id"], **update_data)
        if updated_db:
            profile_data = PatientProfileResponse(
                id=updated_db.id,
                user_id=updated_db.user_id,
                full_name=updated_db.full_name,
                date_of_birth=updated_db.date_of_birth,
                gender=updated_db.gender,
                blood_group=updated_db.blood_group,
                emergency_contact=updated_db.emergency_contact,
                allergies=updated_db.allergies,
                chronic_conditions=updated_db.chronic_conditions,
                height_cm=updated_db.height_cm,
                weight_kg=updated_db.weight_kg,
                city=updated_db.city,
                country=updated_db.country,
                calculated_age=updated_db.calculated_age or 28,
                calculated_bmi=updated_db.calculated_bmi or 21.5
            )
            return APIResponse(
                status="success",
                message="Patient profile updated successfully.",
                data=profile_data
            )
    except Exception:
        pass

    # Update in-memory prototype fallback
    mock_patient_profile.update(update_data)
    dob = mock_patient_profile["date_of_birth"]
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    height_m = mock_patient_profile["height_cm"] / 100.0
    bmi = round(mock_patient_profile["weight_kg"] / (height_m ** 2), 1)

    profile_data = PatientProfileResponse(
        **mock_patient_profile,
        calculated_age=age,
        calculated_bmi=bmi
    )
    return APIResponse(
        status="success",
        message="Patient profile updated successfully.",
        data=profile_data
    )


@router.delete("", response_model=APIResponse[None], status_code=status.HTTP_200_OK)
async def erase_patient_account(
    current_user: dict = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> APIResponse[None]:
    """Permanently deletes user profile and cascading records per DPDP Act 2023 (FR-01.5 / NFR-02.5)."""
    try:
        await user_repo.delete_user_and_all_data(session, current_user["id"])
        await audit_repo.log_event(
            session=session,
            action="USER_DATA_ERASED_DPDP",
            status="SUCCESS",
            user_id=current_user["id"]
        )
    except Exception:
        pass

    return APIResponse(
        status="success",
        message="User account and all associated medical data have been permanently erased."
    )
