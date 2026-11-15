from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.event import AllocationApprovalEvent, EventIngestResponse
import redis.asyncio as aioredis
from app.core.redis import get_redis



router = APIRouter(prefix="/events", tags=["Events & Webhooks"])

@router.post("/allocation-approval", response_model=EventIngestResponse, status_code=status.HTTP_202_ACCEPTED, summary="Ingest Allocation Approval Webhook")
async def ingest_allocation_approval(payload: AllocationApprovalEvent, redis: aioredis.Redis = Depends(get_redis)):

    print(f"Received event {payload.event_id} for {payload.employee_code} on {payload.project_code} [{payload.status}]")
    event_key = f"event:idempotency:{payload.event_id}"

    #  NX=True (Only set if key does NOT exist), EX=600 (Expires in 10 minutes)
    is_new = await redis.set(event_key, "PROCESSING", nx=True, ex=600)
    # Duplicate Check
    if not is_new:
        return EventIngestResponse(success=True,message="Duplicate event detected. Already accepted.", event_id=payload.event_id)
    # Push to Redis queue for background execution
    await redis.lpush("erp_events_queue", payload.model_dump_json())
    return EventIngestResponse(success=True, message="Event accepted for processing", event_id=payload.event_id)
