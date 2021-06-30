# Generated by Django 3.1 on 2021-06-24 19:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderChat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_status', models.PositiveSmallIntegerField(choices=[(1, 'WAITING_MEMBERS'), (2, 'MEMBER_ASSEMBLED'), (3, 'PAY_STATUS_CHECKED'), (4, 'ORDER_COMPLETE'), (5, 'WAITING_PARCELS'), (6, 'WAITING_SHARE'), (7, 'GATGU_COMPLETE')], default=1, null=True)),
                ('tracking_number', models.CharField(max_length=30, null=True)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order_chat', to='article.article')),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now=True)),
                ('pay_status', models.BooleanField(default=False)),
                ('wish_price', models.IntegerField(null=True)),
                ('order_chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant_profile', to='chat.orderchat')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participant_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('order_chat', 'participant')},
            },
        ),
        migrations.AddField(
            model_name='orderchat',
            name='participants',
            field=models.ManyToManyField(related_name='order_chat', through='chat.ParticipantProfile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(null=True)),
                ('sent_at', models.DateTimeField(auto_now=True)),
                ('media', models.URLField(null=True)),
                ('type', models.CharField(max_length=30)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.orderchat')),
                ('sent_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
