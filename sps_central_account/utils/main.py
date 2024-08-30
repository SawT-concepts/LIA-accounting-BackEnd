from typing import List, Dict, Union
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from collections import Counter
from sps_core.models import Grade, School, Student

from sps_fees_payment_structure.models.fees_history_and_status_models import PaymentStatus




def get_total_amount_in_debt(students: List[Student]) -> int:
    '''This function iterates through all the students and calculates the total amount of debt. It caches the result.'''

    total_amount_query = PaymentStatus.objects.filter(student__in=students).aggregate(
        total_amount=Sum('amount_in_debt') + Sum('amount_outstanding')
    )

    # Extract the total amount from the aggregation result
    total_amount: int = total_amount_query['total_amount'] or 0

    return total_amount


def get_payment_summary(students: List[Student]) -> Dict[str, Union[int, float]]:
    '''This function summarizes the payment status of students and returns counts and percentages.'''

    # Use Counter to initialize counts for different payment statuses
    status_counts: Counter = Counter()

    for student in students:
        payment_status = PaymentStatus.objects.get(student=student.id)


        status_counts[payment_status.status] += 1


    # Extract counts for each status
    student_paid: int = status_counts["COMPLETED"]
    student_in_debt: int = status_counts["IN DEBT"]
    student_outstanding: int = status_counts["OUTSTANDING"]

    # Calculate percentages
    total_students: int = len(students)
    percentage_paid: float = (student_paid / total_students) * 100 if total_students > 0 else 0
    percentage_in_debt: float = (student_in_debt / total_students) * 100 if total_students > 0 else 0
    percentage_outstanding: float = (student_outstanding / total_students) * 100 if total_students > 0 else 0

    summary: Dict[str, Union[int, float]] = {
        'student_paid': student_paid,
        'percentage_paid': percentage_paid,
        'student_in_debt': student_in_debt,
        'percentage_in_debt': percentage_in_debt,
        'student_outstanding': student_outstanding,
        'percentage_outstanding': percentage_outstanding,
    }

    return summary


def generate_grade_summary(school: School) -> List[Dict[str, Union[str, int]]]:
    """
    Generates a summary for a bar chart showing the amount paid for each grade.
    """

    grades: List[Grade] = Grade.objects.filter(school=school).only('name', 'amount_paid')

    result: List[Dict[str, Union[str, int]]] = [{"name": grade.name, "amount_paid": grade.amount_paid} for grade in grades]

    return result
