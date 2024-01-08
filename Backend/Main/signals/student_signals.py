from django.db.models.signals import post_save
from django.dispatch import receiver
from Main.models import Student
from Main.models import PaymentHistory


@receiver(post_save, sender=Student)
def create_student_payment_info(sender, instance, created, **kwargs):
  if created: 
    PaymentHistory.objects.create()