# Generated by Django 4.0.3 on 2023-08-04 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it', '0020_sociallink'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.URLField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
