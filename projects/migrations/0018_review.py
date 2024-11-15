# Generated by Django 5.1.2 on 2024-11-14 06:23

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_alter_project_creator'),
        ('users', '0011_alter_profile_short_bio_alter_profile_short_intro'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('body', models.TextField()),
                ('value', models.IntegerField()),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.profile')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='projects.project')),
            ],
            options={
                'unique_together': {('project', 'created_by')},
            },
        ),
    ]
