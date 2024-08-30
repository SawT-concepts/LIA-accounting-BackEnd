from django.contrib import admin
from .models import School, SchoolConfig, Grade, StaffType, Staff, Student

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'email_address')
    search_fields = ('name', 'email_address')

@admin.register(SchoolConfig)
class SchoolConfigAdmin(admin.ModelAdmin):
    list_display = ('school', 'term', 'academic_session')
    list_filter = ('term', 'academic_session')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'is_active', 'amount_paid')
    list_filter = ('school', 'is_active')
    search_fields = ('name', 'school__name')

@admin.register(StaffType)
class StaffTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'basic_salary', 'tax')
    list_filter = ('school',)
    search_fields = ('name', 'school__name')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'school', 'staff_type', 'is_active')
    list_filter = ('school', 'staff_type', 'is_active')
    search_fields = ('first_name', 'last_name', 'school__name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'registration_number', 'school', 'grade', 'is_active')
    list_filter = ('school', 'grade', 'is_active')
    search_fields = ('first_name', 'last_name', 'registration_number', 'school__name')
    readonly_fields = ('student_id',)
