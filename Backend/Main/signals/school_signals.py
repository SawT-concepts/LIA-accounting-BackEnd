from django.db.models.signals import post_save
from django.dispatch import receiver
from Main.models import School, SchoolLevyAnalytics



@receiver(post_save, sender=School)
def create_school_levy_analytics(sender, instance, created, **kwargs):
    if created:
        SchoolLevyAnalytics.objects.create(school=instance)