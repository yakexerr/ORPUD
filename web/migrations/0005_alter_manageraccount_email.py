# Generated by Django 5.1.7 on 2025-04-19 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_employeeaccount_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manageraccount',
            name='email',
            field=models.EmailField(max_length=256, verbose_name='Email'),
        ),
    ]
