# Generated by Django 2.1.7 on 2019-04-07 12:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('profiles', '0003_auto_20190331_2336'), ]
    operations = [
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('author',
                 models.CharField(
                     max_length=254)),
                ('follow',
                 models.CharField(
                     max_length=254)),
            ],
        ),
    ]
