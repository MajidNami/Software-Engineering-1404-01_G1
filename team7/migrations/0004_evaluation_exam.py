# Generated migration: Add exam field to Evaluation model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team7', '0003_apilog'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluation',
            name='exam',
            field=models.ForeignKey(blank=True, help_text='Reference to Exam', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='team7.exam'),
        ),
    ]
