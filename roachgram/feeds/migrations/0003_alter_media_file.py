# Generated by Django 5.0.2 on 2024-02-28 15:29

import feeds.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0002_alter_bookmark_post_alter_bookmark_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='file',
            field=models.ImageField(blank=True, null=True, upload_to=feeds.models.mediaDirectory),
        ),
    ]