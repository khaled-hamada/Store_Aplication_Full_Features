# Generated by Django 3.1.7 on 2021-04-23 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0022_auto_20210423_2306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='point_product_sellings',
            name='restored_amount',
        ),
        migrations.RemoveField(
            model_name='point_product_sellings',
            name='total_quantity_fixed',
        ),
    ]