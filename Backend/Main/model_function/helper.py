from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
import random
import string


def generate_taxroll_staff_table_out_of_payroll(staffs_on_payroll):
    taxroll_staffs = []
    Staff = apps.get_model('Main', 'Staff')
    for staff_data in staffs_on_payroll:
        try:
            staff_object = Staff.objects.get(id=staff_data['staff_id'])
            annual_income = staff_data['basic_salary'] * 12

            taxroll_staff = {
                "staff_name": staff_data.get('staff_firstname') + " " + staff_data.get('staff_lastname'),
                "staff_id": staff_data.get('staff_id'),
                "rank": staff_data.get('rank'),
                "tax_payable": staff_data.get('tax'),
                "basic_salary": staff_data.get('basic_salary'),
                "Annual_Income": annual_income,
                "TIN": staff_object.tin_number,
                # Use provided account_number or None
                "account_number": staff_data.get('account_number'),
                "bank": staff_data.get('bank'),  # Use provided bank or None
                "account_name": staff_data.get('account_name'),
            }

            taxroll_staffs.append(taxroll_staff)
        except ObjectDoesNotExist:
            # Handle the case where the staff with the specified staff_id does not exist
            pass

    return taxroll_staffs


def generate_transaction_reference(length=10):
    """Generate a random transaction reference with the specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_staffroll(school_name):
    '''
        Function to generate a list of staffs to be paid
    '''
    staff_payroll = []
    Staff = apps.get_model('Main', 'Staff')
    staffs = Staff.objects.select_related("staff_type").filter(
        school=school_name, is_active=True)
    transaction_reference = generate_transaction_reference()

    for staff in staffs:

        # GENERATE refrence number here
        try:
            staff_payroll.append({
                "staff_firstname": staff.first_name,
                "staff_lastname": staff.last_name,
                "staff_phonenumber": staff.phone_number,
                "staff_id": staff.id,
                "transaction_refrence": transaction_reference,
                "rank": staff.staff_type.name,
                "recipient_code": staff.paystack_id,
                "tax_payable": staff.staff_type.tax,
                "basic_salary": staff.staff_type.basic_salary,
                "Annual_Income": staff.staff_type.basic_salary * 12,
                "school": staff.school.name,
                "salary_deduction": staff.salary_deduction,
                "salary_recieved": (staff.staff_type.basic_salary - staff.staff_type.tax - staff.salary_deduction),
                "TIN": staff.tin_number,
                "account_number": staff.account_number,
                "bank": staff.bank.name,
            })
        except ObjectDoesNotExist:
            # Handle the case where the staff with the specified staff_id does not exist
            pass

    return staff_payroll
