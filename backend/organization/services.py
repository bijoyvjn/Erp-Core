import requests
import uuid
import logging

logger = logging.getLogger(__name__)

# Sends project allocation event - FastAPI microservice.
def notify_events_microservice(allocation):
    try:
        payload = {
            "event_id": str(uuid.uuid4()),
            "project_code": allocation.project.code,
            "employee_code": allocation.employee.code,
            "status": "APPROVED",
            "notes": "Triggered from Django ERP allocation API."
        }
        # Uses 'requests' library (plural) with Docker service name
        requests.post("http://events_service:8001/api/v1/events/allocation-approval", json=payload, timeout=1.0)

    except requests.exceptions.RequestException as e:
        logger.warning(f"Could not reach Events Microservice: {e}")