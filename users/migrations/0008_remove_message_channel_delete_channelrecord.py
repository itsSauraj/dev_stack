# Generated by Django 5.1.2 on 2024-12-03 05:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_message_receiver'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='channel',
        ),
        migrations.DeleteModel(
            name='ChannelRecord',
        ),
    ]
