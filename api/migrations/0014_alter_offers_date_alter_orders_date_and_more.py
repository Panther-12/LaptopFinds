# Generated by Django 4.1.10 on 2023-09-19 13:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_offers_date_alter_orders_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offers',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 9, 19, 13, 55, 2, 749929, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='orders',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 9, 19, 13, 55, 2, 749929, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='vendororders',
            name='date',
            field=models.DateField(default=datetime.datetime(2023, 9, 19, 13, 55, 2, 749929, tzinfo=datetime.timezone.utc)),
        ),
    ]
