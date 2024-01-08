import string
from django.db import models
from Main.models.fees_structure_models import PaymentHistory, PaymentStatus
from Main.models.school_operations_models import Student
from Main.configuration import *


"""
Django models for handling various fee categories in a school management system.

1. FeesCategory:
   Represents a general fee category associated with a school grade.
   Fields:
   - school: One-to-One relationship with the School model.
   - grade: ForeignKey relationship with the Class model.
   - name: CharField for the name of the category.
   - category_type: CharField with choices from category_types.

2. SchoolFeesCategory:
   Represents a specific fee category associated with a school, grade, and term.
   Fields:
   - name: CharField for the name of the category.
   - category: ForeignKey relationship with the FeesCategory model.
   - term: CharField with choices from school_terms.
   - minimum_percentage: BigIntegerField for the minimum percentage.
   - amount: BigIntegerField for the amount.
   - is_compoulslry: BooleanField indicating whether the fee is compulsory.

3. BusFeeCategory:
   Represents a fee category specifically for bus fees associated with a school, grade, and term.
   Fields:
   - name: CharField for the name of the category.
   - category: ForeignKey relationship with the FeesCategory model.
   - morning_bus_fee: BigIntegerField for the morning bus fee.
   - evening_bus_fee: BigIntegerField for the evening bus fee.

4. UniformAndBooksFeeCategory:
   Represents a fee category for uniform and books associated with a school, grade, and category.
   Fields:
   - name: CharField for the name of the category.
   - image: ImageField for an image associated with the category.
   - category: ForeignKey relationship with the FeesCategory model.
   - grades: Many-to-Many relationship with the Class model.
   - school: ForeignKey relationship with the School model.
   - is_recommended: BooleanField indicating whether it is recommended.
   - amount: BigIntegerField for the amount.

5. OtherFeeCategory:
   Represents other fee categories associated with a school, grade, and category.
   Fields:
   - name: CharField for the name of the category.
   - image: ImageField for an image associated with the category.
   - category: ForeignKey relationship with the FeesCategory model.
   - grades: Many-to-Many relationship with the Class model.
   - school: ForeignKey relationship with the School model.
   - is_recommended: BooleanField indicating whether it is recommended.
   - amount: BigIntegerField for the amount.
"""


class FeesCategory (models.Model):

    school = models.OneToOneField("Main.School", on_delete=models.CASCADE)
    grade = models.ForeignKey("Main.Class", on_delete=models.CASCADE)
    category_type = models.CharField(max_length=60, choices=category_types)

    def __str__(self):
        return f'{self.category_type} for {self.grade} in {self.school}'

# todo: function to manually create all these stuffs as class is being created
# todo: automatically create tuition fee


class SchoolFeesCategory (models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey("Main.FeesCategory", on_delete=models.CASCADE)
    term = models.CharField(max_length=50, choices=school_terms)

    '''financials'''
    minimum_percentage = models.BigIntegerField(default=0)
    amount = models.BigIntegerField(default=0)
    is_compoulslry = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} school fee category for {self.category} in {self.category.grade} for {self.term}'


class BusFeeCategory (models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey("Main.FeesCategory", on_delete=models.CASCADE)

    '''financials'''
    morning_bus_fee = models.BigIntegerField(default=0)
    evening_bus_fee = models.BigIntegerField(default=0)

    def __str__(self):
        return f'{self.name} bus fee category for {self.category} in {self.category.grade} for {self.term}'


class UniformAndBooksFeeCategory (models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    category = models.ForeignKey("Main.FeesCategory", on_delete=models.CASCADE)
    is_recommended = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    '''financials'''
    minimum_percentage = models.BigIntegerField(default=0)
    amount = models.BigIntegerField(default=0)
    is_compoulslry = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} uniform fee category for {self.school}'


class OtherFeeCategory (models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    category = models.ForeignKey("Main.FeesCategory", on_delete=models.CASCADE)
    grades = models.ManyToManyField("Main.Class")
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)
    is_compoulslry = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    '''financials'''
    amount = models.BigIntegerField(default=0)

    def __str__(self):
        return f'{self.name} bus fee category for {self.school}'


class SchoolLevyAnalytics(models.Model):
    school = models.OneToOneField("Main.School", on_delete=models.CASCADE)
    amount_paid = models.BigIntegerField(default=0, null=True)
    amount_in_debt = models.BigIntegerField(default=0, null=True)
    amount_outstanding = models.BigIntegerField(default=0, null=True)
    percentage_paid = models.IntegerField(default=0, null=True)
    percentage_of_student_in_debt = models.IntegerField(default=0, null=True)
    percentage_of_student_outstanding = models.IntegerField(
        default=0, null=True)

    def __str__(self) -> string:
        return f'{self.school} levy analytics'

    def update_levy_record(self):
        '''
        Updates the levy analytics based on students' payment statuses and histories.

        Retrieves payment statuses and payment histories for students in the associated school,
        calculates the total amounts paid, in debt, and outstanding, and updates the instance fields.
        '''
        amount_in_debt = 0
        amount_outstanding = 0
        amount_paid = 0

        # Retrieve students with payments and history for the given school
        students = Student.objects.filter(school=self.school)

        for student in students:
            try:
                payment_status = PaymentStatus.objects.get(student=student)
                if payment_status.status == "OUTSTANDING":
                    amount_outstanding += payment_status.amount_outstanding
                elif payment_status.status == "IN DEBT":
                    amount_in_debt += payment_status.amount_in_debt
            except PaymentStatus.DoesNotExist:
                pass

            try:
                payment_history = PaymentHistory.objects.get(student=student)
                amount_paid += payment_history.amount_debited
            except PaymentHistory.DoesNotExist:
                pass
        # Update the object's fields and save changes
        self.amount_paid = amount_paid
        self.amount_in_debt = amount_in_debt
        self.amount_outstanding = amount_outstanding
        self.save()

    def reset_levy_record(self):
        self.amount_paid = 0
        self.save()

    def update_percentage_summary(self) -> None:
        """
        Updates percentage summary of students falling into different payment statuses.

        Calculates the percentages of students who have paid, are outstanding, or in debt
        based on their payment statuses and updates the respective fields in the model.

        """
        students_paid = 0
        students_outstanding = 0
        students_in_debt = 0

        students = Student.objects.filter(school=self.school)

        for student in students:
            try:
                payment_status = PaymentStatus.objects.get(student=student)
                if payment_status.status == "COMPLETED":
                    students_paid += 1
                elif payment_status.status == "IN DEBT":
                    students_in_debt += 1
                else:
                    students_outstanding += 1
            except PaymentStatus.DoesNotExist:
                pass

        total_number_of_students = len(students)

        # Calculate percentages only if there are students
        if total_number_of_students > 0:
            self.percentage_paid = (
                students_paid / total_number_of_students) * 100
            self.percentage_of_student_in_debt = (
                students_in_debt / total_number_of_students) * 100
            self.percentage_of_student_outstanding = (
                students_outstanding / total_number_of_students) * 100

        self.save()
