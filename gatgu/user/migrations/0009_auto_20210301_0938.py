# Generated by Django 3.1 on 2021-03-01 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_merge_20210301_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='nickname',
            field=models.CharField(db_index=True, max_length=20),
        ),
    ]
