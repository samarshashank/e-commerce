# Generated by Django 3.0.8 on 2020-08-18 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200818_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='latest_bid',
            field=models.IntegerField(default='startbid'),
        ),
    ]
