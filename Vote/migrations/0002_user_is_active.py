# Generated by Django 3.0.5 on 2020-06-16 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Vote', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]