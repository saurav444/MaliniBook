# Generated by Django 2.1.5 on 2021-01-11 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0004_auto_20201210_2014'),
    ]

    operations = [
        migrations.CreateModel(
            name='Buk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('mobile_number', models.IntegerField(max_length=10)),
                ('email_id', models.EmailField(blank=True, max_length=254, null=True)),
                ('Book_description', models.CharField(max_length=1000)),
            ],
        ),
    ]