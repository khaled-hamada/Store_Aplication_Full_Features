# Generated by Django 3.1.7 on 2021-04-21 07:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0011_auto_20210420_2130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='point_product',
            name='trader_product',
        ),
        migrations.CreateModel(
            name='Store_To_Point_Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('quantity_packet', models.IntegerField(default=0)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('unit_sell_price', models.FloatField(default=0)),
                ('line_type', models.IntegerField(default=0)),
                ('given_status', models.IntegerField(default=0)),
                ('point_product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='content.point_product')),
                ('trader_product', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='content.trader_product')),
            ],
        ),
    ]
