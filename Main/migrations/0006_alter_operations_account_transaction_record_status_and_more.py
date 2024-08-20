# Generated by Django 4.2.5 on 2023-10-06 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0005_remove_operations_account_transaction_record_is_approved_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operations_account_transaction_record',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('INITIALIZED', 'INITIALIZED'), ('SUCCESS', 'SUCCESS'), ('FAILED', 'FAILED'), ('CANCELLED', 'CANCELLED'), ('RETRYING', 'RETRYING')], default='PENDING', max_length=50),
        ),
        migrations.AlterField(
            model_name='payroll',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('INITIALIZED', 'INITIALIZED'), ('SUCCESS', 'SUCCESS'), ('FAILED', 'FAILED'), ('RECONCILIATION', 'RECONCILIATION')], default='PENDING', max_length=100),
        ),
    ]