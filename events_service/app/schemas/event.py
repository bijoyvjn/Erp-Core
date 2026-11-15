from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from uuid import UUID


# 1. Python Enum for strict choices (Like TextChoices in Django Models)
class EventStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING = "PENDING"


# 2. input data schema - Pydantic Model (Replaces DRF Serializer)
class AllocationApprovalEvent(BaseModel):
    # Enforces Pydantic v2 configuration
    model_config = ConfigDict(extra="forbid")  # Rejects payload if unknown keys are passed

    event_id: UUID = Field(..., description="Unique event identifier")
    project_code: str = Field(..., min_length=2, max_length=50, example="PRJ-ALPHA")
    employee_code: str = Field(..., min_length=2, max_length=30, example="EMP-001")
    status: EventStatus = Field(default=EventStatus.PENDING)
    notes: str | None = Field(default=None, max_length=255)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# 3. Response Schema (What we return back to the caller)
class EventIngestResponse(BaseModel):
    success: bool
    message: str
    event_id: UUID
    received_at: datetime = Field(default_factory=datetime.utcnow)