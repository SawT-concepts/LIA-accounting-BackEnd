from rest_framework import serializers
from Main.models import *
from Paystack.models import Bank


class OperationsAccountSerializer(serializers.ModelSerializer):
    total_amount_available = serializers.SerializerMethodField()

    class Meta:
        model = Operations_account
        fields = ('total_amount_available', 'amount_available_cash',
                  'amount_available_transfer')

    def get_total_amount_available(self, obj):
        return obj.get_total_amount_available()


class SummaryTransactionSerializer(serializers.Serializer):
    date = serializers.CharField()
    transaction_data = serializers.ListField(child=serializers.DictField())


class MonthlyTransactionSerializer(serializers.Serializer):
    month = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class CashandTransactionTotalSerializer (serializers.Serializer):
    cash_total = serializers.IntegerField()
    transfer_total = serializers.IntegerField()


class OperationsAccountCashTransactionRecordSerializer(serializers.ModelSerializer):
    particulars = serializers.CharField(
        source='particulars.name', read_only=True)

    class Meta:
        model = Operations_account_transaction_record
        fields = ('id', 'time', 'amount', 'transaction_category',
                  'particulars', 'reason', 'name_of_reciever', 'status')


class CashTransactionReadSerializer (serializers.ModelSerializer):
    particulars = serializers.CharField(
        source='particulars.name', read_only=True)

    class Meta:
        model = Operations_account_transaction_record
        fields = ('id', 'time', 'amount', 'transaction_category',
                  'particulars', 'name_of_reciever', 'status', 'reason')


class CashTransactionWriteSerializer (serializers.ModelSerializer):
    class Meta:
        model = Operations_account_transaction_record
        fields = ('time', 'amount', 'reason', 'particulars',
                  'name_of_reciever', 'status')


class CashTransactionDetailsSerializer (serializers.Serializer):
    cash_amount = serializers.IntegerField()
    total_amount = serializers.IntegerField()


class ParticularSerializer (serializers.ModelSerializer):
    class Meta:
        model = Particulars
        fields = ('id', 'name')


class RankSerializer (serializers.ModelSerializer):

    class Meta:
        model = Staff_type
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
        model = Staff_type
        fields = ('id', 'basic_salary', 'tax', 'name')


class StaffReadSerializer (serializers.ModelSerializer):
    staff_type = StaffTypeSerializer()

    class Meta:
        model = Staff
        fields = ('id', 'first_name', 'last_name', 'account_number',
        fields = ('id', 'first_name', 'last_name', 'account_number',
                  'staff_type', 'salary_deduction')


class StaffWriteSerializer (serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ('first_name', 'last_name', 'bank', 'account_number', 'staff_type',
                  'salary_deduction')


class PayrollSerializer (serializers.ModelSerializer):
    class Meta:
        model = Payroll
        fields = ('status', 'name', 'date_initialized', 'total_amount_salary')


class PayrollReadSerializer (serializers.ModelSerializer):

    class Meta:
        model = Payroll
        fields = ('status', 'name', 'date_initialized',
                  'total_amount_salary', 'total_amount_tax')


class TransferTransactionWriteSerializer (serializers.ModelSerializer):

    class Meta:
        model = Operations_account_transaction_record
        fields = ('amount', 'particulars', 'reason', 'name_of_reciever',
                  'account_number_of_reciever', 'reciever_bank')


class TaxRollReadSerializer (serializers.ModelSerializer):

    class Meta:
        models = Taxroll
        fields = "__all__"


class TransactionSummarySerializer(serializers.Serializer):
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_tax_paid = serializers.DecimalField(max_digits=10, decimal_places=2)

    # You can add more fields as needed based on your data model

    class Meta:
        # Additional options for the serializer (if needed)
        fields = ('amount_paid', 'total_tax_paid')


class PayrollSerializer (serializers.ModelSerializer):

    class Meta:
        model = Payroll
        fields = ("name", "date_initiated")


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
                  "is_compoulslry", "amount")


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
        model = Class
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


class CreateClassSerializer (serializers.ModelSerializer):
    class Meta:
        model = Class
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
