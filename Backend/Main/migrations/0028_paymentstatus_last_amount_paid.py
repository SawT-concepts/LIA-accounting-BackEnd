# Generated by Django 4.2.5 on 2024-02-20 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0027_remove_otherfeecategory_grades_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentstatus',
            name='last_amount_paid',
            field=models.BigIntegerField(default=0),
        ),
    ]
