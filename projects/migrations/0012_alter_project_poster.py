# Generated by Django 5.1.2 on 2024-10-18 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_alter_project_poster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='poster',
            field=models.ImageField(default='posters/default.png', upload_to='posters/'),
        ),
    ]