from django.apps import AppConfig


class SpsCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sps_core'

    def ready(self):
        import sps_core.signals.grade_signals
        import sps_core.signals.student_signals
        import sps_core.signals.school_signals
