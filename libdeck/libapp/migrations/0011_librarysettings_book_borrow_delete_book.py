# Generated by Django 5.1.3 on 2024-12-24 05:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libapp', '0010_alter_book_parent_cover_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibrarySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_period', models.PositiveIntegerField(default=14)),
                ('late_fee_amount', models.PositiveIntegerField(default=50)),
            ],
        ),
        migrations.CreateModel(
            name='Book_Borrow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrow_date', models.DateField(auto_now_add=True)),
                ('return_date', models.DateField(blank=True, null=True)),
                ('is_returned', models.BooleanField(default=False)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='copies', to='libapp.book_parent')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libapp.student')),
            ],
        ),
        migrations.DeleteModel(
            name='Book',
        ),
    ]