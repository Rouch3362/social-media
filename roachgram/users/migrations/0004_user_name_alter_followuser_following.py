# Generated by Django 5.0.2 on 2024-02-22 10:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_followuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='followuser',
            name='following',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followings', to=settings.AUTH_USER_MODEL),
        ),
    ]
