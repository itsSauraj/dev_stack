# Generated by Django 5.1.2 on 2024-10-16 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_rename_user_skills_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills',
            name='level',
            field=models.IntegerField(default=1, max_length=5),
        ),
    ]