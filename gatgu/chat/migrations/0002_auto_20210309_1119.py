# Generated by Django 3.1 on 2021-03-09 11:19

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='participantprofile',
            unique_together={('order_chat', 'participant')},
        ),
        migrations.RemoveField(
            model_name='participantprofile',
            name='out_at',
        ),
    ]
