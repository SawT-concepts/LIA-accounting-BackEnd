'''
    This file exist to give the paystack api support for other complex API
'''
import hashlib
import hmac
import requests
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from background_tasks.tasks import handle_webhook_event_in_celery
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging

from sps_core.models import Student

logger = logging.getLogger(__name__)
PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
SECRET_KEY = settings.PAYSTACK_SECRET_KEY


def get_banks_from_paystack():
    '''
        this function fetches the list of all the banks from paystack database
    '''
    url = "https://api.paystack.co/bank"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    return response.json()["data"]


def resolve_bank_account(account_number, bank_code):
    '''
        Verifies a user's bank account
    '''
    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print (response.json()['data'])
        return response.json()
    else:
        return None




def generate_paystack_id(instance, full_name_present=None):
    '''
    Generate paystack_id_for_staff after verifying the account name and bank.
    '''

    url = "https://api.paystack.co/transferrecipient"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "type": instance.bank.bank_type,
        "name": f"{instance.name_of_receiver}" if full_name_present else f"{instance.first_name} {instance.last_name}",
        "account_number": instance.account_number_of_receiver if full_name_present else instance.account_number,
        "bank_code": instance.bank.bank_code,
        "currency": instance.bank.currency
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response_json = response.json()

        if response_json["status"]:
            payload = {'status': 200, 'data': response_json['data']["recipient_code"]}
        else:
            print(response_json)
            payload = {'status': 200, 'data': response_json["message"]}

        return payload

    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")

    # Return None or an appropriate message if an exception occurstfggf
    return None


def verify_payment (transaction_refrence, customer_id):
    url = f"https://api.paystack.co/transfer/verify/{transaction_refrence}"  # Replace with your actual reference

    headers = {
        "Authorization": f"Bearer {SECRET_KEY}"
    }
    try:
        response = requests.get(url, headers=headers)
        response_json = response.json()

        print(response_json)

    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")



def create_paystack_structure(batch):
    """
    Create paystack transfer objects for each staff in a batch.

    Parameters:
    - batch: List representing a batch of staff.

    Returns:
    List of paystack transfer objects.
    """
    data = []
    for single_batch_instance in batch:
        paystack_transfer_object = {
            "amount": single_batch_instance['salary_recieved'],
            "reference": single_batch_instance['transaction_refrence'],
            "reason": "Salary Payment",
            "recipient": single_batch_instance['recipient_code']
        }
        data.append(paystack_transfer_object)

    return data



def verify_customer_and_create_a_digital_virtual_account(customer_details: dict) -> bool:
    '''
        This function verifies a customer and creates a digital virtual account for them
    '''
    url = "https://api.paystack.co/dedicated_account/assign"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": customer_details['email'],
        "first_name": customer_details['first_name'],
        "last_name": customer_details['last_name'],
        "phone": customer_details['phone'],
        "preferred_bank": customer_details['preferred_bank'],
        "country": "NG",
        "account_number": "0123456789",
        "bvn": "20012345678",
        "bank_code": "007"
    }

    response = requests.post(url, headers=headers, json=data)

    return True if response.status_code == 200 else False


def get_all_dedicated_accounts():
    '''
        This function gets all the dedicated accounts
    '''
    url = "https://api.paystack.co/dedicated_account"
    headers = {
        "Authorization": f"Bearer {SECRET_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    print(response.status_code)
    print(response.json())


def verify_webhook_signature(request):
    '''
        This function verifies the webhook signature
    '''
    paystack_signature = request.headers.get('x-paystack-signature')
    hash = hmac.new(
        SECRET_KEY.encode('utf-8'),
        request.data,
        hashlib.sha512
    ).hexdigest()
    if hash == paystack_signature:
        handle_webhook_event_in_celery.delay(request)
        return True
    return False



def handle_webhook_event(request):
    '''
    This function handles the webhook event for dedicated account assignment.
    '''
    from paystack.models import DedicatedAccount
    try:
        data = request.data
        event_type = data.get('event')

        if event_type == 'dedicatedaccount.assign.success' and 'data' in data:
            account_data = data['data'].get('dedicated_account')
            student = Student.objects.get(parent_email=account_data.get('email'))
            if not account_data:
                raise ValueError("Invalid data in the webhook payload")

            with transaction.atomic():
                DedicatedAccount.objects.create(
                    student=student,
                    account_number=account_data.get('account_number'),
                    account_name=account_data.get('account_name'),
                    account_type=account_data.get('account_type'),
                    bank_code=account_data.get('bank_code'),
                    bank_name=account_data.get('bank_name')
                )

            user_group_name = f"virtual_account_paystack_updates_{student.id}"

            # Notify via channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'virtual_account_paystack_update',
                    'message': 'Account created successfully',
                    'data': account_data
                }
            )

        elif event_type == 'dedicatedaccount.assign.failed' and 'data' in data:
            account_data = data['data'].get('dedicated_account')
            student = Student.objects.get(parent_email=account_data.get('email'))
            if not account_data:
                raise ValueError("Invalid data in the webhook payload")

            user_group_name = f"virtual_account_paystack_updates_{student.id}"

            # Notify via channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'virtual_account_paystack_update',
                    'message': 'Failed to create dedicated account',
                    'data': account_data
                }
            )
        else:
            logger.info("Invalid event type")
    except ObjectDoesNotExist as e:
        logger.error(f"Student with id does not exist: {e}")
    except Exception as e:
        logger.error(f"Error handling webhook event: {e}")
