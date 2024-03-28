# Generated by Django 5.0.2 on 2024-02-28 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variation',
            name='iphone_case_variation_category',
        ),
        migrations.AlterField(
            model_name='variation',
            name='clothes_variation_category',
            field=models.CharField(blank=True, choices=[('size', 'size'), ('colour', 'colour')], max_length=100),
        ),
    ]