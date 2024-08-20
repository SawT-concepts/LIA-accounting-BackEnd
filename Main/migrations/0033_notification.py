# Generated by Django 4.2.5 on 2024-08-20 15:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Main', '0032_operations_account_transaction_modification_tracker_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now=True)),
                ('type_of_notification', models.CharField(choices=[('transaction', 'Transaction'), ('payment', 'Payment'), ('school', 'School'), ('system', 'System')], max_length=255)),
                ('message', models.TextField()),
                ('recipients', models.ManyToManyField(related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('recipients_viewed', models.ManyToManyField(related_name='notifications_viewed', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
