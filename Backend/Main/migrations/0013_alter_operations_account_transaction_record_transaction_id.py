# Generated by Django 4.2.5 on 2023-11-12 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0012_operations_account_transaction_record_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operations_account_transaction_record',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
