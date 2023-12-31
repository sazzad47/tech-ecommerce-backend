# Generated by Django 4.0.3 on 2023-08-04 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('it', '0018_alter_product_pdf_alter_product_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
            ],
        ),
    ]
