# Generated by Django 4.2.5 on 2024-01-12 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0024_alter_feescategory_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feescategory',
            name='category_type',
            field=models.CharField(choices=[('SCHOOL FEES', 'SCHOOL FEES'), ('UNIFORM WEARS AND BOOKS', 'UNIFORM WEARS AND BOOKS'), ('BUS FEES', 'BUS FEES'), ('OTHER', 'OTHER')], max_length=60),
        ),
    ]
