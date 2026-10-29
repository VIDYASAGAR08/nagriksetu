from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class AdministrativeUnitCreate(BaseModel):
    identifier: str = Field(..., min_length=2, max_length=50, description="Unique code e.g. IN-KA-BLR-01")
    name: str = Field(..., min_length=2, max_length=150, description="Official name e.g. Bengaluru Urban")
    unit_type: str = Field(..., description="country, state, district, sub_district, ward, or village")
    parent_id: Optional[int] = Field(None, description="Parent unit ID in the hierarchy")
    status: str = Field("active", description="active or inactive")


class AdministrativeUnitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    parent_id: Optional[int] = None
    status: Optional[str] = Field(None, description="active or inactive")


class AdministrativeUnitResponse(BaseModel):
    id: int
    identifier: str
    name: str
    unit_type: str
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None
    parent_identifier: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    children_count: int = 0
    citizens_count: int = 0
    households_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AdministrativeUnitListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[AdministrativeUnitResponse]
