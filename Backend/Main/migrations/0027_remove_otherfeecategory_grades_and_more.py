# Generated by Django 4.2.5 on 2024-02-10 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0026_busfeecategory_term'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otherfeecategory',
            name='grades',
        ),
        migrations.RemoveField(
            model_name='otherfeecategory',
            name='school',
        ),
        migrations.AddField(
            model_name='otherfeecategory',
            name='minimum_percentage',
            field=models.BigIntegerField(default=0),
        ),
    ]