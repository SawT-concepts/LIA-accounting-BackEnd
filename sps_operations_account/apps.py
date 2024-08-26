from django.apps import AppConfig


class SpsOperationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sps_operations_account'


    def ready(self):
        import sps_operations_account.signals
