from django.db.models.signals import post_save
from django.dispatch import receiver
from Main.models import Student
from Main.models import PaymentStatus


@receiver(post_save, sender=Student)
def create_student_payment_info(sender, instance, created, **kwargs):
    if created: 
        try:
            amount_in_debt = instance.calculate_basic_amount_in_debt()
            print("wallow wallow")
            print(amount_in_debt)
            payment_status = PaymentStatus.objects.create(student=instance, amount_in_debt=amount_in_debt)
            payment_status.save()
        except Exception as e:
            # Handle the exception (e.g., log it or raise a specific signal)
            print(f"Error creating payment status: {e}")
