from Main.models import *
from Authentication.models import CustomUser
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from Authentication.models import CustomUser
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.status import *
from rest_framework.exceptions import PermissionDenied
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from django.db.models import Sum
from enum import Enum
from Paystack.models import Bank


def check_account_type(user, account_type):
    '''
        This api is used to check if the correct user role is accessing the API. if its not the user
        then it should raise a PermissionDenied exception
    '''
    def get_user_type(user, account_type):
        user_model = get_user_model()
        user = user_model.objects.get(id=user.id)

        if user.account_type != account_type:
            raise PermissionDenied()  # Raise an exception if unauthorized

    get_user_type(user, account_type)  # Call the inner function


def get_school_from_user(user_id):
    """
    Retrieves the school ID associated with a user.

    Parameters:
        user_id (int): The identifier of the user.

    Returns:
        int or None: The school ID associated with the user. If the user is not found or
                     does not have an associated school, returns None.
    """
    try:
        custom_user = get_object_or_404(CustomUser, id=user_id)
        user_school = custom_user.school
        return user_school.id
    except CustomUser.DoesNotExist:
        # Handle the case where the user does not exist
        return None


def get_unarranged_transaction_six_months_ago(school_id):
    """
    Retrieves a list of successful debit transactions that occurred within the last
    six months for a specified school. The records are unarranged and include details such
    as transaction time, amount, and transaction type.

    Parameters:
        school_id (int): The identifier of the school for which transaction records are retrieved.

    Returns:
        list or None: A list of dictionaries representing unarranged debit transaction records
                      within the last six months. Each dictionary contains details such as:
                      - 'time': The timestamp of the transaction.
                      - 'amount': The amount involved in the transaction.
                      - 'transaction_type': The type of the transaction.
                  If no records are found, returns None.
    """
    try:
        current_date = datetime.now()
        print(current_date)
        six_months_ago = current_date - relativedelta(months=6)
        print(six_months_ago)

        # Use the model class directly to filter records
        transaction_records = Operations_account_transaction_record.get_transaction(
            start_date=six_months_ago,
            end_date=current_date,
            school=school_id
        ).filter(status="SUCCESS", transaction_category="DEBIT")

        transaction_records_list = [
            {
                "time": record.time,
                "amount": record.amount,
                "transaction_type": record.transaction_type
            }

            for record in transaction_records
        ]

        return transaction_records_list

    except Operations_account_transaction_record.DoesNotExist:
        return None


def get_unarranged_transaction_seven_days_ago(school_id):
    """
    Retrieves a list of successful transaction records that occurred within the last
    seven days for a specified school. The records are unarranged and include details such
    as transaction time, amount, transaction type, status, reason, name of the receiver, and particulars.

    Parameters:
        school_id (int): The identifier of the school for which transaction records are retrieved.

    Returns:
        list or None: A list of dictionaries representing unarranged transaction records within
                      the last seven days. Each dictionary contains details such as:
                      - 'time': The timestamp of the transaction.
                      - 'amount': The amount involved in the transaction.
                      - 'transaction_type': The type of the transaction.
                      - 'status': The status of the transaction (e.g., 'SUCCESS').
                      - 'reason': The reason or description of the transaction.
                      - 'name_of_receiver': The name of the receiver, if applicable.
                      - 'particulars': The particulars associated with the transaction.
                  If no records are found, returns None.
    """
    try:
        current_date = datetime.now()
        seven_days_ago = current_date - timedelta(days=7)

        # Use the model class directly to filter records
        transaction_records = Operations_account_transaction_record.get_transaction(
            start_date=seven_days_ago,
            end_date=current_date,
            school=school_id
        ).filter(status="SUCCESS")

        # Convert the queryset to a list of dictionaries
        transaction_records_list = [
            {
                "time": record.time,
                "amount": record.amount,
                "transaction_type": record.transaction_type,
                "status": record.status,
                "reason": record.reason,
                "name_of_reciever": record.name_of_reciever,
                "particulars": record.particulars
            }
            for record in transaction_records
        ]

        return transaction_records_list

    except Operations_account_transaction_record.DoesNotExist:
        return None


def format_date(date):
    # Create a dictionary for mapping month numbers to month names
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
        6: "June", 7: "July", 8: "August", 9: "September", 10: "October",
        11: "November", 12: "December"
    }

    day_of_week = date.strftime("%A")

    day_of_month = date.strftime("%d")
    if day_of_month.endswith("1") and day_of_month != "11":
        day_of_month += "st"
    elif day_of_month.endswith("2") and day_of_month != "12":
        day_of_month += "nd"
    elif day_of_month.endswith("3") and day_of_month != "13":
        day_of_month += "rd"
    else:
        day_of_month += "th"

    month = month_names[date.month]

    year = date.strftime("%Y")

    formatted_date = f"{day_of_week}, {day_of_month} {month} {year}"

    return formatted_date


