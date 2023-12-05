import uuid
from django.db import models
from Main.model_function.helper import *
from Paystack.service import *
from django.core.exceptions import ValidationError
from Main.configuration import *


"""
This module defines Django models for managing a school system, including schools, classes, staff types, and staff members.

1. School Model (`School`):
   - Represents a school with attributes like `id`, `name`, `address`, `email_address`, and `logo`.
   - Uses a UUID field as the primary key.
   - Custom `__str__` method returns the school's name.

2. Class Model (`Class`):
   - Represents a class within a school with attributes like `name` and a foreign key to the `School` model.
   - Custom `__str__` method returns the class name.

3. Staff Type Model (`Staff_type`):
   - Represents types of staff roles within a school with attributes like `school`, `basic_salary`, `tax`, and `name`.
   - Custom `__str__` method returns the staff type's name.

4. Staff Model (`Staff`):
   - Represents individual staff members with attributes like `first_name`, `last_name`, `phone_number`, etc.
   - Includes relationships with other models (e.g., `School`, `Class`, `Staff_type`, `Paystack.Bank`).
   - Defines methods like `reset_salary_deduction_for_staffs_in_a_school` and `get_staff_total_payment`.
   - Overrides `save` to generate a unique `paystack_id` using `generate_paystack_id` before saving.

5. Custom Functions:
   - `reset_salary_deduction_for_staffs_in_a_school`: Resets salary deductions for all staff in a given school.
   - `get_staff_total_payment`: Calculates total payment for a staff member based on salary components.

"""

class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    email_address = models.EmailField(max_length=50)
    # django media settings
    logo = models.ImageField()

    def __str__(self):
        return self.name


class SchoolConfig (models.Model):

    school = models.OneToOneField("Main.School", on_delete=models.CASCADE)
    term = models.CharField(default="FIRST TERM", choices=school_terms, max_length=50)

    def __str__(self):
        return f'{self.school} config'

class Class(models.Model):
    name = models.CharField(max_length=50)
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Staff_type (models.Model):
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)
    basic_salary = models.BigIntegerField()
    tax = models.BigIntegerField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Staff (models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    account_number = models.CharField(max_length=50)
    bank = models.ForeignKey("Paystack.Bank", on_delete=models.CASCADE)
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)
    staff_type = models.ForeignKey(
        Staff_type, on_delete=models.SET_NULL, null=True)
    salary_deduction = models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    tin_number = models.CharField(max_length=50)
    paystack_id = models.CharField(max_length=50, blank=True)

    @staticmethod
    def reset_salary_deduction_for_staffs_in_a_school(school_id):
        staffs = Staff.objects.filter(school=school_id)

        for staff in staffs:
            staff.salary_deduction = 0
            staff.save()

    def get_staf_total_payment(self):
        basic_salary = self.staff_type.basic_salary
        tax = self.staff_type.tax
        salary_deduction = self.salary_deduction
        salary_to_be_paid = basic_salary - (tax + salary_deduction)

        return salary_to_be_paid

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



    def save(self, *args, **kwargs):
        # If paystack_id is not already assigned, generate it.
        if not self.paystack_id:
            paystack_id_generated = generate_paystack_id(instance=self)
            
            # Check if the generated paystack_id is 400 (or any other condition you want).
            if paystack_id_generated['status'] == 400:
                raise ValidationError(paystack_id_generated['data'])  # Use ValidationError instead of ValueError
            
            
            self.paystack_id = paystack_id_generated['data']
        
        super().save(*args, **kwargs)


class Student (models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    other_names = models.CharField( max_length=50)
    registration_number = models.CharField(max_length=60)
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)
    grade = models.ForeignKey("Main.Class", on_delete=models.CASCADE)


    def __str__(self):
        return self.first_name + " " + self.last_name
    

