# Generated by Django 5.2.2 on 2025-07-01 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classsection',
            name='subjects',
            field=models.ManyToManyField(blank=True, related_name='class_sections', to='core.subject'),
        ),
    ]
