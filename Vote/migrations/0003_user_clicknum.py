# Generated by Django 3.0.5 on 2020-06-17 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Vote', '0002_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='clicknum',
            field=models.IntegerField(default=0, verbose_name='剩余投票数'),
        ),
    ]