# Generated by Django 2.0.7 on 2018-07-20 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0004_clubmemberroles_club'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='facebook',
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='phone',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='short_description',
            field=models.CharField(default='Short description. Change in profile.', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='twitter',
            field=models.URLField(null=True),
        ),
    ]
