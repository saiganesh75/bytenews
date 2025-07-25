# Generated by Django 5.2.4 on 2025-07-24 06:16

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_article_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='readinghistory',
            options={'ordering': ['-timestamp']},
        ),
        migrations.RenameField(
            model_name='readinghistory',
            old_name='read_at',
            new_name='timestamp',
        ),
        migrations.AlterUniqueTogether(
            name='readinghistory',
            unique_together={('user', 'article')},
        ),
    ]
