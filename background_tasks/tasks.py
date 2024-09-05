from celery import shared_task
from paystack.service import handle_webhook_event


@shared_task
def handle_webhook_event_in_celery(request):
    handle_webhook_event(request)
