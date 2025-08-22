# Generated manually for Gmail integration

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('selexia_travel', '0006_usersettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gmail_access_token',
            field=models.TextField(blank=True, null=True, verbose_name='Gmail Access Token'),
        ),
        migrations.AddField(
            model_name='user',
            name='gmail_refresh_token',
            field=models.TextField(blank=True, null=True, verbose_name='Gmail Refresh Token'),
        ),
        migrations.AddField(
            model_name='user',
            name='gmail_token_expiry',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Gmail Token Expiry'),
        ),
        migrations.AddField(
            model_name='user',
            name='gmail_profile_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Последнее обновление профиля Gmail'),
        ),
    ]
