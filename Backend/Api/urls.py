from django.urls import path, include
from Api.Api_pages.Authentication import *
from Api.Api_pages.operations.cashbook import *
from Api.Api_pages.head_teacher.operation_account import *
from Api.Api_pages.operations.salaries import *
from Api.Api_pages.directors.operations import *
from Api.Api_pages.main.general import *
from rest_framework_simplejwt.views import TokenRefreshView
from Api.Api_pages.school_fees.main import *
from Backend.settings import DEBUG, STATIC_URL, STATIC_ROOT, MEDIA_URL, MEDIA_ROOT
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('view_create_modify_cash_transaction',
                ViewAndModifyCashTransaction, basename='cashtransaction')


urlpatterns = [
    # authentication
    # ?✅ API responsible for the login functionality
    path('login', LoginView.as_view(), name='login'),
    # ✅? API responsible for the refresh functionality
    path('refresh_token', TokenRefreshView.as_view(), name='refresh'),
    path('get_account_type', GetUserType.as_view(), name='get_account_type'),  # ✅
    path('get_user_details', GetUserDetails.as_view(),
         name='get_user_details'),  # ✅


    # genral
    path('fetch_header', FetchHeader.as_view(), name='fetch_header'),

    # Operation
    path('get_amount_available_operations_account',
         GetAmountAvailableOperationsAccount.as_view(), name='get_amount available'),  # ✅
    path('get_cash_transaction_six_months_ago',
         GetMonthlyTransaction.as_view(), name="get_monthly_transaction"),  # ✅
    path('get_cash_and_transfer_record_seven_days_ago', GetTransactionSevenDaysAgo.as_view(
    ), name='get_cash_and transfer_record_seven_days_ago'),  # ✅
    path('get_all_cash_transactions/<str:pending>/',
         GetAllCashTransactions.as_view(), name='all_cash_transactions_with_status'),
    path('create_cash_transaction', CreateCashTransaction.as_view(),
         name='create_cash_transaction'),  # ✅
    path('view_cash_transction_summary', GetCashLeftInSafeAndCurrentMonthCashSummary.as_view(
    ), name="View cash transaction summary"),
    path('', include(router.urls)),
    # path ('get_header_summary', GetPercentageSummary.as_view(), name='get_header_summary'),



    # salaries and staffs
    path('get_all_staffs', GetAllStaffs.as_view(), name='get_all_staffs'),  # ✅
    path('add_and_edit_staff', AddAndEditStaff.as_view(),
         name='add_and_edit_staff'),  # ✅
    path('show_staff_type', ShowStaffType, name='show_staff_type'),  # ✅
    path('initiate_payroll', InitiatePayroll.as_view(),
         name='initiate_payroll'),  # ✅
    path('generate_taxroll/<str:payroll_id',
         InitiateTaxroll.as_view(), name='generate_taxroll'),
    path('get_payroll_summary/<str:payroll_id',
         GenerateTransactionSummary.as_view(), name='get_payroll_summary'),
    path('get_all_payroll', GetAllPayroll.as_view(), name='get_all_payroll'),


    # director salary and staffs
    path('approve_payroll/<str:payroll_id>',
         ApprovePayroll.as_view(), name='approve_payroll'),
    path('get_all_payroll', GetAllPayroll.as_view(), name='get_all_payroll'),
    path('get_payroll_details/<str:payroll_id>',
         ViewPayrollDetails.as_view(), name='get_payroll_details'),

    # directors transfers
    path('approve_transfer/<str:transaction_id>',
         ApproveTransfer.as_view(), name='approve_transfer'),


    # head teacher
    path('head_teacher/get_pending_transaction',
         HeadTeacherGetAllPendingTransaction.as_view(), name='head_teacher_get_all_transactions'),
    path('head_teacher/modify_transaction/<str:id>',
         HeadTeacherModifyTransaction.as_view(), name='head_teacher_modify_transaction'),


    # school fees payment
    path('payment/get_token', LoginPaymentPortal.as_view(),
         name='get payement token'),  # ✅
    path('payment/get_student_info/<str:student_id>',
         GetStudentInfo.as_view(), name='get student info'),  # ✅
    path("payment/get_use_payment_status/<str:student_id>",
         GetUserPaymentStatus.as_view(), name='get_use_payment_status'),  # add signals here
    path("payment/get_school_config/<str:student_id>",
         GetSchoolStatus.as_view(), name='get_school_config'),  # ✅
    path("payment/get_school_fees_breakdown/<str:student_id>",
         GetSchoolFeesBreakDownCharges.as_view(), name='get_school_fees_Breakdown'),
    path("payment/get_uniform_books_breakdown/<str:student_id>",
         GetUniformAndBookFeeBreakDownCharges.as_view(), name='get_uniform_books_Breakdown'),


]

if DEBUG:
    urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
