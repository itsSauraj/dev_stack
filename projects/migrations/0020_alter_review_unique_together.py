# Generated by Django 5.1.2 on 2024-11-14 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_alter_review_body_alter_review_value'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
    ]
