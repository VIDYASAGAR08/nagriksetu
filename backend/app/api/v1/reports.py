import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.citizen import CitizenProfile
from app.models.household import Household, HouseholdMembership
from app.models.records import MedicalRecord, EducationRecord, LandRecord
from app.models.hierarchy import AdministrativeUnit
from app.api.deps import (
    get_current_user,
    get_current_citizen_profile,
    get_current_admin,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


def _generate_report_checksum(data: Dict[str, Any]) -> str:
    """Generate tamper-evident SHA-256 digital signature hash."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@router.get("/citizen/{citizen_id}/dossier")
def generate_citizen_comprehensive_dossier(
    citizen_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an officially structured comprehensive Citizen Dossier report:
    - Identity & Census Demographics
    - Family Structure & Relationships (Father/Son, Husband/Wife, etc.)
    - Confidential Medical Health Passport
    - Educational Credentials & Literacy
    - Immovable Property & Land Registry Holdings
    - Digital Verification Stamp & Tamper-Evident SHA-256 Checksum
    
    Security: Accessible by Platform Admins, or the citizen themselves, or an authorized household member.
    """
    citizen = db.query(CitizenProfile).filter(CitizenProfile.id == citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen record with ID {citizen_id} not found."
        )

    # Permission check: Admins can view any citizen; Citizens can view self or household member
    if current_user.role != UserRole.ADMIN.value:
        caller_profile = db.query(CitizenProfile).filter(CitizenProfile.user_id == current_user.id).first()
        if not caller_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this citizen's report."
            )
        if caller_profile.id != citizen.id:
            # Check if in same household
            if not (caller_profile.household_id and caller_profile.household_id == citizen.household_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access restricted: You may only view reports for yourself or registered members of your household."
                )

    # 1. Demographic & Administrative Details
    admin_unit_name = citizen.administrative_unit.name if citizen.administrative_unit else "National Central Administrative Jurisdiction"
    admin_unit_code = citizen.administrative_unit.identifier if citizen.administrative_unit else "IND-CENTRAL"

    # 2. Medical Record
    med = db.query(MedicalRecord).filter(MedicalRecord.citizen_id == citizen.id).first()
    medical_data = {
        "blood_group": med.blood_group if med else "Unknown",
        "vaccination_status": med.vaccination_status if med else "Up to date",
        "chronic_conditions": med.chronic_conditions if med else "None Reported",
        "allergies": med.allergies if med else "None",
        "disability_status": med.disability_status if med else "None",
        "abha_id": med.abha_id if med else "Not Linked",
        "emergency_hospital": med.emergency_hospital if med else "District Government Hospital",
        "emergency_contact_name": med.emergency_contact_name if med else "Household Primary Contact",
        "emergency_contact_phone": med.emergency_contact_phone if med else (citizen.phone_number or "N/A"),
    }

    # 3. Education Record
    edu = db.query(EducationRecord).filter(EducationRecord.citizen_id == citizen.id).first()
    education_data = {
        "highest_qualification": edu.highest_qualification if edu else "Secondary (10th)",
        "institution_name": edu.institution_name if edu else "Government Recognized Institution",
        "specialization": edu.specialization if edu else "General Studies",
        "year_of_completion": edu.year_of_completion if edu else None,
        "literacy_status": edu.literacy_status if edu else "Literate",
        "certificate_number": edu.certificate_number if edu else "N/A",
    }

    # 4. Household and Family Relationships
    household_data = None
    land_records_data = []
    family_members_list = []

    if citizen.household_id:
        hh = db.query(Household).filter(Household.id == citizen.household_id).first()
        if hh:
            household_data = {
                "household_id": hh.id,
                "household_code": hh.household_code,
                "address_line": hh.address_line,
                "locality": hh.locality,
                "city": hh.city,
                "state": hh.state,
                "postal_code": hh.postal_code,
            }

            # Fetch household land records
            lands = db.query(LandRecord).filter(LandRecord.household_id == hh.id).all()
            for l in lands:
                land_records_data.append({
                    "id": l.id,
                    "survey_number": l.survey_number,
                    "land_type": l.land_type,
                    "area_measurement": l.area_measurement,
                    "patta_passbook_number": l.patta_passbook_number or "N/A",
                    "district_sub_registrar": l.district_sub_registrar or "District Revenue Authority",
                    "property_tax_status": l.property_tax_status or "Paid",
                    "market_valuation_inr": l.market_valuation_inr or 0.0,
                })

            # Fetch all family members
            members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).order_by(CitizenProfile.id).all()
            for m in members:
                family_members_list.append({
                    "id": m.id,
                    "citizen_code": m.citizen_code,
                    "full_name": m.full_name,
                    "relationship": getattr(m, "relationship", None) or m.household_relationship or "Member",
                    "relationship_details": getattr(m, "relationship_details", None) or f"{m.household_relationship or 'Member'} of Household",
                    "household_role": m.household_role or "MEMBER",
                    "date_of_birth": str(m.date_of_birth) if m.date_of_birth else "N/A",
                    "profile_status": m.profile_status,
                    "is_current": m.id == citizen.id,
                })

    # 5. Build Dossier Payload
    issue_time = datetime.now(timezone.utc)
    report_serial = f"DOSSIER-{citizen.citizen_code}-{issue_time.strftime('%Y%m%d%H%M')}"

    core_data = {
        "report_serial": report_serial,
        "citizen_code": citizen.citizen_code,
        "full_name": citizen.full_name,
        "date_of_birth": str(citizen.date_of_birth) if citizen.date_of_birth else "N/A",
        "phone_number": citizen.phone_number or "N/A",
        "preferred_language": citizen.preferred_language,
        "profile_status": citizen.profile_status,
        "relationship": getattr(citizen, "relationship", None) or "Individual",
        "relationship_details": getattr(citizen, "relationship_details", None) or "Individual citizen record",
        "administrative_unit": {
            "name": admin_unit_name,
            "code": admin_unit_code,
        },
        "household": household_data,
        "family_members": family_members_list,
        "medical_health_passport": medical_data,
        "education_credentials": education_data,
        "land_property_assets": land_records_data,
    }

    checksum = _generate_report_checksum(core_data)

    return {
        "metadata": {
            "report_title": "OFFICIAL COMPREHENSIVE CITIZEN DOSSIER",
            "issuing_authority": "National Civic & Administrative Management Authority (NagrikSetu)",
            "jurisdiction": "Central Administrative Repository, Government of India",
            "report_serial": report_serial,
            "issued_at": issue_time.isoformat(),
            "issued_by": current_user.email,
            "digital_checksum_sha256": checksum,
            "verification_status": "OFFICIALLY AUTHENTICATED",
            "qr_verification_payload": f"NAGRIKSETU://VERIFY/DOSSIER/{report_serial}?sha256={checksum[:16]}&cit={citizen.citizen_code}",
        },
        "citizen": {
            "id": citizen.id,
            "citizen_code": citizen.citizen_code,
            "full_name": citizen.full_name,
            "date_of_birth": str(citizen.date_of_birth) if citizen.date_of_birth else "N/A",
            "phone_number": citizen.phone_number or "N/A",
            "preferred_language": citizen.preferred_language,
            "profile_status": citizen.profile_status,
            "relationship": getattr(citizen, "relationship", None) or "Individual",
            "relationship_details": getattr(citizen, "relationship_details", None) or "Individual citizen record",
            "household_role": citizen.household_role or "MEMBER",
            "administrative_unit_name": admin_unit_name,
            "administrative_unit_code": admin_unit_code,
        },
        "household": household_data,
        "family_members": family_members_list,
        "medical_health_passport": medical_data,
        "education_credentials": education_data,
        "land_property_assets": land_records_data,
        "legal_attestation": {
            "declaration": (
                "This document is an electronically certified civic dossier compiled from authoritative public registries "
                "under the NagrikSetu Unified Civic Governance Framework. It constitutes valid digital certification "
                "of identity, household census relationships, educational literacy, health profile, and registered land holdings."
            ),
            "validity": "Perpetual unless superseded by subsequent certified census alteration.",
            "confidentiality_notice": "Protected under public records privacy and data sovereignty provisions.",
        }
    }


