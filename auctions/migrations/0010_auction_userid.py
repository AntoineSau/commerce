# Generated by Django 4.0.2 on 2022-04-13 15:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_alter_auction_category_delete_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='userid',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='auctionuserid', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
