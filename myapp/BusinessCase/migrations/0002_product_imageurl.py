# Generated by Django 5.0.6 on 2024-06-12 13:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("BusinessCase", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="imageUrl",
            field=models.CharField(default="-", max_length=255),
            preserve_default=False,
        ),
    ]
