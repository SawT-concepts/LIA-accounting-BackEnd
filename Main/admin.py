from django.contrib import admin

from Main.models.notification_models import Notification
from .models import (
    School,
    Operations_account,
    Operations_account_transaction_record,
    Operations_account_transaction_modification_tracker,
    Operations_account_transaction_records_edited_fields,
    Capital_Account,
    Capital_account_transaction_record,
    Particulars,
    Staff_type,
    Staff,
    Payroll,
    Taxroll,
    Class,
    Student,
    BusFeeCategory,
    UniformAndBooksFeeCategory,
    SchoolFeesCategory,
    OtherFeeCategory,
    FeesCategory,
    SchoolConfig,
    PaymentStatus
)

# Register your models here.

class OperationsAccountTransactionRecordsEditedFieldsInline(admin.TabularInline):
    model = Operations_account_transaction_records_edited_fields
    extra = 0  # No empty forms displayed
    readonly_fields = ('previous_state_attribute', 'previous_state_value', 'new_state_attribute', 'new_state_value', 'date_of_modification')
    can_delete = False
    max_num = 0  

@admin.register(Operations_account_transaction_modification_tracker)
class OperationsAccountTransactionModificationTrackerAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'status', 'head_teacher_comment')
    readonly_fields = ('transaction', 'status', 'head_teacher_comment')
    inlines = [OperationsAccountTransactionRecordsEditedFieldsInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Operations_account_transaction_records_edited_fields)
class OperationsAccountTransactionRecordsEditedFieldsAdmin(admin.ModelAdmin):
    list_display = ('previous_state_attribute', 'previous_state_value', 'new_state_attribute', 'new_state_value', 'tracker', 'date_of_modification')
    readonly_fields = ('previous_state_attribute', 'previous_state_value', 'new_state_attribute', 'new_state_value', 'tracker', 'date_of_modification')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(School)
admin.site.register(Operations_account)
admin.site.register(Capital_Account)
admin.site.register(Capital_account_transaction_record)
admin.site.register(Particulars)
admin.site.register(Staff_type)
admin.site.register(Staff)
admin.site.register(Payroll)
admin.site.register(Taxroll)
admin.site.register(Student)
admin.site.register(Class)
admin.site.register(SchoolFeesCategory)
admin.site.register(BusFeeCategory)
admin.site.register(UniformAndBooksFeeCategory)
admin.site.register(OtherFeeCategory)
admin.site.register(FeesCategory)
admin.site.register(SchoolConfig)
admin.site.register(PaymentStatus)
admin.site.register(Notification)
admin.site.register(Operations_account_transaction_record)
