from django.db.models.signals import post_save
from django.dispatch import receiver
from sps_central_account.models.central_account_models import CapitalAccount
from sps_core.models import School
from sps_fees_payment_structure.models.fees_breakdown_models import SchoolLevyAnalytics
from sps_operations_account.models.main_models import OperationsAccount




@receiver(post_save, sender=School)
def create_associated_school_models(sender, instance, created, **kwargs):
    if created:
        SchoolLevyAnalytics.objects.create(school=instance)
        OperationsAccount.objects.create(school=instance)
        CapitalAccount.objects.create(school=instance)
