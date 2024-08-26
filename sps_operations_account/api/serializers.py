from rest_framework import serializers
from paystack.models import Bank
from sps_central_account.models import CapitalAccount
from sps_central_account.models.central_account_models import Receipts
from sps_core.models import Grade, SchoolConfig, Staff, StaffType, Student
from sps_fees_payment_structure.models import BusFeeCategory, SchoolLevyAnalytics, UniformAndBooksFeeCategory
from sps_fees_payment_structure.models.fees_breakdown_models import OtherFeeCategory, SchoolFeesCategory
from sps_fees_payment_structure.models.fees_history_and_status_models import PaymentHistory, PaymentStatus
from sps_operations_account.models import OperationsAccountTransactionModificationTracker, OperationsAccountTransactionRecord, OperationsAccountTransactionRecordsEditedField
from sps_operations_account.models import OperationsAccount
from sps_operations_account.models.operations_payment_models import Payroll, Taxroll
from sps_operations_account.models.transaction_models import Particular


class ReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipts
        fields = '__all__'



class OperationsAccountSerializer(serializers.ModelSerializer):
    total_amount_available = serializers.SerializerMethodField()

    class Meta:
        model =OperationsAccount
        fields = ('total_amount_available', 'amount_available_cash',
                  'amount_available_transfer')

    def get_total_amount_available(self, obj):
        return obj.get_total_amount_available()


class OperationsAndCapitalAccountSerializer(serializers.Serializer):
    operations_account = serializers.SerializerMethodField()
    central_account = serializers.SerializerMethodField()

    def get_operations_account(self, obj):
        operations_account = obj.get('operations_account')
        return OperationsAccountTotalSerializer(operations_account).data

    def get_central_account(self, obj):
        central_account = obj.get('central_account')
        return CentralAccountTotalSerializer(central_account).data



class  OperationsAccountTotalSerializer(serializers.ModelSerializer):
    total_amount_available = serializers.SerializerMethodField()
    class Meta:
        model =OperationsAccount
        fields = ('total_amount_available',)

    def get_total_amount_available(self, obj):
        return obj.get_total_amount_available()


class  CentralAccountTotalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalAccount
        fields = ('amount_available',)


class SummaryTransactionSerializer(serializers.Serializer):
    date = serializers.CharField()
    transaction_data = serializers.ListField(child=serializers.DictField())


class MonthlyTransactionSerializer(serializers.Serializer):
    month = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class CashandTransactionTotalSerializer(serializers.Serializer):
    cash_total = serializers.IntegerField()
    transfer_total = serializers.IntegerField()
    total = serializers.SerializerMethodField()

    def get_total(self, obj):
        return obj['cash_total'] + obj['transfer_total']


class OperationsAccountCashTransactionRecordSerializer(serializers.ModelSerializer):
    particulars = serializers.CharField(
        source='particulars.name', read_only=True)
    transaction_modification = serializers.SerializerMethodField()

    class Meta:
        model = OperationsAccountTransactionRecord
        fields = ('id', 'time', 'amount', 'transaction_category',
                  'particulars', 'reason', 'name_of_receiver', 'status', 'transaction_modification')


    def get_transaction_modification(self, obj):
        modifications = OperationsAccountTransactionModificationTracker.objects.filter(
            transaction=obj,
            status='PENDING'
        )
        if modifications.exists():
            return TransactionModificationReadSerializer(modifications.first()).data
        return None



class CashTransactionReadSerializer (serializers.ModelSerializer):
    particulars = serializers.CharField(
        source='particulars.name', read_only=True)

    class Meta:
        model = OperationsAccountTransactionRecord
        fields = ('id', 'time', 'amount', 'transaction_category',
                  'particulars', 'name_of_receiver', 'status', 'reason')



class TransactionEditedFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationsAccountTransactionRecordsEditedField
        fields = '__all__'


class TransactionModificationReadSerializer(serializers.ModelSerializer):
    edited_field_list = serializers.SerializerMethodField()
    class Meta:
        model = OperationsAccountTransactionModificationTracker
        fields = ('id', 'transaction', 'status', 'head_teacher_comment', 'date_of_modification', 'edited_field_list')

    def get_edited_field_list(self, obj):
        return TransactionEditedFieldSerializer(OperationsAccountTransactionRecordsEditedField.objects.filter(tracker=obj), many=True).data


class CashTransactionWriteSerializer (serializers.ModelSerializer):
    class Meta:
        model = OperationsAccountTransactionRecord
        fields = ('time', 'amount', 'reason', 'particulars',
                  'name_of_receiver', 'status')


class CashTransactionDetailsSerializer (serializers.Serializer):
    cash_amount = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class ParticularSerializer (serializers.ModelSerializer):
    class Meta:
        model = Particular
        fields = ('id', 'name')


class RankSerializer (serializers.ModelSerializer):

    class Meta:
        model = StaffType
        fields = ('id', 'basic_salary', 'tax', 'name')