def process_and_sort_transactions_by_months(transactions):
    """
    Processes a list of transactions, grouping them by the month in which they occurred
    and sorting the data by month name.

    Parameters:
        transactions (iterable): A collection of transactions, where each transaction is
                                expected to be a dictionary with 'time' and 'amount' fields.

    Returns:
        list: A list of dictionaries, where each dictionary represents a month's total
              transaction amount. Each dictionary has the following structure:
              {
                'month': str,        # The name of the month.
                'total_amount': float # The total amount of transactions for the month.
              }
    """
    import calendar

    monthly_totals = {}

    for transaction in transactions:
        transaction_date = transaction['time']
        month_name = calendar.month_name[transaction_date.month]

        # Check if the month already exists in the dictionary, and if not, initialize it
        if month_name not in monthly_totals:
            monthly_totals[month_name] = {
                'month': month_name,
                'total_amount': 0,
            }

        # Update the total amount for the corresponding month
        monthly_totals[month_name]['total_amount'] += transaction['amount']

    # Sort the monthly totals by month name
    sorted_monthly_totals = sorted(
        monthly_totals.values(),
        key=lambda x: list(calendar.month_name).index(x['month'])
    )

    return sorted_monthly_totals


def process_and_sort_transactions_by_days(transactions):
    """
    Processes a list of transactions, grouping them by their transaction date and
    organizing the data for each day.

    Parameters:
        transactions (iterable): A collection of transactions, where each transaction is
                                expected to be a dictionary with 'time', 'particulars',
                                'amount', and 'reason' fields.

    Returns:
        list: A list of dictionaries, where each dictionary represents a day's transactions.
              Each dictionary has the following structure:
              {
                "date": str,  # The formatted date of the transactions for the day.
                "transaction_data": [
                    {
                        "particulars": str,  # The name of the particulars for the transaction.
                        "amount": float,     # The amount of the transaction.
                        "reason": str        # The reason or description of the transaction.
                    },
                    # ... additional transaction data for the day ...
                ]
              }
    """
    daily_totals = defaultdict(lambda: {"date": None, "transaction_data": []})

    for transaction in transactions:
        transaction_date = transaction['time'].date()
        data = {
            "particulars": transaction['particulars'].name,
            "amount": transaction['amount'],
            "reason": transaction['reason']
        }

        daily_totals[transaction_date]["date"] = format_date(transaction_date)
        daily_totals[transaction_date]["transaction_data"].append(data)

    return list(daily_totals.values())


def calculate_cash_and_transfer_transaction_total(transactions):
    """
    Calculates the total amount of 'CASH' and 'TRANSFER' transactions from a given list.

    Parameters:
        transactions (iterable): A collection of transactions, where each transaction is
                                expected to be a dictionary with a 'transaction_type' and
                                'amount' field.

    Returns:
        tuple: A tuple containing two values:
            - The total amount of transactions with 'transaction_type' as 'CASH'.
            - The total amount of transactions with 'transaction_type' as 'TRANSFER'.
    """
    cash_total = 0
    transfer_total = 0

    for transaction in transactions:
        # Check if the transaction has a 'transaction_type' field and it is "Cash"
        if 'transaction_type' in transaction and transaction['transaction_type'] == "CASH":
            cash_total += transaction['amount']

        if 'transaction_type' in transaction and transaction['transaction_type'] == "TRANSFER":
            transfer_total += transaction['amount']

    return cash_total, transfer_total


def get_user_school(user):
    '''
        Get the user's school
    '''
    return get_object_or_404(School, id=get_school_from_user(user.id))


