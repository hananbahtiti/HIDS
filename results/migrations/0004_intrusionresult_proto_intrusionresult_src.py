# Generated by Django 4.2.20 on 2025-05-18 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0003_alter_intrusionresult_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='intrusionresult',
            name='proto',
            field=models.CharField(default='N/A', max_length=20),
        ),
        migrations.AddField(
            model_name='intrusionresult',
            name='src',
            field=models.GenericIPAddressField(default='N/A'),
        ),
    ]
