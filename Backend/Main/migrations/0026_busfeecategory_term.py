# Generated by Django 4.2.5 on 2024-02-08 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0025_alter_feescategory_category_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='busfeecategory',
            name='term',
            field=models.CharField(choices=[('FIRST TERM', 'FIRST TERM'), ('SECOND TERM', 'SECOND TERM'), ('THIRD TERM', 'THIRD TERM')], default='FIRST TERM', max_length=50),
            preserve_default=False,
        ),
    ]