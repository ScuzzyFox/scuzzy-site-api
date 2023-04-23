# Generated by Django 4.1.7 on 2023-04-23 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramChatId',
            fields=[
                ('chat_id', models.BigIntegerField(primary_key=True, serialize=False, unique=True)),
            ],
            options={
                'ordering': ['chat_id'],
            },
        ),
    ]
