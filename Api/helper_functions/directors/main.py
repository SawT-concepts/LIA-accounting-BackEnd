from Main.models import Payroll
from Paystack.transfers import process_bulk_transaction
import json
import time

BATCH_SIZE = 100


'''
SALARY PAYMENT
'''

def process_salary_payment(payroll_id):
    """
    Process salary payment for a given payroll.

    Parameters:
    - payroll_id: The ID of the payroll to process.
    """
    payroll_instance = Payroll.objects.get(id=payroll_id)

    # Convert staffs JSONField to a list
    payroll_staffs = json.loads(payroll_instance.staffs) if payroll_instance.staffs else []

    num_batches = (len(payroll_staffs) + BATCH_SIZE - 1) // BATCH_SIZE

    # Create and return batches
    batches = [payroll_staffs[i * BATCH_SIZE:(i + 1) * BATCH_SIZE] for i in range(num_batches)]
    process_salary_by_batch(batches)


def process_salary_by_batch(batch_list):
    """
    Process salary for each batch in the provided list.

    Parameters:
    - batch_list: List of batches to process.
    """
    for batch in batch_list:
        batch_object = create_paystack_structure(batch)
        #send the batch_object to paystack processor
        process_bulk_transaction(batch_object)
        time.sleep(0.5)



def create_paystack_structure(batch):
    """
    Create Paystack transfer objects for each staff in a batch.

    Parameters:
    - batch: List representing a batch of staff.

    Returns:
    List of Paystack transfer objects.
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


def convert_to_double_quoted_string(data):
    """
    Convert data to a double-quoted JSON-formatted string.

    Parameters:
    - data: Data to convert.

    Returns:
    Double-quoted JSON-formatted string.
    """
    return json.dumps(data)




