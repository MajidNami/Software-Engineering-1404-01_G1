from django.db import migrations


def set_writing_min_word_count(apps, schema_editor):
    Question = apps.get_model('team11', 'Question')
    Question.objects.filter(category__question_type='writing').update(min_word_count=150)


class Migration(migrations.Migration):

    dependencies = [
        ('team11', '0005_speakingsubmission_and_more'),
    ]

    operations = [
        migrations.RunPython(set_writing_min_word_count, migrations.RunPython.noop),
    ]
