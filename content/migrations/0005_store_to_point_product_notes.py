# Generated by Django 3.0.2 on 2021-05-15 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_auto_20210513_1954'),
    ]

    operations = [
        migrations.AddField(
            model_name='store_to_point_product',
            name='notes',
            field=models.TextField(default='', null=True),
        ),
    ]
