# Generated by Django 5.1.3 on 2024-12-26 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libapp', '0012_feedback_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarysettings',
            name='fee_compound',
            field=models.PositiveIntegerField(default=5),
        ),
    ]
