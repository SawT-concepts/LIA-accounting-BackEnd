from django.db import transaction
from django.shortcuts import get_object_or_404
from typing import List, Dict
from paystack.transfers import process_bulk_transaction
import json
import time

from paystack.service import create_paystack_structure
from sps_core.models import Grade, School, Student
from sps_operations_account.models.operations_payment_models import Payroll


def promote_students(school: School, demoted_students: List[Student]) -> Dict[str, str]:
    try:
        with transaction.atomic():
            students: List[Student] = Student.objects.filter(school=school)

            for student in students:
                if student in demoted_students:
                    continue  # Skip demoted students

                current_grade: Grade = student.grade
                next_class_to_be_promoted_to: Grade = current_grade.next_class_to_be_promoted_to

                # Update the student's grade
                student.grade = next_class_to_be_promoted_to
                student.save()

            # Transaction successful, commit changes
            return {"message": "Promotion successful"}
    except Exception as e:
        # Handle exceptions and provide details in the response
        return {"message": f"An error occurred during promotion: {str(e)}"}


def get_student_id_from_request(payload: str) -> Student:
    student = get_object_or_404(Student, student_id=payload)
    return student

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


def convert_to_double_quoted_string(data):
    """
    Convert data to a double-quoted JSON-formatted string.

    Parameters:
    - data: Data to convert.

    Returns:
    Double-quoted JSON-formatted string.
    """
    return json.dumps(data)
