"""
Skill Development Service Integration Router for NagrikSetu
Federates requests between NagrikSetu Central Portal and the Skill Development Microservice (Port 8003).
Provides aggregated stats, program discovery, and unified citizen skill credential verification.
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/skills", tags=["Skill Development Service Federation"])

SKILL_SERVICE_URL = os.getenv("SKILL_SERVICE_URL", "http://skill_backend:8000")
FALLBACK_LOCAL_URL = "http://localhost:8003"


async def fetch_from_skill_service(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Helper to query the skill development microservice with timeout and fallback."""
    urls_to_try = [SKILL_SERVICE_URL, FALLBACK_LOCAL_URL]
    for base in urls_to_try:
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                res = await client.get(f"{base}{endpoint}", params=params)
                if res.status_code == 200:
                    return res.json()
        except Exception:
            continue
    return None


@router.get("/stats")
async def get_skill_service_stats():
    """
    Returns live aggregated metrics federated from the Skill Development microservice (MySQL 8.4).
    """
    data = await fetch_from_skill_service("/health")
    programmes = await fetch_from_skill_service("/api/programmes")
    centres = await fetch_from_skill_service("/api/centres")

    total_progs = len(programmes) if isinstance(programmes, list) else 6
    total_centres = len(centres) if isinstance(centres, list) else 8

    return {
        "status": "online" if data else "degraded",
        "service": "nagriksetu-skill-development",
        "portal_url": "http://localhost:5175",
        "total_programmes": total_progs,
        "training_centres": total_centres,
        "database": "MySQL 8.4 LTS",
        "schemes": [
            "Pradhan Mantri Kaushal Vikas Yojana (PMKVY 4.0)",
            "National Apprenticeship Promotion Scheme (NAPS)",
            "Craftsmen Training Scheme (ITI Technical)",
            "FutureSkills PRIME AI & Cloud Skilling Initiative"
        ],
        "integration_mode": "federated_rest_live" if data else "fallback_manifest"
    }


@router.get("/programmes")
async def discover_programmes(
    q: Optional[str] = Query(None, description="Search keyword"),
    mode: Optional[str] = Query(None, description="Offline, Online, or Hybrid")
):
    """
    Federated query endpoint allowing Central Portal citizens to discover vocational skill programmes.
    """
    params = {}
    if q:
        params["q"] = q
    if mode:
        params["mode"] = mode

    data = await fetch_from_skill_service("/api/programmes", params=params)
    if data is not None:
        return data

    # Static fallback if service is starting up
    return [
        {
            "id": 1,
            "title": "Government Accelerated Python Cloud Services Programme",
            "mode": "Hybrid",
            "duration_hours": 60,
            "fee": 0.0,
            "scholarship_available": True
        },
        {
            "id": 2,
            "title": "Industrial Electrician & Solar PV Installation",
            "mode": "Offline",
            "duration_hours": 120,
            "fee": 0.0,
            "scholarship_available": True
        }
    ]


@router.get("/verify-certificate/{code}")
async def verify_certificate_credential(code: str):
    """
    Federated public credential verification bridging Central verification requests
    directly to the Skill Development microservice's tamper-evident certificate records.
    """
    data = await fetch_from_skill_service(f"/api/certificates/verify/{code}")
    if data:
        return data
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Certificate code '{code}' could not be verified on the federated credential registry."
    )
