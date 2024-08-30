'''
    This file exist to give accept transfer transactions
'''
import requests
from django.conf import settings


PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
SECRET_KEY = settings.PAYSTACK_SECRET_KEY


header = {
    "Authorization": f"Bearer {SECRET_KEY}",
    "Content-Type": "application/json"
}


def process_bulk_transaction(bulk_data):
    '''
        this function processes bulk transactions for salary payment and random payments
        in bulk
    '''
    url = "https://api.paystack.co/transfer/bulk"

    data = {
        "currency": "NGN",
        "source": "balance",
        "transfers": bulk_data
    }

    response = requests.post(url, headers=header, json=data)
    print(response.json())
    #! should return a feedback after this have appended


'''
TRANSFERS
'''

def process_transaction(transaction_data):
    # generate the transaction id
    '''
        This function processes regular transactions and sends them to paystack API
    '''
    url = "https://api.paystack.co/transfer"

    data = {
        "source": "balance",
        "amount": transaction_data['amount'],
        "reference": transaction_data['reference'],
        "recipient": transaction_data['reciepient'],
        "reason": transaction_data['reason']
    }


    try:
        response = requests.post(url, json=data, headers=header)
        response_json = response.json()

        print(response_json)

    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred: {req_err}")