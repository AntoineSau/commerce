# Generated by Django 4.0.2 on 2022-04-08 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auctions'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Auctions',
            new_name='Auction',
        ),
    ]
