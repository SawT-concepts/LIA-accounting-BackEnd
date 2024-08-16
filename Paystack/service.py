'''
    This file exist to give the paystack api support for other complex API
'''
import requests
from django.conf import settings


PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
SECRET_KEY = settings.PAYSTACK_SECRET_KEY


def get_banks_from_paystack():
    '''
        this function fetches the list of all the banks from Paystack database
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
        "name": f"{instance.name_of_reciever}" if full_name_present else f"{instance.first_name} {instance.last_name}",
        "account_number": instance.account_number_of_reciever if full_name_present else instance.account_number,
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