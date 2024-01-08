from django.db.models.signals import post_save
from django.dispatch import receiver
from Main.models import FeesCategory
from Main.models import Class
from django.db import transaction
from Main.configuration import *

@receiver(post_save, sender=Class)
@transaction.atomic
def create_fee_category_for_class(sender, instance, created, **kwargs):
    if created: 
        try:
            print("Signal triggered")
            #school fees category
            FeesCategory.objects.create(grade =instance, school = instance.school, category_type = category_types[0][0])

            #bus fee category
            FeesCategory.objects.create(grade =instance, school = instance.school, category_type = category_types[1][0])

            #unifomial fee category
            FeesCategory.objects.create(grade =instance, school = instance.school, category_type = category_types[2][0])


            #other fee category
            FeesCategory.objects.create(grade =instance, school = instance.school, category_type = category_types[3][0])


        except Exception as e:
            # Handle the exception (e.g., log it or raise a specific signal)
            print(f"Error creating payment status: {e}")
