# Generated by Django 4.0.3 on 2023-08-03 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it', '0011_security'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='keywords',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='security',
            name='short_description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='security',
            name='title',
            field=models.CharField(max_length=1000),
        ),
    ]
