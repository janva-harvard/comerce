# Generated by Django 3.1 on 2020-10-22 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20201022_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='buyer',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, related_name='buyer', to=settings.AUTH_USER_MODEL),
        ),
    ]
