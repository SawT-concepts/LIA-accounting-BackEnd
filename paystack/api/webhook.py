


import json
from django.http import HttpResponse
from paystack.service import verify_webhook_signature


def process_success_or_failed_payment_from_paystack_dva_process(request):
    if request.method == 'POST':
        if verify_webhook_signature(request):
            return HttpResponse(json.dumps({"status": "success"}), status=200, content_type="application/json")
        return HttpResponse(json.dumps({"status": "invalid signature"}), status=401, content_type="application/json")
    return HttpResponse(status=405)
