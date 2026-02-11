# Generated manually for team11 app

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team11', '0001_initial'),  # Update this to match your latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='listeningsubmission',
            name='transcription',
            field=models.TextField(blank=True, null=True),
        ),
    ]
