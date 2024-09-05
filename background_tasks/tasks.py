from celery import shared_task



@shared_task
def handle_webhook_event_in_celery(request):
    from paystack.service import handle_webhook_event
    handle_webhook_event(request)
