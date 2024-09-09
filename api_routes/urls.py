from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from sps_announcements.api.views import AnnouncementList
from sps_authentication.api.authentication import *
from sps_central_account.api.school_accountant.class_fee_configuration import *
from sps_central_account.api.school_accountant.main import *
from sps_central_account.api.school_accountant.student_and_class import *
from sps_fees_payment_structure.api.school_fees_payment import *
from sps_generics.api.main import *
from sps_operations_account.api.director_operation_account import *
from sps_operations_account.api.head_teacher_operation_account import *
from sps_operations_account.api.operations_accountant.cashbook import *
from sps_operations_account.api.operations_accountant.salaries import *
from sps_operations_account.api.operations_accountant.transfers import *
from .config import *




router = DefaultRouter()
router.register(f'{OPERATIONS_ACCOUNTANT}/view_create_modify_cash_transaction',
                ViewAndModifyCashTransaction, basename='cashtransaction')


urlpatterns = [
#     # authentication
#     # ?✅ API responsible for the login functionality
    path('login', LoginView.as_view(), name='login'),
    path('refresh_token', TokenRefreshView.as_view(), name='refresh'),
    path('get_account_type', GetUserType.as_view(), name='get_account_type'),  # ✅
    path('get_user_details', GetUserDetails.as_view(),
         name='get_user_details'),


#     # generics
    path(f'{GENERIC}/fetch_header', FetchHeader.as_view(), name='fetch_header'),
    path(f'{GENERIC}/fetch_school_rank', GetRanks.as_view(), name='fetch_school_rank'),
    path(f'{GENERIC}/fetch_banks', GetBanks.as_view(), name='fetch_banks'),
    path(f'{GENERIC}/verify_account_number', VerifyAccountNumber.as_view(),
         name='verify_account_number'),
    path(f'{GENERIC}/get_announcements', AnnouncementList.as_view(), name='get_announcements'),


#     # Operation Accountant cashbook
    path(f'{OPERATIONS_ACCOUNTANT}/get_amount_available_operations_account',
         GetAmountAvailableOperationsAccount.as_view(), name='get_amount available'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_operations_and_central_operations_account',
         GetOperationsAndCentralAccountTotal.as_view(), name='get_operations_and_central_operations'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_cash_transaction_six_months_ago',
         GetMonthlyTransaction.as_view(), name="get_monthly_transaction"),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/get_cash_and_transfer_record_seven_days_ago', GetTransactionSevenDaysAgo.as_view(
    ), name='get_cash_and transfer_record_seven_days_ago'),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/get_all_approved_cash_transactions',
         GetAllApprovedCashTransactions.as_view(), name='all_cash_transactions_with_status'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_all_pending_cash_transactions',
         GetAllPendingCashTransactions.as_view(), name='all_pending_cash_transactions'),
    path(f'{OPERATIONS_ACCOUNTANT}/create_cash_transaction', CreateCashTransaction.as_view(),
         name='create_cash_transaction'),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/view_cash_transaction_summary', GetCashLeftInSafeAndCurrentMonthCashSummary.as_view(
    ), name="View cash transaction summary"),
    path('', include(router.urls)),
    path(f'{OPERATIONS_ACCOUNTANT}/get_header_summary', GetPercentageSummary.as_view(),
         name='get_header_summary'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_operations_breakdown', GetParticularSummary.as_view(),
         name='get_percentage_breakdown'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_payroll_info/<str:payroll_id>',
         GetPayrollDetails.as_view(), name='get_payroll'),
    path(f'{OPERATIONS_ACCOUNTANT}/process_payroll/<str:payroll_id>',
         ProcessPayrollAndTax.as_view(), name='process_payroll'),
    path(f'{OPERATIONS_ACCOUNTANT}/particulars', ViewAndAddParticulars.as_view(), name="view_and_add_particulars"),



#     # Operations Accountant transfers
    path(f'{OPERATIONS_ACCOUNTANT}/get_all_transfers_transaction/<str:pending>/',
         GetAllTransferTransaction.as_view(), name='get_all_transfers_transaction'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_cash_transaction_summary', GetCashLeftInSafeAndCurrentMonthTransferSummary.as_view(
    ), name='get_cash_transaction_summary'),