class BankSerializer (serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('id', 'name', 'bank_code')


class TransactionSummarySerializer(serializers.Serializer):
    total_amount = serializers.IntegerField()
    percentage = serializers.FloatField()


class PercentageSummarySerializer(serializers.Serializer):
    particulars_name = serializers.CharField()
    total_amount = serializers.IntegerField()
    percentage = serializers.FloatField()


class StaffTypeSerializer (serializers.ModelSerializer):
    class Meta:
        model = StaffType
        fields = ('id', 'basic_salary', 'tax', 'name')


class StaffReadSerializer (serializers.ModelSerializer):
    staff_type = StaffTypeSerializer()
    bank = BankSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'first_name', 'last_name', 'account_number', 'bank',
                  'staff_type', 'salary_deduction')


class StaffWriteSerializer (serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ('first_name', 'last_name', 'bank', 'account_number', 'staff_type',
                  'salary_deduction')


class PayrollSerializer (serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = ('id', 'status', 'name', 'date_initiated', 'total_amount_for_salary')


class PayrollReadSerializer (serializers.ModelSerializer):

    class Meta:
        model = Payroll
        fields = ('status', 'name', 'date_initiated',
                  'total_amount_for_salary', 'total_amount_for_tax')


class TransferTransactionWriteSerializer (serializers.ModelSerializer):

    class Meta:
        model = OperationsAccountTransactionRecord
        fields = ('amount', 'particulars', 'reason', 'name_of_receiver',
                  'account_number_of_receiver', 'receiver_bank')


class TaxRollReadSerializer (serializers.ModelSerializer):

    class Meta:
        model = Taxroll
        fields = "__all__"


class TransactionSummarySerializer(serializers.Serializer):
    amount_paid = serializers.IntegerField()
    total_tax_paid = serializers.IntegerField()
    total_staffs = serializers.IntegerField()

    # You can add more fields as needed based on your data model

    class Meta:
        # Additional options for the serializer (if needed)
        fields = ('amount_paid', 'total_tax_paid')


class PayrollWriteSerializer (serializers.ModelSerializer):

    class Meta:
        model = Payroll
        fields = ("id", "name", "date_initiated", "staffs")


class StudentSerializer (serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("first_name", "last_name", "other_names")


class PaymentStatusSerializer (serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = ("status", "amount_in_debt", "amount_outstanding")


class SchoolFeeCategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = SchoolFeesCategory
        fields = ("id", "name", "minimum_percentage",
                  "is_compulsory", "amount")


class UniformAndBookFeeCategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = UniformAndBooksFeeCategory
        fields = ("id", "name", "minimum_percentage", "image",
                  "amount", "description")


class BusFeeCategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = BusFeeCategory
        fields = ("name", "morning_bus_fee", "evening_bus_fee")


class OtherFeeCategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = OtherFeeCategory
        fields = ("name", "minimum_percentage",
                  "is_compoulsry", "amount", "description")


class GradeSerializer (serializers.ModelSerializer):

    class Meta:
        model = Grade
        fields = ("name", "id")


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = ("status", "amount_in_debt",
                  "amount_outstanding", "last_amount_paid")


class StudentSerializer(serializers.ModelSerializer):
    grade_id = serializers.IntegerField(source='grade.id', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    payment_status = PaymentStatusSerializer(
        source='paymentstatus', read_only=True)

    class Meta:
        model = Student
        fields = ("first_name", "last_name", "other_names",
                  "registration_number", "student_id", "grade_id", "grade_name", "id", "payment_status")


class StudentPaymentStatusDetailSerializer (serializers.ModelSerializer):

    class Meta:
        model = PaymentStatus
        fields = ("status", "amount_in_debt", "amount_outstanding")


class PaymentHistorySerializer (serializers.ModelSerializer):

    class Meta:
        model = PaymentHistory
        fields = ("name", "amount_debited", "date_time_initiated", "id")


class PaymentHistoryDetailSerializer (serializers.ModelSerializer):

    class Meta:
        model = PaymentHistory
        fields = "__all__"


class CreateStudentSerializer (serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ("first_name", "last_name", "other_names",
                  "registration_number", "grade", "is_active")


class SchoolConfigSerializer (serializers.ModelSerializer):

    class Meta:
        model = SchoolConfig
        fields = ("term", "academic_session", "id")


class SchoolFeesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolFeesCategory
        fields = '__all__'


class BusFeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusFeeCategory
        fields = '__all__'


class UniformAndBooksFeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UniformAndBooksFeeCategory
        fields = '__all__'


class OtherFeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherFeeCategory
        fields = '__all__'

    class PaymentHistorySerializer (serializers.ModelSerializer):

        class Meta:
            model = PaymentHistory
            fields = '__all__'


class CreateGradeSerializer (serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name', 'next_class_to_be_promoted_to', 'school']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['next_class_to_be_promoted_to'] = self.to_representation(
            instance.next_class_to_be_promoted_to)
        return representation


class PayrollDetailSerializer (serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = '__all__'


class LevyAnalyticsSerializer (serializers.ModelSerializer):
    class Meta:
        model = SchoolLevyAnalytics
        fields = "__all__"
