# Generated by Django 4.0 on 2023-03-14 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cbcreport',
            name='file_path',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]