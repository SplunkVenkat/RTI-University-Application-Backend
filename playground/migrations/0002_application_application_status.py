# Generated by Django 3.2.9 on 2021-12-28 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='application_status',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
