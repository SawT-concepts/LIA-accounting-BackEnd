from django.contrib import admin
from .models import Receipts, CapitalAccount, CapitalAccountTransactionRecord

@admin.register(Receipts)
class ReceiptsAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'title', 'from_account', 'to_account', 'amount', 'timestamp')
    search_fields = ('title', 'from_account', 'to_account')
    readonly_fields = ('transaction_id', 'title', 'timestamp')

@admin.register(CapitalAccount)
class CapitalAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number', 'school', 'amount_available')
    search_fields = ('name', 'account_number', 'school__name')

@admin.register(CapitalAccountTransactionRecord)
class CapitalAccountTransactionRecordAdmin(admin.ModelAdmin):
    list_display = ('time', 'amount', 'school')
    list_filter = ('school',)
