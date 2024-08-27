from django.contrib import admin
from .models.main_models import OperationsAccount
from .models.operations_payment_models import Payroll, Taxroll
from .models.transaction_models import OperationsAccountTransactionRecord, OperationsAccountTransactionModificationTracker, OperationsAccountTransactionRecordsEditedField, Particular


@admin.register(OperationsAccount)
class OperationsAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'school', 'amount_available_cash', 'amount_available_transfer', 'get_total_amount_available')
    list_filter = ('school',)
    search_fields = ('name', 'account_number', 'school__name')


    def get_total_amount_available(self, obj):
        return obj.get_total_amount_available()
    get_total_amount_available.short_description = 'Total Amount Available'

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_initiated', 'status', 'total_amount_for_tax', 'total_amount_for_salary', 'school')
    list_filter = ('status', 'school')
    search_fields = ('name', 'school__name')
    readonly_fields = ('date_initiated', 'total_amount_for_tax', 'total_amount_for_salary')

@admin.register(Taxroll)
class TaxrollAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount_paid_for_tax', 'date_initiated', 'status', 'payroll', 'school')
    list_filter = ('status', 'school')
    search_fields = ('name', 'payroll__name', 'school__name')
    readonly_fields = ('date_initiated',)

@admin.register(OperationsAccountTransactionRecord)
class OperationsAccountTransactionRecordAdmin(admin.ModelAdmin):
    list_display = ('time', 'amount', 'transaction_type', 'status', 'transaction_category', 'school', 'name_of_receiver')
    list_filter = ('transaction_type', 'status', 'transaction_category', 'school')
    search_fields = ('reason', 'name_of_receiver', 'account_number_of_receiver', 'school__name')
    readonly_fields = ('customer_transaction_id', 'reference')

@admin.register(OperationsAccountTransactionModificationTracker)
class OperationsAccountTransactionModificationTrackerAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'status', 'date_of_modification')
    list_filter = ('status',)
    search_fields = ('transaction__reason', 'head_teacher_comment')
    readonly_fields = ('date_of_modification',)

@admin.register(OperationsAccountTransactionRecordsEditedField)
class OperationsAccountTransactionRecordsEditedFieldAdmin(admin.ModelAdmin):
    list_display = ('previous_state_attribute', 'previous_state_value', 'new_state_attribute', 'new_state_value', 'tracker', 'date_of_modification')
    list_filter = ('previous_state_attribute', 'new_state_attribute')
    search_fields = ('previous_state_value', 'new_state_value', 'tracker__transaction__reason')
    readonly_fields = ('date_of_modification',)

@admin.register(Particular)
class ParticularAdmin(admin.ModelAdmin):
    list_display = ('name', 'school')
    list_filter = ('school',)
    search_fields = ('name', 'school__name')
