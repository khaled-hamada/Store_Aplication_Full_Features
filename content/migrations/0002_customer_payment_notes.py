# Generated by Django 3.0.2 on 2021-05-17 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer_payment',
            name='notes',
            field=models.TextField(default=''),
        ),
    ]
