from django.contrib import admin
from .models.fees_breakdown_models import (
    FeesCategory,
    SchoolFeesCategory,
    BusFeeCategory,
    UniformAndBooksFeeCategory,
    OtherFeeCategory,
    SchoolLevyAnalytics
)
from .models.fees_history_and_status_models import PaymentStatus, PaymentHistory

@admin.register(FeesCategory)
class FeesCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_type', 'school', 'grade')
    list_filter = ('school', 'grade', 'category_type')
    search_fields = ('school__name', 'grade__name', 'category_type')

@admin.register(SchoolFeesCategory)
class SchoolFeesCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'term', 'amount', 'is_compulsory')
    list_filter = ('term', 'is_compulsory')
    search_fields = ('name', 'category__school__name', 'category__grade__name')

@admin.register(BusFeeCategory)
class BusFeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'term', 'morning_bus_fee', 'evening_bus_fee')
    list_filter = ('term',)
    search_fields = ('name', 'category__school__name', 'category__grade__name')

@admin.register(UniformAndBooksFeeCategory)
class UniformAndBooksFeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'amount', 'is_recommended', 'is_compulsory')
    list_filter = ('is_recommended', 'is_compulsory')
    search_fields = ('name', 'category__school__name')

@admin.register(OtherFeeCategory)
class OtherFeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'term', 'amount', 'is_compulsory')
    list_filter = ('term', 'is_compulsory')
    search_fields = ('name', 'category__school__name')

@admin.register(SchoolLevyAnalytics)
class SchoolLevyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('school', 'amount_paid', 'amount_in_debt', 'amount_outstanding', 'percentage_paid')
    readonly_fields = ('amount_paid', 'amount_in_debt', 'amount_outstanding', 'percentage_paid', 'percentage_of_student_in_debt', 'percentage_of_student_outstanding')
    search_fields = ('school__name',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'last_amount_paid', 'amount_in_debt', 'amount_outstanding')
    list_filter = ('status',)
    search_fields = ('student__first_name', 'student__last_name', 'student__school__name')

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'date_time_initiated', 'amount_debited', 'payment_status', 'receipt_id')
    list_filter = ('payment_status', 'is_active', 'school')
    search_fields = ('student__first_name', 'student__last_name', 'school__name', 'receipt_id', 'paystack_reference')
    readonly_fields = ('breakdowns',)
