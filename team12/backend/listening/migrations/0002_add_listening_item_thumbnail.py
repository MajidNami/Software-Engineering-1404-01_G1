# Generated manually for optional audio thumbnails

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listening', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listeningitem',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='thumbnails/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='listeningitem',
            name='thumbnail_url',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
