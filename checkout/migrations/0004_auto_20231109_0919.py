# Generated by Django 3.2 on 2023-11-09 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_auto_20231104_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='original_bag',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='order',
            name='stripe_pid',
            field=models.CharField(default='', max_length=254),
        ),
    ]
