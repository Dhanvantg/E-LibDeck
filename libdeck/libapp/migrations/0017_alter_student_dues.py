# Generated by Django 5.1.3 on 2024-12-26 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libapp', '0016_alter_book_borrow_borrow_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='dues',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=2),
        ),
    ]
