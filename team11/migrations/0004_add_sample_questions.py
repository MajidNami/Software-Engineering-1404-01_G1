# Generated for team11 app - Add Question Categories and Questions

from django.db import migrations
import uuid


def create_sample_data(apps, schema_editor):
    QuestionCategory = apps.get_model('team11', 'QuestionCategory')
    Question = apps.get_model('team11', 'Question')
    
    # Writing Categories
    academic_writing = QuestionCategory.objects.create(
        category_id=uuid.uuid4(),
        name='Academic Topics',
        description='TOEFL-style academic writing prompts',
        question_type='writing',
        is_active=True
    )
    
    personal_writing = QuestionCategory.objects.create(
        category_id=uuid.uuid4(),
        name='Personal Experience',
        description='Personal preference and experience topics',
        question_type='writing',
        is_active=True
    )
    
    # Speaking Categories
    personal_speaking = QuestionCategory.objects.create(
        category_id=uuid.uuid4(),
        name='Personal Preferences',
        description='TOEFL-style personal preference questions',
        question_type='listening',
        is_active=True
    )
    
    opinion_speaking = QuestionCategory.objects.create(
        category_id=uuid.uuid4(),
        name='Opinion & Reasoning',
        description='Express opinions with reasoning',
        question_type='listening',
        is_active=True
    )
    
    # Writing Questions
    writing_questions = [
        {
            'category': academic_writing,
            'text': 'Do you agree or disagree with the following statement? Technology has made the world a better place to live. Use specific reasons and examples to support your answer.',
            'difficulty': 'intermediate',
            'min_words': 300
        },
        {
            'category': academic_writing,
            'text': 'Some people prefer to work for a large company. Others prefer to work for a small company. Which would you prefer? Use specific reasons and details to support your answer.',
            'difficulty': 'intermediate',
            'min_words': 300
        },
        {
            'category': academic_writing,
            'text': 'Do you agree or disagree with the following statement? It is more important for students to study history and literature than it is for them to study science and mathematics. Use specific reasons and examples to support your opinion.',
            'difficulty': 'advanced',
            'min_words': 300
        },
        {
            'category': personal_writing,
            'text': 'Describe a person who has had a significant influence on your life. Explain why this person has been important to you.',
            'difficulty': 'beginner',
            'min_words': 250
        },
        {
            'category': personal_writing,
            'text': 'If you could change one important thing about your hometown, what would you change? Use reasons and specific examples to support your answer.',
            'difficulty': 'intermediate',
            'min_words': 300
        },
    ]
    
    for q in writing_questions:
        Question.objects.create(
            question_id=uuid.uuid4(),
            category=q['category'],
            question_text=q['text'],
            difficulty_level=q['difficulty'],
            min_word_count=q['min_words'],
            is_active=True
        )
    
    # Speaking Questions
    speaking_questions = [
        {
            'category': personal_speaking,
            'text': 'Talk about a teacher who had a positive influence on you. Describe this person and explain why he or she was important to you.',
            'difficulty': 'beginner',
            'duration': 45
        },
        {
            'category': personal_speaking,
            'text': 'Some people prefer to live in a small town. Others prefer to live in a big city. Which place would you prefer to live in? Use specific reasons and details to support your answer.',
            'difficulty': 'intermediate',
            'duration': 45
        },
        {
            'category': opinion_speaking,
            'text': 'Do you agree or disagree with the following statement? People should sometimes do things that they do not enjoy doing. Use specific reasons and examples to support your answer.',
            'difficulty': 'intermediate',
            'duration': 45
        },
        {
            'category': opinion_speaking,
            'text': 'Some people think that it is better to travel as part of a tour group when they are visiting a foreign country. Other people think that it is better to travel alone. Which do you prefer and why?',
            'difficulty': 'advanced',
            'duration': 45
        },
        {
            'category': personal_speaking,
            'text': 'Describe your ideal job. Explain why this job would be appealing to you.',
            'difficulty': 'beginner',
            'duration': 45
        },
    ]
    
    for q in speaking_questions:
        Question.objects.create(
            question_id=uuid.uuid4(),
            category=q['category'],
            question_text=q['text'],
            difficulty_level=q['difficulty'],
            expected_duration_seconds=q['duration'],
            is_active=True
        )


class Migration(migrations.Migration):

    dependencies = [
        ('team11', '0003_question_questioncategory'),
    ]

    operations = [
        migrations.RunPython(create_sample_data),
    ]
