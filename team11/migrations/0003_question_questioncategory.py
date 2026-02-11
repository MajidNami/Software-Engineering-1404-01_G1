# Generated for team11 app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('team11', '0002_add_transcription'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionCategory',
            fields=[
                ('category_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('question_type', models.CharField(choices=[('writing', 'Writing'), ('listening', 'Listening')], max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'Question Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('question_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question_text', models.TextField(help_text='The prompt/question for the task')),
                ('difficulty_level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='intermediate', max_length=20)),
                ('expected_duration_seconds', models.PositiveIntegerField(blank=True, help_text='Expected time to complete (for speaking tasks)', null=True)),
                ('min_word_count', models.PositiveIntegerField(blank=True, help_text='Minimum word count (for writing tasks)', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='team11.questioncategory')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='writingsubmission',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='team11.question'),
        ),
        migrations.AddField(
            model_name='listeningsubmission',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='team11.question'),
        ),
    ]
