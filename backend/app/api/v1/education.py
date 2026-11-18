"""
Education & School Service Integration Router for NagrikSetu
Federates requests between NagrikSetu Central Portal and the School Microservice (Port 8001).
Provides high-availability fallback to the local SQLite database.
"""

import os
import sqlite3
import httpx
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/education", tags=["Education & School Service"])

SCHOOL_SERVICE_URL = os.getenv("SCHOOL_SERVICE_URL", "http://school_backend:8000")
FALLBACK_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../School service/backend/data/nagriksetu.db")
)


def get_sqlite_fallback_conn():
    if os.path.exists(FALLBACK_DB_PATH):
        conn = sqlite3.connect(FALLBACK_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    # Also check container mount path
    container_path = "/app/school_data/nagriksetu.db"
    if os.path.exists(container_path):
        conn = sqlite3.connect(container_path)
        conn.row_factory = sqlite3.Row
        return conn
    return None


@router.get("/stats")
async def get_education_stats():
    """
    Returns aggregated metrics from the School & Education microservice.
    """
    # 1. Try remote microservice
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(f"{SCHOOL_SERVICE_URL}/schools?limit=100")
            if res.status_code == 200:
                schools = res.json()
                districts = set(s.get("district") for s in schools if s.get("district"))
                return {
                    "status": "online",
                    "total_schools": len(schools),
                    "districts_covered": len(districts),
                    "portal_url": "http://localhost:5174",
                    "schemes": [
                        "National Scholarship Portal (NSP)",
                        "DigiLocker Marksheets & Certificates",
                        "Pre/Post-Matric Grants for Minority & Rural Students",
                        "RTE Admission Portal & Degree Verification"
                    ],
                    "integration_mode": "microservice_live"
                }
    except Exception:
        pass

    # 2. Local database fallback
    conn = get_sqlite_fallback_conn()
    if conn:
        try:
            total = conn.execute("SELECT count(*) FROM schools").fetchone()[0]
            districts_count = conn.execute("SELECT count(DISTINCT district) FROM schools").fetchone()[0]
            conn.close()
            return {
                "status": "online",
                "total_schools": total,
                "districts_covered": districts_count,
                "portal_url": "http://localhost:5174",
                "schemes": [
                    "National Scholarship Portal (NSP)",
                    "DigiLocker Marksheets & Certificates",
                    "Pre/Post-Matric Grants for Minority & Rural Students",
                    "RTE Admission Portal & Degree Verification"
                ],
                "integration_mode": "database_fallback"
            }
        except Exception:
            pass

    return {
        "status": "online",
        "total_schools": 10,
        "districts_covered": 5,
        "portal_url": "http://localhost:5174",
        "schemes": [
            "National Scholarship Portal (NSP)",
            "DigiLocker Marksheets & Certificates",
            "Pre/Post-Matric Grants for Minority & Rural Students",
            "RTE Admission Portal & Degree Verification"
        ],
        "integration_mode": "static_manifest"
    }


@router.get("/schools")
async def list_education_schools(
    q: Optional[str] = Query(None, description="Search by school name or keyword"),
    district: Optional[str] = Query(None, description="Filter by district"),
    state: Optional[str] = Query(None, description="Filter by state"),
    limit: int = Query(50, ge=1, le=100),
):
    """
    Search and retrieve public school directory records federated from School Microservice.
    """
    # 1. Try microservice API
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            target_url = f"{SCHOOL_SERVICE_URL}/schools?limit={limit}"
            res = await client.get(target_url)
            if res.status_code == 200:
                schools = res.json()
                if q:
                    query_lower = q.lower()
                    schools = [s for s in schools if query_lower in s.get("school_name", "").lower() or query_lower in s.get("district", "").lower()]
                if district and district != "ALL":
                    schools = [s for s in schools if s.get("district", "").lower() == district.lower()]
                if state and state != "ALL":
                    schools = [s for s in schools if s.get("state", "").lower() == state.lower()]
                return {
                    "total": len(schools),
                    "items": schools,
                    "source": "school_microservice_api"
                }
    except Exception:
        pass

    # 2. Try direct database fallback
    conn = get_sqlite_fallback_conn()
    if conn:
        try:
            sql = "SELECT school_id, school_name, district, state, school_type, address, established_year, description, public_phone, website, facilities_json FROM schools WHERE 1=1"
            params = []
            if q:
                sql += " AND (school_name LIKE ? OR district LIKE ?)"
                params.extend([f"%{q}%", f"%{q}%"])
            if district and district != "ALL":
                sql += " AND district = ?"
                params.append(district)
            if state and state != "ALL":
                sql += " AND state = ?"
                params.append(state)
            sql += f" LIMIT {limit}"

            rows = conn.execute(sql, params).fetchall()
            schools = []
            for r in rows:
                s_dict = dict(r)
                # Parse facilities_json if string
                if isinstance(s_dict.get("facilities_json"), str):
                    try:
                        import json
                        s_dict["facilities"] = json.loads(s_dict["facilities_json"])
                    except Exception:
                        s_dict["facilities"] = []
                schools.append(s_dict)
            conn.close()
            return {
                "total": len(schools),
                "items": schools,
                "source": "school_database_direct"
            }
        except Exception:
            pass

    return {
        "total": 0,
        "items": [],
        "source": "empty"
    }


@router.get("/schools/{school_id}")
async def get_school_detail(school_id: str):
    """
    Get detailed profile of a specific school including programs and contacts.
    """
    # 1. Try microservice API
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            res = await client.get(f"{SCHOOL_SERVICE_URL}/schools/{school_id}")
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass

    # 2. Database fallback
    conn = get_sqlite_fallback_conn()
    if conn:
        try:
            row = conn.execute("SELECT * FROM schools WHERE school_id = ?", [school_id]).fetchone()
            if row:
                res = dict(row)
                conn.close()
                return res
            conn.close()
        except Exception:
            pass

    raise HTTPException(status_code=404, detail=f"School with ID {school_id} not found.")
