# Generated by Django 4.0.2 on 2022-04-11 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_category_alter_auction_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='category',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
