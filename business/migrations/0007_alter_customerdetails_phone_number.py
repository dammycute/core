# Generated by Django 4.1.4 on 2022-12-26 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0006_bvn_customerdetails_nin_picture_security_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdetails',
            name='phone_number',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True),
        ),
    ]
