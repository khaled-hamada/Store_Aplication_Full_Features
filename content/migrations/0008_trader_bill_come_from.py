# Generated by Django 3.1.7 on 2021-04-19 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_auto_20210418_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='trader_bill',
            name='come_from',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='content.trader_bill'),
        ),
    ]
