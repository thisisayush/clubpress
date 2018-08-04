# Generated by Django 2.0.7 on 2018-07-20 20:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('club', '0006_auto_20180720_1922'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubMemberPermissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('permission', models.CharField(max_length=50)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Club')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='clubmemberpermissions',
            unique_together={('user', 'club', 'permission')},
        ),
    ]
