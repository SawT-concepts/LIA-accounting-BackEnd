from django.urls import path, include
from Api.Api_pages.Authentication import *
from Api.Api_pages.operations.cashbook import *
from Api.Api_pages.head_teacher.operation_account import *
from Api.Api_pages.operations.salaries import *
from Api.Api_pages.directors.operations import *
from Api.Api_pages.main.general import *
from rest_framework_simplejwt.views import TokenRefreshView
from Api.Api_pages.school_fees.main import *
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from Api.Api_pages.school_accountant.main import GetPercentageSummary, GetGraphOfClassPayment, GetPaymentSmmaryByClass
from Api.Api_pages.school_accountant.student_and_class import GetAllStudents, GetListOfClass
from Api.Api_pages.school_accountant.class_fee_settings import GetFinancialInfoForAClass
from Api.Api_pages.operations.transfers import GetAllTransferTransaction, GetCashLeftInSafeAndCurrentMonthTransferSummary


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
    path('fetch_school_rank', GetRanks.as_view(), name='fetch_school_rank'),
    path('fetch_banks', GetBanks.as_view(), name='fetch_banks'),
    path('verify_account_number', VerifyAccountNumber.as_view(),
         name='verify_account_number'),

    # Operation
    path('get_amount_available_operations_account',
         GetAmountAvailableOperationsAccount.as_view(), name='get_amount available'),
    path('get_operations_and_central_operations_account',
         GetOperationsAndCenteralAccountTotal.as_view(), name='get_operations_and_central_operations'),
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
    path('get_header_summary', GetPercentageSummary.as_view(),
         name='get_header_summary'),
    path('get_operations_breakdown', GetParticularsSummary.as_view(),
         name='get_percentage_breakdown'),
    path('get_payroll_info/<str:payroll_id>',
         GetPayrollDetails.as_view(), name='get_payroll'),
    path('process_payroll/<str:payroll_id>',
         ProcessPayrollAndTax.as_view(), name='process_payroll'),


    # transfers
    path('get_all_transfers_transaction/<str:pending>/',
         GetAllTransferTransaction.as_view(), name='get_all_transfers_transaction'),
    path('get_cash_transaction_summary', GetCashLeftInSafeAndCurrentMonthTransferSummary.as_view(
    ), name='get_cash_transaction_summary'),


    # salaries and staffs
    path('get_all_staffs', GetAllStaffs.as_view(), name='get_all_staffs'),  # ✅
    path('add_and_edit_staff', AddAndEditStaff.as_view(),
         name='add_and_edit_staff'),  # ✅
    path('show_staff_type', ShowStaffType, name='show_staff_type'),  # ✅
    path('initiate_payroll', InitiatePayroll.as_view(),
         name='initiate_payroll'),  # ✅
    path('generate_taxroll/<str:payroll_id>',
         InitiateTaxroll.as_view(), name='generate_taxroll'),
    path('get_payroll_summary/<str:payroll_id>',
         GenerateTransactionSummary.as_view(), name='get_payroll_summary'),
    path('add_staff_to_payroll/<str:payroll_id>',
         AddStaffToPayroll.as_view(), name='add_staff_to_payroll'),
    path('remove_staff_from_payroll/<str:payroll_id>',
         RemoveStaffFromPayroll.as_view(), name='remove_staff_from_payroll'),
    path('get_all_payroll', OperationsGetAllPayroll.as_view(), name='get_all_payroll_operations'),


    # director salary and staffs
    path('approve_payroll/<str:payroll_id>',
         ApprovePayroll.as_view(), name='approve_payroll'),
    path('get_all_payroll', GetAllPayroll.as_view(), name='get_all_payroll'),
    path('get_payroll_details/<str:payroll_id>',
         ViewPayrollDetails.as_view(), name='get_payroll_details'),
     path('get_all_receipts', ReceiptsListView.as_view(), name='get_all_receipt'),
    # directors transfers
    path('approve_transfer/<str:transaction_id>',
         ApproveTransfer.as_view(), name='approve_transfer'),


    # head teacher
    path('head_teacher/get_pending_transaction',
         HeadTeacherGetAllPendingTransaction.as_view(), name='head_teacher_get_all_transactions'),
    path('head_teacher/modify_transaction/<str:id>',
         HeadTeacherModifyTransaction.as_view(), name='head_teacher_modify_transaction'),
    path('head_teacher/bulk_modify_transaction/<str:status>',
         HeadTeacherBulkModifyTransaction.as_view(), name='head_teacher_bulk_modify_transaction'),


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
    path("payment/get_bus_fee_breakdown/<str:student_id>",
         GetBusFeeBreakDownCharges.as_view(), name="get_bus_fee_Break_Down"),
    path("payment/get_other_fee_breakdown/<str:student_id>",
         GetOtherPaymentBreakDownCharges.as_view(), name="get_other_fee_breakdown"),




    # school accountant
    path('accountant/get_percentage_summary',
         GetPercentageSummary.as_view(), name="get_percentage_summary"),
    path('accountant/get_graph_payment_of_classes',
         GetGraphOfClassPayment.as_view(), name="get_graph_payment_of_classes"),
    path('accountant/get_payment_summary_by_class/<str:class_id>',
         GetPaymentSmmaryByClass.as_view(), name="get_payment_summary_by_class"),

    path('accountant/get_classes',  GetListOfClass.as_view(), name="get_classes"),
    path('accountant/get_all_students',
         GetAllStudents.as_view(), name="get_all_students"),


    path('accountant/get_financial_info_for_class/<str:grade_id>/<str:term>',
         GetFinancialInfoForAClass.as_view(), name="get_financial_info_for_class")
]
