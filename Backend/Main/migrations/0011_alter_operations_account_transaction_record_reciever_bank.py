# Generated by Django 4.2.5 on 2023-11-12 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Paystack', '0001_initial'),
        ('Main', '0010_remove_staff_bank_name_staff_bank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operations_account_transaction_record',
            name='reciever_bank',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Paystack.bank'),
            preserve_default=False,
        ),
    ]
