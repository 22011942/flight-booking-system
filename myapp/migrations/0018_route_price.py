# Generated by Django 5.0.4 on 2024-05-29 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_booking_booked_flight'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
