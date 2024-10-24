from celery import shared_task
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from .models import Email
import logging


logger = logging.getLogger(__name__)

@shared_task(bind=True)
def send_scheduled_email(self, email_id):
    try:
        email = Email.objects.get(id=email_id)
        send_mail(
            subject=email.subject,
            message=email.body,
            from_email=email.sender.email,
            recipient_list=[email.recipient.email],
            fail_silently=False,
        )
        logger.info(f"Sent email id {email_id}")
    except ObjectDoesNotExist:
        logger.error(f"Email id {email_id} does not exist")
    except Exception as exc:
        logger.exception(f"Error sending email id {email_id}: {str(exc)}")
        # Optionally retry the task in case of temporary issues
        # self.retry(exc=exc, max_retries=3, countdown=60)
