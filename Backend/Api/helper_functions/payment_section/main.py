from ast import Dict
from django.shortcuts import get_object_or_404
from Main.models.fees_structure_models import PaymentStatus
from Main.models.school_operations_models import Class, Student
from django.db.models import Sum
from collections import Counter

def get_student_id_from_request (payload):
    student = get_object_or_404(Student, student_id=payload)
    return student


def get_total_amount_in_debt(students):
    '''This function iterates through all the students and calculates the total amount of debt. It caches the result.'''
    
    total_amount_query = PaymentStatus.objects.filter(student__in=students).aggregate(
        total_amount=Sum('amount_in_debt') + Sum('amount_outstanding')
    )

    # Extract the total amount from the aggregation result
    total_amount = total_amount_query['total_amount'] or 0

    return total_amount


def get_payment_summary(students):
    '''This function summarizes the payment status of students and returns counts and percentages.'''
    
    # Use Counter to initialize counts for different payment statuses
    status_counts = Counter()

    for student in students:
        payment_status = PaymentStatus.objects.get(student=student.id)
        
        # Increment the corresponding count based on payment status
        status_counts[payment_status.status] += 1
        

    # Extract counts for each status
    student_paid = status_counts["COMPLETED"]
    student_in_debt = status_counts["IN DEBT"]
    student_outstanding = status_counts["OUTSTANDING"]

    # Calculate percentages
    total_students = len(students)
    percentage_paid = (student_paid / total_students) * 100 if total_students > 0 else 0
    percentage_in_debt = (student_in_debt / total_students) * 100 if total_students > 0 else 0
    percentage_outstanding = (student_outstanding / total_students) * 100 if total_students > 0 else 0

    summary = {
        'student_paid': student_paid,
        'percentage_paid': percentage_paid,
        'student_in_debt': student_in_debt,
        'percentage_in_debt': percentage_in_debt,
        'student_outstanding': student_outstanding,
        'percentage_outstanding': percentage_outstanding,
    }

    return summary


def generate_grade_summary(school):
    """
    Generates a summary for a bar chart showing the amount paid for each grade.
    """

    grades = Class.objects.filter(school=school).only('name', 'amount_paid')

    result = [{"name": grade.name, "amount_paid": grade.amount_paid} for grade in grades]

    return result
