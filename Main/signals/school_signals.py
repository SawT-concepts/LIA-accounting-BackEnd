from django.db.models.signals import post_save
from django.dispatch import receiver
from Main.models import School, SchoolLevyAnalytics
from Main.models.account_models import Capital_Account, Operations_account



@receiver(post_save, sender=School)
def create_associated_school_models(sender, instance, created, **kwargs):
    if created:
        SchoolLevyAnalytics.objects.create(school=instance)
        Operations_account.objects.create(school=instance)
        Capital_Account.objects.create(school=instance)
