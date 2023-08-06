# Generated by Django 4.0.3 on 2023-08-05 04:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ce', '0003_company_design_footerpage_globallocation_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='template',
            old_name='photo',
            new_name='cover_photo',
        ),
        migrations.RenameField(
            model_name='template',
            old_name='link',
            new_name='video',
        ),
        migrations.AddField(
            model_name='template',
            name='features',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='template',
            name='photos',
            field=models.JSONField(blank=True, null=True),
        ),
    ]