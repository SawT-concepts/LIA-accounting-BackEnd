# Generated by Django 4.2.5 on 2024-06-09 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Paystack', '0001_initial'),
        ('Main', '0028_paymentstatus_last_amount_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operations_account_transaction_record',
            name='bank',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Paystack.bank'),
        ),
    ]
