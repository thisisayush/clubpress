# Generated by Django 2.0.7 on 2018-07-07 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Options',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=250, unique=True)),
                ('value', models.TextField()),
                ('label', models.CharField(max_length=500)),
            ],
        ),
    ]
