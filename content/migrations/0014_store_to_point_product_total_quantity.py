# Generated by Django 3.1.7 on 2021-04-21 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_auto_20210421_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='store_to_point_product',
            name='total_quantity',
            field=models.IntegerField(default=0),
        ),
    ]
