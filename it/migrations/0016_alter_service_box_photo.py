# Generated by Django 4.0.3 on 2023-08-04 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it', '0015_alter_service_keywords'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='box_photo',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]
