# Generated by Django 4.1.7 on 2024-01-01 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userData', '0006_remove_glossarywords_bookname_glossarywords_book_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='studyTime',
        ),
    ]
