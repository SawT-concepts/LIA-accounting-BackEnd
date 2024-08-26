from django.db.models.signals import post_save
from django.dispatch import receiver
from sps_core.models import Student
from sps_fees_payment_structure.models.fees_history_and_status_models import PaymentStatus


@receiver(post_save, sender=Student)
def create_student_payment_info(sender, instance, created, **kwargs):
    if created:
        try:
            amount_in_debt = instance.calculate_basic_amount_in_debt()
            print(amount_in_debt)
            payment_status = PaymentStatus.objects.create(student=instance, amount_in_debt=amount_in_debt)
            payment_status.save()
        except Exception as e:
            print(f"Error creating payment status: {e}")
