# Generated migration: Add Exam model and update Question model

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('team7', '0001_initial'),
    ]

    operations = [
        # Remove difficulty from Question FIRST (before creating Exam)
        migrations.RemoveField(
            model_name='question',
            name='difficulty',
        ),
        
        # Create Exam model
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('exam_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('exam_type', models.CharField(choices=[('writing', 'Writing'), ('speaking', 'Speaking')], default='writing', max_length=20)),
                ('total_time', models.IntegerField(default=0, help_text='Total time for the exam in seconds')),
                ('total_questions', models.IntegerField(default=0)),
                ('difficulty', models.IntegerField(default=1)),
            ],
        ),
        
        # Add title field to Question
        migrations.AddField(
            model_name='question',
            name='title',
            field=models.CharField(blank=True, help_text='Display title for the question', max_length=255),
        ),
        
        # Add requirements field to Question
        migrations.AddField(
            model_name='question',
            name='requirements',
            field=models.JSONField(blank=True, default=list, help_text='List of requirements/instructions for the task'),
        ),
        
        # Add tips field to Question
        migrations.AddField(
            model_name='question',
            name='tips',
            field=models.JSONField(blank=True, default=list, help_text='List of helpful tips for completing the task'),
        ),
        
        # Add exam FK to Question
        migrations.AddField(
            model_name='question',
            name='exam',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='team7.exam'),
        ),
    ]
