from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ProjectAllocation
import time

# Send project allocation email to employee - Celery
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_allocation_email(self, employee_code, project_code):
    try:
        print(f"Starting email dispatch to {employee_code} for project {project_code}...")
        time.sleep(3)
        print(f"Email successfully sent to {employee_code}!")
        return f"Notification sent to {employee_code}"
    except Exception as exc:
        # Retry 3 times
        print(f"Failed to send to {employee_code}. Retrying in 5s... (Attempt {self.request.retries + 1}/3)")
        raise self.retry(exc=exc)


# scheduled to check project allocation expiry in every 1 hour - Celery
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def check_expiring_allocations(self):
    try:
        target_date = timezone.now().date() + timedelta(days=7)
        
        # Query allocations ending in exactly 7 days
        expiring = ProjectAllocation.objects.select_related('employee', 'project').filter(completed_date=target_date,is_active=True)
        
        print(f"[BEAT] Checking allocations for {target_date}... Found: {expiring.count()}")
        for alloc in expiring:
            print(f"ALERT: {alloc.employee.code}'s allocation on {alloc.project.code} ends in 7 days!")
            
        return f"Processed {expiring.count()} expiring allocations."
    except Exception as exc:
        # Retry 3 times
        print(f"Database check failed. Retrying... (Attempt {self.request.retries + 1}/3)")
        raise self.retry(exc=exc)


# scheduled to check project close status in every day midnight - Celery
@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def auto_close_expired_allocations(self):
    try:
        today = timezone.now().date()
        
        # Find allocations past their completion date that are still active
        expired_allocations = ProjectAllocation.objects.filter(completed_date__lt=today,status=ProjectAllocation.Status.IN_PROGRESS,is_active=True)
        count = expired_allocations.count()
        
        # Bulk update status
        expired_allocations.update(status=ProjectAllocation.Status.COMPLETED,is_active=False)
        
        print(f"[MIDNIGHT CRON] Auto-closed {count} expired allocations.")
        return f"Closed {count} allocations."
    except Exception as exc:
        print(f"Failed to close allocations. Retrying in 10s...")
        raise self.retry(exc=exc)