from django.db import models
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from sps_operations_account.utils.main import generate_taxroll_staff_table_out_of_payroll



Status = (
    ("PENDING", "PENDING"),
    ("INITIALIZED", "INITIALIZED"),
    ("SUCCESS", "SUCCESS"),
    ("FAILED", "FAILED"),
    ("RECONCILIATION", "RECONCILIATION"),
    ("CANCELLED", "CANCELLED"),
    ("PARTIAL_SUCCESS", "PARTIAL_SUCCESS"),
)


def get_default_staffs() -> List[Dict[str, Any]]:
    return [{}]


class Payroll(models.Model):
    name: str = models.CharField(max_length=100)
    date_initiated: datetime = models.DateTimeField(auto_now_add=True)
    status: str = models.CharField(
        max_length=100, choices=Status, default="PENDING")

    staffs: List[Dict[str, Any]] = models.JSONField(default=get_default_staffs)

    total_amount_for_tax: int = models.BigIntegerField(default=0)
    total_amount_for_salary: int = models.BigIntegerField(default=0)

    school: models.ForeignKey = models.ForeignKey("sps_core.school", on_delete=models.CASCADE)

    def add_staff(self, staff_data_list: List[Dict[str, Any]]) -> None:
        if "staffs" not in self.staffs:
            self.staffs = []

        self.staffs.extend(staff_data_list)

    def get_total_tax_paid(self) -> int:
        staffs_data: List[Dict[str, Any]] = json.loads(self.staffs) if isinstance(self.staffs, str) else self.staffs
        return sum(staff.get("tax_payable", 0) for staff in staffs_data if isinstance(staff, dict) and "tax_payable" in staff)

    def get_total_salary_paid(self) -> int:
        staffs_data: List[Dict[str, Any]] = json.loads(self.staffs) if isinstance(self.staffs, str) else self.staffs
        total_payable_salary: int = sum(staff.get("basic_salary", 0) for staff in staffs_data if isinstance(staff, dict) and "basic_salary" in staff)
        total_tax: int = sum(staff.get("tax_payable", 0) for staff in staffs_data if isinstance(staff, dict) and "tax_payable" in staff)
        deductions: int = sum(staff.get("salary_deduction", 0) for staff in staffs_data if isinstance(staff, dict) and "salary_deduction" in staff)

        return total_payable_salary + total_tax - deductions

    def remove_staff_by_id(self, staff_id: str) -> bool:
        if isinstance(self.staffs, str):
            self.staffs = json.loads(self.staffs)

        if not isinstance(self.staffs, list):
            return False

        original_length: int = len(self.staffs)
        updated_staffs: List[Dict[str, Any]] = [
            staff for staff in self.staffs if staff.get("staff_id") != staff_id
        ]
        self.staffs = updated_staffs

        print(len(updated_staffs) < original_length)
        return len(updated_staffs) < original_length

    def get_all_failed_staff_payment(self) -> List[Dict[str, Any]]:
        failed_staffs: List[Dict[str, Any]] = []
        for staff in self.staffs:
            if staff.get("status") == "FAILED":
                failed_staffs.append(staff)

        return failed_staffs

    def get_payment_summary(self) -> Dict[str, Any]:
        staffs_data: List[Dict[str, Any]] = json.loads(self.staffs) if isinstance(self.staffs, str) else self.staffs

        total_amount_for_tax: int = self.total_amount_for_tax
        total_amount_for_salary: int = self.total_amount_for_salary
        total_staffs: int = len(staffs_data)
        successful_staffs: int = sum(
            1 for staff in staffs_data if isinstance(staff, dict) and staff.get("status") == "SUCCESS")
        failed_staffs: int = sum(
            1 for staff in staffs_data if isinstance(staff, dict) and staff.get("status") == "FAILED")

        return {
            "total_amount_for_tax": total_amount_for_tax,
            "total_amount_for_salary": total_amount_for_salary,
            "total_staffs": total_staffs,
            "successful_staffs": successful_staffs,
            "failed_staffs": failed_staffs,
        }

    @staticmethod
    def generate_payroll_name() -> str:
        pre_text: str = 'Salary Payment for'
        current_year: int = datetime.now().year
        current_month_name: str = datetime.now().strftime('%B')
        payroll_name: str = f"{pre_text} {current_year}, {current_month_name} Ending quarter"
        return payroll_name

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.total_amount_for_tax = self.get_total_tax_paid()
        self.total_amount_for_salary = self.get_total_salary_paid()
        if isinstance(self.staffs, list):
            self.staffs = json.dumps(self.staffs)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Taxroll(models.Model):
    Status = (
        ("PENDING", "PENDING"),
        ("INITIALIZED", "INITIALIZED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("RECONCILIATION", "RECONCILIATION"),
    )

    name: str = models.CharField(max_length=100)
    amount_paid_for_tax: int = models.BigIntegerField()
    date_initiated: datetime = models.DateTimeField(auto_now_add=True)
    status: str = models.CharField(max_length=100, choices=Status)
    staffs: List[Dict[str, Any]] = models.JSONField(default=get_default_staffs)
    payroll: models.OneToOneField = models.OneToOneField("sps_operations_account.Payroll", on_delete=models.CASCADE)
    school: Optional[models.ForeignKey] = models.ForeignKey("sps_core.school", on_delete=models.CASCADE, null=True)

    def add_staff(self, staff_data_list: List[Dict[str, Any]]) -> None:
        if "staffs" not in self.staffs:
            self.staffs = []
        self.staffs.extend(staff_data_list)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if isinstance(self.staffs, list):
            self.staffs = json.dumps(self.staffs)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def generate_taxroll_out_of_payroll(payroll_id: int, school: Any) -> Dict[str, Any]:
        try:
            payroll: Payroll = Payroll.objects.select_related('school').get(id=payroll_id)
            staffs_on_payroll: List[Dict[str, Any]] = json.loads(payroll.staffs)

            taxroll_staffs: List[Dict[str, Any]] = generate_taxroll_staff_table_out_of_payroll(staffs_on_payroll)

            taxroll_name: str = f'Taxroll for {payroll.name}'
            Taxroll.objects.filter(name=taxroll_name, school=school).delete()

            taxroll: Taxroll = Taxroll.objects.create(
                name=taxroll_name,
                amount_paid_for_tax=payroll.total_amount_for_tax,
                status=Status[2][0],
                staffs=taxroll_staffs,
                payroll=payroll,
                school=school
            )

            print(taxroll)
            return {
                "status": "SUCCESS",
                "data": taxroll
            }

        except Payroll.DoesNotExist:
            return {
                "status": "ERROR",
                "message": "Payroll not found",
                "code": "ERROR_404"
            }

        except Exception as e:
            print(f"Error generating Taxroll: {str(e)}")
            return {
                "status": "ERROR",
                "message": str(e),
                "code": "ERROR_502"
            }