def get_transaction_summary_by_header(transactions):
    """
    Generates a summary of transactions based on their particulars (eg: Transportation, feeding), including total
    amounts and percentages for each particular type.

    Parameters:
        transactions (iterable): A collection of transactions to be summarized.

    Returns:
        dict: A dictionary containing transaction summaries based on particulars. Each
              entry in the dictionary includes the following information:
              - 'total_amount': The total amount of transactions for the specific particulars.
              - 'percentage': The percentage of the total transaction amount represented by
                               transactions of this particulars type.
    """
    transaction_summary = {}

    for transaction in transactions:
        # Ensure transaction has the expected attributes
        particulars = getattr(transaction, 'particulars', None)
        amount = getattr(transaction, 'amount', None)

        if particulars is None or amount is None:
            raise ValueError("Each transaction must have 'particulars' and 'amount' attributes")

        # Get the name of the particulars
        particulars_name = getattr(particulars, 'name', None)

        if particulars_name is None:
            raise ValueError("Particulars must have a 'name' attribute")

        # Check if a summary for this particulars already exists
        if particulars_name in transaction_summary:
            summary = transaction_summary[particulars_name]
        else:
            # If not, initialize a new summary dictionary
            summary = {
                'total_amount': 0,
                'percentage': 0,
            }

        # Update the summary for this particulars
        summary['total_amount'] += amount

        # Update or add the summary to the transaction_summary dictionary
        transaction_summary[particulars_name] = summary

    all_amount = sum(summary['total_amount'] for summary in transaction_summary.values())

    # Calculate the percentage for each particulars, handle case where all_amount is zero
    if all_amount == 0:
        for summary in transaction_summary.values():
            summary['percentage'] = 0
    else:
        for particulars_name, summary in transaction_summary.items():
            percentage = (summary['total_amount'] / all_amount) * 100
            summary['percentage'] = percentage

    return transaction_summary


def  get_cash_left_and_month_summary(school_id, transaction_type=None):
    """
    Retrieves the remaining cash amount and total debit transactions for a given school
    within the current month.

    If `transaction_type` is specified:
    - If set to 'CASH', it returns only debit transactions for cash.
    - If set to 'TRANSFER', it returns only debit transactions for transfers.
    - If not specified or set to None, it returns all debit transactions.

    Parameters:
        - school_id (int): The identifier of the school for which the information is retrieved.
        - transaction_type (str, optional): The type of transaction.

    Returns:
        dict: A dictionary containing the following information:
            - 'cash_amount': The remaining amount of cash in the school's operations account.
            - 'total_amount': The total amount of debit transactions within the current month.
                              If no transactions are found, it defaults to 0.
    """


    operation_account = get_object_or_404(Operations_account, school=school_id)
    cash_amount_left = (
        operation_account.amount_available_transfer
        if transaction_type == "TRANSFER"
        else operation_account.amount_available_cash
    )

    if transaction_type is not None and transaction_type == "CASH":
        transaction_type = "CASH"

    if transaction_type is not None and transaction_type == "TRANSFER":
        transaction_type = "TRANSFER"


    # Get the current date and time in the appropriate time zone
    current_date = timezone.now()

    # Calculate the beginning of the current month
    beginning_of_month = timezone.make_aware(
        timezone.datetime(current_date.year, current_date.month, 1)
    )

    total_amount = Operations_account_transaction_record.objects.filter(
        transaction_category="DEBIT",
        transaction_type=transaction_type,
        status="SUCCESS",
        time__range=(beginning_of_month, current_date)
    ).aggregate(Sum('amount'))['amount__sum']

    # Create a dictionary with the result data
    data = {
        "cash_amount": cash_amount_left,
        "total_amount": total_amount or 0
    }

    return data


def get_all_school_header(school_id):
    '''
        Get all the school transactionsheader available
    '''
    particulars = Particulars.objects.filter(school=school_id)
    return particulars


def get_all_school_ranks (school_id):
    '''
        Get all the school ranks available
    '''
    ranks = Staff_type.objects.filter(school=school_id)
    return ranks


def get_all_banks ():

    banks = Bank.objects.all()
    return banks

class OperationType(Enum):
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    SAFE = "SAFE"


def update_operations_account(amount, school_id, operation_type):
    """
    Updates the amount of available cash in the operations account for a specific school
    based on the specified operation type.

    Parameters:
        amount (float): The amount to be added or subtracted from the available cash.
        school_id (int): The identifier of the school's operations account to be updated.
        operation_type (str): The type of operation to be performed. Supported values are
                              'SUBTRACT', 'ADD', or 'SAFE' to deduct, add, or keep the
                              current cash amount respectively.

    Returns:
        float: The updated amount of available cash after the specified operation.
    Raises:
        ValueError: If the provided operation_type is not one of the supported values.
    """

    operation_account = get_object_or_404(Operations_account, school=school_id)
    cash_amount_left = operation_account.amount_available_cash

    if operation_type == OperationType.SUBTRACT.value:
        cash_amount_left -= amount
    elif operation_type == OperationType.ADD.value:
        cash_amount_left += amount
    elif operation_type == OperationType.SAFE.value:
        cash_amount_left = cash_amount_left
    else:
        raise ValueError(f"Unsupported operation type: {operation_type}")

    # Update the database record
    operation_account.amount_available_cash = cash_amount_left
    operation_account.save()

    return cash_amount_left