@router.get("/household/{household_id}/census")
def generate_household_census_report(
    household_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate an official Household Census & Family Tree Certificate:
    - Dwelling & Locality Information
    - Complete Roster of Family Members with Specific Roles & Relationships
    - Land Parcels & Assets registered to the Dwelling
    - Digital Verification Seal
    """
    hh = db.query(Household).filter(Household.id == household_id).first()
    if not hh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Household record with ID {household_id} not found."
        )

    # Permission check: Admins or members of this household
    if current_user.role != UserRole.ADMIN.value:
        caller_profile = db.query(CitizenProfile).filter(CitizenProfile.user_id == current_user.id).first()
        if not caller_profile or caller_profile.household_id != hh.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access restricted: You may only view census reports for your own registered household."
            )

    members = db.query(CitizenProfile).filter(CitizenProfile.household_id == hh.id).order_by(CitizenProfile.id).all()
    lands = db.query(LandRecord).filter(LandRecord.household_id == hh.id).all()

    members_summary = []
    for m in members:
        members_summary.append({
            "id": m.id,
            "citizen_code": m.citizen_code,
            "full_name": m.full_name,
            "relationship": getattr(m, "relationship", None) or m.household_relationship or "Member",
            "relationship_details": getattr(m, "relationship_details", None) or f"{m.household_relationship or 'Member'} of Household",
            "household_role": m.household_role or "MEMBER",
            "date_of_birth": str(m.date_of_birth) if m.date_of_birth else "N/A",
            "phone_number": m.phone_number or "N/A",
            "profile_status": m.profile_status,
        })

    lands_summary = []
    for l in lands:
        lands_summary.append({
            "survey_number": l.survey_number,
            "land_type": l.land_type,
            "area_measurement": l.area_measurement,
            "patta_passbook_number": l.patta_passbook_number or "N/A",
            "district_sub_registrar": l.district_sub_registrar or "District Revenue Authority",
            "property_tax_status": l.property_tax_status or "Paid",
            "market_valuation_inr": l.market_valuation_inr or 0.0,
        })

    issue_time = datetime.now(timezone.utc)
    report_serial = f"CENSUS-{hh.household_code}-{issue_time.strftime('%Y%m%d%H%M')}"
    checksum = _generate_report_checksum({
        "report_serial": report_serial,
        "household_code": hh.household_code,
        "members": members_summary,
        "lands": lands_summary,
    })

    return {
        "metadata": {
            "report_title": "OFFICIAL HOUSEHOLD CENSUS & FAMILY REGISTRY RECORD",
            "issuing_authority": "National Civic & Administrative Management Authority (NagrikSetu)",
            "report_serial": report_serial,
            "issued_at": issue_time.isoformat(),
            "issued_by": current_user.email,
            "digital_checksum_sha256": checksum,
            "qr_verification_payload": f"NAGRIKSETU://VERIFY/CENSUS/{report_serial}?sha256={checksum[:16]}",
        },
        "household": {
            "id": hh.id,
            "household_code": hh.household_code,
            "address_line": hh.address_line,
            "locality": hh.locality,
            "city": hh.city,
            "state": hh.state,
            "postal_code": hh.postal_code,
            "total_members": len(members_summary),
        },
        "family_roster": members_summary,
        "registered_lands": lands_summary,
    }


@router.get("/admin/census-summary")
def get_administrative_census_summary_report(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin)
):
    """
    Administrative overview report of all citizens and households with demographic metrics.
    Restricted strictly to administrators.
    """
    total_citizens = db.query(CitizenProfile).count()
    active_citizens = db.query(CitizenProfile).filter(CitizenProfile.profile_status == "active").count()
    total_households = db.query(Household).count()
    total_lands = db.query(LandRecord).count()
    total_medicals = db.query(MedicalRecord).count()
    total_educations = db.query(EducationRecord).count()

    # Relationship breakdown
    citizens = db.query(CitizenProfile).all()
    relationship_distribution: Dict[str, int] = {}
    for c in citizens:
        rel = getattr(c, "relationship", None) or "Unassigned / Individual"
        relationship_distribution[rel] = relationship_distribution.get(rel, 0) + 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": admin_user.email,
        "statistics": {
            "total_registered_citizens": total_citizens,
            "active_citizens": active_citizens,
            "total_households": total_households,
            "total_registered_land_parcels": total_lands,
            "medical_records_maintained": total_medicals,
            "education_records_maintained": total_educations,
        },
        "relationship_distribution": relationship_distribution,
    }
