
import uuid
from typing import Optional, List
from django.db import models
from paystack.service import *
from django.core.exceptions import ValidationError
from sps_core.configuration import *
import hashlib
from django.shortcuts import get_object_or_404
from cloudinary.models import CloudinaryField

"""
This module defines Django models for managing a school system, including schools, classes, staff types, and staff members.

1. School Model (`School`):
   - Represents a school with attributes like `id`, `name`, `address`, `email_address`, and `logo`.
   - Uses a UUID field as the primary key.
   - Custom `__str__` method returns the school's name.

2. Grade Model (`Grade`):
   - Represents a class within a school with attributes like `name` and a foreign key to the `School` model.
   - Custom `__str__` method returns the class name.

3. Staff Type Model (`StaffType`):
   - Represents types of staff roles within a school with attributes like `school`, `basic_salary`, `tax`, and `name`.
   - Custom `__str__` method returns the staff type's name.

4. Staff Model (`Staff`):
   - Represents individual staff members with attributes like `first_name`, `last_name`, `phone_number`, etc.
   - Includes relationships with other models (e.g., `School`, `Grade`, `StaffType`, `paystack.Bank`).
   - Defines methods like `reset_salary_deduction_for_staffs_in_a_school` and `get_staff_total_payment`.
   - Overrides `save` to generate a unique `paystack_id` using `generate_paystack_id` before saving.

5. Custom Functions:
   - `reset_salary_deduction_for_staffs_in_a_school`: Resets salary deductions for all staff in a given school.
   - `get_staff_total_payment`: Calculates total payment for a staff member based on salary components.

"""


class School(models.Model):
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: str = models.CharField(max_length=100)
    address: str = models.CharField(max_length=100)
    email_address: str = models.EmailField(max_length=50)
    # django media settings
    logo: str = CloudinaryField('image', null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class SchoolConfig(models.Model):
    school: School = models.OneToOneField("sps_core.school", on_delete=models.CASCADE)
    term: str = models.CharField(default="FIRST TERM",
                            choices=school_terms, max_length=50)
    academic_session: str = models.CharField(
        default="2020/2021", choices=academic_session_choice, max_length=50)

    def __str__(self) -> str:
        return f'{self.school} config'


# update

class Grade(models.Model):
    name: str = models.CharField(max_length=50)
    next_class_to_be_promoted_to: Optional['Grade'] = models.ForeignKey(
        "sps_core.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    school: School = models.ForeignKey("sps_core.school", on_delete=models.CASCADE)
    is_active: bool = models.BooleanField(default=True, null=True)

    # total amount students paid in this class
    amount_paid: int = models.BigIntegerField(default=0, null=True)

    def __str__(self) -> str:
        return self.name

    def reset_amount_paid(self) -> None:
        self.amount_paid = 0
        self.save()

    def update_amount_paid(self, updated_amount: int) -> None:
        self.amount_paid = updated_amount
        self.save()


class StaffType(models.Model):
    school: School = models.ForeignKey("sps_core.school", on_delete=models.CASCADE)
    basic_salary: int = models.BigIntegerField()
    tax: int = models.BigIntegerField()
    name: str = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Staff(models.Model):
    first_name: str = models.CharField(max_length=100)
    last_name: str = models.CharField(max_length=100)
    phone_number: str = models.CharField(max_length=20)
    account_number: str = models.CharField(max_length=50)
    bank = models.ForeignKey("paystack.Bank", on_delete=models.CASCADE)
    school: School = models.ForeignKey("sps_core.school", on_delete=models.CASCADE)
    staff_type: Optional[StaffType] = models.ForeignKey(
        StaffType, on_delete=models.SET_NULL, null=True)
    salary_deduction: int = models.BigIntegerField()
    is_active: bool = models.BooleanField(default=True)
    tin_number: str = models.CharField(max_length=50)
    paystack_id: str = models.CharField(max_length=50, blank=True)

    @staticmethod
    def reset_salary_deduction_for_staffs_in_a_school(school_id: uuid.UUID) -> None:
        staffs: List[Staff] = Staff.objects.filter(school=school_id)

        for staff in staffs:
            staff.salary_deduction = 0
            staff.save()

    def get_staff_total_payment(self) -> int:
        basic_salary: int = self.staff_type.basic_salary
        tax: int = self.staff_type.tax
        salary_deduction: int = self.salary_deduction
        salary_to_be_paid: int = basic_salary - (tax + salary_deduction)

        return salary_to_be_paid

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs) -> None:
        # If paystack_id is not already assigned, generate it.
        if not self.paystack_id:
            paystack_id_generated: dict = generate_paystack_id(instance=self)

            # Check if the generated paystack_id is 400 (or any other condition you want).
            if paystack_id_generated['status'] == 400:
                raise ValidationError(paystack_id_generated['data'])

            self.paystack_id = paystack_id_generated['data']

        super().save(*args, **kwargs)


class Student(models.Model):
    first_name: str = models.CharField(max_length=50)
    last_name: str = models.CharField(max_length=50)
    other_names: str = models.CharField(max_length=50)
    parent_email: str = models.EmailField(max_length=50, null=True, unique=True)
    parent_phone_number: str = models.CharField(max_length=20, null=True)
    registration_number: str = models.CharField(max_length=60)
    school: School = models.ForeignKey("sps_core.school", on_delete=models.CASCADE)
    grade: Grade = models.ForeignKey("sps_core.Grade", on_delete=models.CASCADE)
    student_id: Optional[str] = models.CharField(
        max_length=128, unique=True, blank=True, null=True, editable=False)
    is_active: bool = models.BooleanField(default=True)

    def save(self, *args, **kwargs) -> None:
        pattern: str = f"{self.first_name}{self.last_name}{self.school.name}{self.registration_number}"
        hashed_pattern: str = hashlib.sha256(pattern.encode()).hexdigest()
        self.student_id = hashed_pattern
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name

    def calculate_basic_amount_in_debt(self) -> int:
        '''this function here just calculates the amount in debt for a student.
        it gets the payment of stuffs in his grade that are compoulsry'''

        # get the school current term
        # find the compoulsry school payment models for that class and term
        # do the same thing for the other fees too
        # then return the value
        student_class: Grade = self.grade
        amount: int = 0
        print(self.school)
        school_config: SchoolConfig = get_object_or_404(
            SchoolConfig.objects.select_related('school'), school=self.school)

        term: str = school_config.term

        # Use string references to avoid circular imports
        fee_category = models.get_model('sps_fees_payment_structure', 'FeesCategory').objects.get(
            grade=student_class, category_type=category_types[0][0])
        school_fees = models.get_model('sps_fees_payment_structure', 'SchoolFeesCategory').objects.filter(
            category=fee_category, term=term, is_compulsory=True)

        for fee in school_fees:
            amount += fee.amount

        other_fees = models.get_model('sps_fees_payment_structure', 'OtherFeeCategory').objects.filter(
            category=fee_category, term=term, is_compulsory=True)

        for fee in other_fees:
            amount += fee.amount

        return amount
