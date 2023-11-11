import uuid
from django.db import models
import json
from Main.model_function.helper import generate_taxroll_staff_table_out_of_payroll
from datetime import datetime

def get_default_staffs():
    return [{}]

class Payroll(models.Model):
    Status = (
        ("PENDING", "PENDING"),
        ("INITIALIZED", "INITIALIZED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("RECONCILIATION", "RECONCILIATION"),
        ("CANCELLED", "CANCELLED"),
        ("PARTIAL_SUCCESS", "PARTIAL_SUCCESS"),
    )

    name = models.CharField(max_length=100)
    date_initiated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=100, choices=Status, default="PENDING")
    

    # Change staffs field to a JSONField
    staffs = models.JSONField(default=get_default_staffs)

    # financials
    total_amount_for_tax = models.BigIntegerField(default=0)
    total_amount_for_salary = models.BigIntegerField(default=0)

    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)

    #!

    def add_staff(self, staff_data_list):
        if "staffs" not in self.staffs:
            self.staffs = []

        # Use extend to add all elements in the list
        self.staffs.extend(staff_data_list)

    #! method to calculate the total amount paid for tax
    def get_total_tax_paid(self):
        staffs_data = json.loads(self.staffs) if self.staffs else []
        return sum(staff.get("tax_payable", 0) for staff in staffs_data)

    def get_total_salary_paid(self):
        staffs_data = json.loads(self.staffs) if self.staffs else []
        return sum(staff.get("basic_salary", 0) for staff in staffs_data)
    
    
    def remove_staff_by_id(self, staff_id):
        if "staffs" not in self.staffs:
            return  # If staffs is not a list, nothing to remove

        updated_staffs = [
            staff for staff in self.staffs if staff.get("staff_id") != staff_id]
        self.staffs = updated_staffs

    def get_all_failed_staff_payment(self):
        failed_staffs = []
        for staff in self.staffs:
            if staff.get("status") == "FAILED":
                failed_staffs.append(staff)

        return failed_staffs

    def get_payment_summary(self):
        total_amount_for_tax = self.total_amount_for_tax
        total_amount_for_salary = self.total_amount_for_salary
        total_staffs = len(self.staffs)
        successful_staffs = sum(
            1 for staff in self.staffs if staff.get("status") == "SUCCESS")
        failed_staffs = sum(
            1 for staff in self.staffs if staff.get("status") == "FAILED")

        return {
            "total_amount_for_tax": total_amount_for_tax,
            "total_amount_for_salary": total_amount_for_salary,
            "total_staffs": total_staffs,
            "successful_staffs": successful_staffs,
            "failed_staffs": failed_staffs,
        }




    @staticmethod
    def generate_payroll_name():
        pre_text = 'Salary Payment for'
        # get the current year and month
        current_year = datetime.now().year
        current_month_name = datetime.now().strftime('%B')

        # save it as Salary payment for 2021, March Ending quarter
        payroll_name = f"{pre_text} {current_year}, {current_month_name} Ending quarter"
        return payroll_name
    


    def save(self, *args, **kwargs):

        self.total_amount_for_tax = self.get_total_tax_paid()
        self.total_amount_for_salary = self.get_total_salary_paid()


        # Convert staffs list to JSON before saving
        if isinstance(self.staffs, list):
            self.staffs = json.dumps(self.staffs)


        super().save(*args, **kwargs)

        

    def __str__(self):
        return self.name


class Taxroll(models.Model):
    Status = (
        ("PENDING", "PENDING"),
        ("INITIALIZED", "INITIALIZED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("RECONCILIATION", "RECONCILIATION"),
    )

    name = models.CharField(max_length=100)
    amount_paid_for_tax = models.BigIntegerField()
    date_initiated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=Status)
    staffs = models.JSONField(default=get_default_staffs)

    # Create a one-to-one relationship with the Payroll model
    payroll = models.OneToOneField("Main.Payroll", on_delete=models.CASCADE)

    def add_staff(self, staff_data_list):
        if "staffs" not in self.staffs:
            self.staffs = []

        # Use extend to add all elements in the list
        self.staffs.extend(staff_data_list)

    def save(self, *args, **kwargs):
        # Convert staffs list to JSON before saving
        if isinstance(self.staffs, list):
            self.staffs = json.dumps(self.staffs)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @staticmethod
    def generate_taxroll_out_of_payroll(payroll_id):
        try:
            payroll = Payroll.objects.select_related(
                'school').get(id=payroll_id)
            staffs_on_payroll = json.loads(payroll.staffs)

            # Generate taxroll staffs from payroll staffs
            taxroll_staffs = generate_taxroll_staff_table_out_of_payroll(
                staffs_on_payroll)

            # Create a Taxroll instance
            taxroll_name = f'Taxroll for {payroll.name}'
            taxroll = Taxroll.objects.create(
                name=taxroll_name,
                amount_paid_for_tax=payroll.total_amount_for_tax,
                status=Payroll.Status['Success'],
                staffs=taxroll_staffs,
                payroll=payroll
            )
            taxroll.save()
            return ("SUCCESS")  # Successful generation
        except Payroll.DoesNotExist:
            return ("ERROR_404")
        except Exception as e:
            print(f"Error generating Taxroll: {str(e)}")
            return ("ERROR_502")  # Error occurred during generation3

#gnerate paystacl id for each staffs