# Generated by Django 5.1.2 on 2024-11-29 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_message_sent_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='channel',
            field=models.TextField(default=None, null=True),
        ),
    ]
