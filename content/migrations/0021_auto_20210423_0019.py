# Generated by Django 3.1.7 on 2021-04-22 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0020_auto_20210422_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store_to_point_product',
            name='point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Store_To_Point_Product', to='content.point'),
        ),
        migrations.AlterField(
            model_name='store_to_point_product',
            name='to_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='To_Point', to='content.point'),
        ),
    ]