#     # salaries and staffs
    path(f'{OPERATIONS_ACCOUNTANT}/get_all_staffs', GetAllStaffs.as_view(), name='get_all_staffs'),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/add_and_edit_staff', AddAndEditStaff.as_view(),
         name='add_and_edit_staff'),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/show_staff_type', ShowStaffType, name='show_staff_type'),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/initiate_payroll', InitiatePayroll.as_view(),
         name='initiate_payroll'),  # ✅
    path(f'{OPERATIONS_ACCOUNTANT}/generate_taxroll/<str:payroll_id>',
         InitiateTaxroll.as_view(), name='generate_taxroll'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_payroll_summary/<str:payroll_id>',
         GenerateTransactionSummary.as_view(), name='get_payroll_summary'),
    path(f'{OPERATIONS_ACCOUNTANT}/add_staff_to_payroll/<str:payroll_id>',
         AddStaffToPayroll.as_view(), name='add_staff_to_payroll'),
    path(f'{OPERATIONS_ACCOUNTANT}/remove_staff_from_payroll/<str:payroll_id>',
         RemoveStaffFromPayroll.as_view(), name='remove_staff_from_payroll'),
    path(f'{OPERATIONS_ACCOUNTANT}/get_all_payroll', OperationsGetAllPayroll.as_view(), name='get_all_payroll_operations'),


# director salary and staffs
    path(f'{DIRECTOR}/approve_payroll/<str:payroll_id>',
         ApprovePayroll.as_view(), name='approve_payroll'),
    path(f'{DIRECTOR}/get_all_payroll', GetAllPayroll.as_view(), name='get_all_payroll'),
    path(f'{DIRECTOR}/get_payroll_details/<str:payroll_id>',
         ViewPayrollDetails.as_view(), name='get_payroll_details'),
     path('get_all_receipts', ReceiptsListView.as_view(), name='get_all_receipt'),
    # directors transfers
    path('approve_transfer/<str:transaction_id>',
         ApproveTransfer.as_view(), name='approve_transfer'),



#     # head teacher
    path(f'{HEAD_TEACHER}/get_pending_transaction',
         HeadTeacherGetAllPendingTransaction.as_view(), name='head_teacher_get_all_transactions'),
    path(f'{HEAD_TEACHER}/modify_transaction/<str:id>',
         HeadTeacherModifyTransaction.as_view(), name='head_teacher_modify_transaction'),
    path(f'{HEAD_TEACHER}/bulk_modify_transaction/<str:status>',
         HeadTeacherBulkModifyTransaction.as_view(), name='head_teacher_bulk_modify_transaction'),
    path(f'{HEAD_TEACHER}/get_pending_transaction_modification',
         HeadTeacherGetAllPendingTransactionModification.as_view(), name='head_teacher_get_all_pending_transaction_modification'),



#     # school fees payment
    path(f'{PAYMENTS}/get_token', LoginPaymentPortal.as_view(),
         name='get payment token'),  # ✅
    path(f'{PAYMENTS}/get_student_info/<str:student_id>',
         GetStudentInfo.as_view(), name='get student info'),  # ✅
    path(f'{PAYMENTS}/get_use_payment_status/<str:student_id>',
         GetUserPaymentStatus.as_view(), name='get_use_payment_status'),  # add signals here
    path(f'{PAYMENTS}/get_school_config/<str:student_id>',
         GetSchoolStatus.as_view(), name='get_school_config'),  # ✅
    path(f'{PAYMENTS}/get_school_fees_breakdown/<str:student_id>',
         GetSchoolFeesBreakDownCharges.as_view(), name='get_school_fees_Breakdown'),
    path(f'{PAYMENTS}/get_uniform_books_breakdown/<str:student_id>',
         GetUniformAndBookFeeBreakDownCharges.as_view(), name='get_uniform_books_Breakdown'),
    path(f'{PAYMENTS}/get_bus_fee_breakdown/<str:student_id>',
         GetBusFeeBreakDownCharges.as_view(), name="get_bus_fee_Break_Down"),
    path(f'{PAYMENTS}/get_other_fee_breakdown/<str:student_id>',
         GetOtherPaymentBreakDownCharges.as_view(), name="get_other_fee_breakdown"),



#     # school accountant
    path(f'{ACCOUNTANT}/get_percentage_summary',
         GetPercentageSummary.as_view(), name="get_percentage_summary"),
    path(f'{ACCOUNTANT}/get_graph_payment_of_classes',
         GetGraphOfGradePayment.as_view(), name="get_graph_payment_of_classes"),
    path(f'{ACCOUNTANT}/get_payment_summary_by_class/<str:class_id>',
         GetPaymentSummaryByGrade.as_view(), name="get_payment_summary_by_class"),

    path(f'{ACCOUNTANT}/get_classes',  GetListOfGrade.as_view(), name="get_classes"),
    path(f'{ACCOUNTANT}/get_all_students',
         GetAllStudents.as_view(), name="get_all_students"),


    path(f'{ACCOUNTANT}/get_financial_info_for_class/<str:grade_id>/<str:term>',
         GetFinancialInfoForAGrade.as_view(), name="get_financial_info_for_class")
]
