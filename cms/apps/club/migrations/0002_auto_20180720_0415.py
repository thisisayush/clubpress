# Generated by Django 2.0.7 on 2018-07-20 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='cover_image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='club',
            name='logo',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
