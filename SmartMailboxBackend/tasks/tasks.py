from celery import shared_task
import logging
from .services.reminder_service import ReminderService

logger = logging.getLogger(__name__)

@shared_task(name="tasks.run_reminder_sweep")
def run_reminder_sweep():
    """
    Periodic task to check for upcoming deadlines and send notifications.
    """
    logger.info("Starting periodic reminder sweep...")
    service = ReminderService()
    stats = service.run_reminder_check()
    logger.info(f"Reminder sweep complete: {stats}")
    return stats
