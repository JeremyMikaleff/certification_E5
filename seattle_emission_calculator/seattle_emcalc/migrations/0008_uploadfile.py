# Generated by Django 4.2.2 on 2023-06-30 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seattle_emcalc", "0007_alter_newbuilding_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file_upload", models.FileField(upload_to="")),
            ],
        ),
    ]
