# Generated by Django 5.2 on 2025-04-12 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_timeslot_end_date_alter_timeslot_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='tags',
            field=models.ManyToManyField(blank=True, to='web.timeslottag', verbose_name='Теги'),
        ),
    ]
