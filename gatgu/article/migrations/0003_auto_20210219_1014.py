# Generated by Django 3.1 on 2021-02-19 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_auto_20210219_0712'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='time_remaining',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='product_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='article',
            name='thumbnail_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='article',
            name='time_max',
            field=models.DateTimeField(null=True),
        ),
    ]
