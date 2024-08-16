from pyclbr import Class
from django.contrib import admin
from .models import (
    School,
    Operations_account,
    Operations_account_transaction_record,
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

admin.site.register(School)
admin.site.register(Operations_account)
admin.site.register(Operations_account_transaction_record)
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