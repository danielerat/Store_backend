# Generated by Django 4.0.4 on 2022-04-24 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_rename_price_product_unit_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collection',
            old_name='title',
            new_name='name',
        ),
    ]
