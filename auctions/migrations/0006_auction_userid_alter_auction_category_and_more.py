# Generated by Django 4.0.2 on 2022-04-11 11:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_comment_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='userid',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='addedby', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auction',
            name='category',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='auction',
            name='image',
            field=models.URLField(blank=True),
        ),
    ]
