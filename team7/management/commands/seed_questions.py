"""
Django management command to seed exam and question data into the database.
Populates both writing and speaking exams with their questions, based on mock data structure.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from team7.models import Exam, Question, TaskType


class Command(BaseCommand):
    help = 'Seed exam and question data into the database'

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed exams and questions...')
        
        with transaction.atomic():
            self.seed_writing_exams()
            self.seed_speaking_exams()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded all exams and questions'))

    def seed_writing_exams(self):
        """Seed writing exams and their questions"""
        writing_exams = [
            {
                'title': 'Formal Letter',
                'exam_type': TaskType.WRITING,
                'total_time': 1200,
                'difficulty': 1,
                'questions': [
                    {
                        'title': 'Task 1: Formal Letter',
                        'prompt_text': 'You want to apply for a scholarship at an international university. Write a formal letter to request more information about the scholarship programs.',
                        'requirements': [
                            'Write 50-150 words',
                            'Start the letter with proper greeting and salutation',
                            'Clearly state your purpose',
                            'End the letter with respectful closing'
                        ],
                        'tips': [
                            'Follow the structure of a formal letter',
                            'Use formal and respectful language',
                            'Write the letter neatly and readably',
                            'Proofread the letter before sending'
                        ]
                    },
                    {
                        'title': 'Task 2: Complaint Letter',
                        'prompt_text': 'You recently purchased a product online but it arrived defective. Write a formal letter to the seller, describe the problem, and request a replacement or refund.',
                        'requirements': [
                            'Write 50-150 words',
                            'Explain the problem in detail',
                            'Suggest an appropriate solution',
                            'End the letter formally'
                        ],
                        'tips': [
                            'First explain the current situation',
                            'Specify the expected resolution steps',
                            'Use polite and courteous phrases',
                            'Allow reasonable time for response'
                        ]
                    }
                ]
            },
            {
                'title': 'Academic Text Analysis',
                'exam_type': TaskType.WRITING,
                'total_time': 1500,
                'difficulty': 2,
                'questions': [
                    {
                        'title': 'Task 1: Academic Text Analysis',
                        'prompt_text': 'Recent research shows that artificial intelligence technology has a profound impact on the education system. This technology has not only changed teaching methods but also transformed how students learn. On one hand, the use of smart educational systems has made personalized learning possible. On the other hand, increased dependence on technology can affect students\' social skills.',
                        'requirements': [
                            'Write 50-150 words',
                            'Identify the main idea',
                            'Examine evidence and sources',
                            'Provide logical conclusion'
                        ],
                        'tips': [
                            'Read the text carefully and note the main ideas',
                            'Distinguish between main and supporting ideas',
                            'Support your position with evidence',
                            'Write your analysis logically and coherently'
                        ]
                    }
                ]
            },
            {
                'title': 'Improvement Proposal',
                'exam_type': TaskType.WRITING,
                'total_time': 1200,
                'difficulty': 2,
                'questions': [
                    {
                        'title': 'Task 1: Write an Improvement Proposal',
                        'prompt_text': 'You work in a company. The company\'s time management system is very outdated and causes many problems for employees. Write a proposal for improving this system.',
                        'requirements': [
                            'Write 50-150 words',
                            'Describe the current problems',
                            'Propose a detailed solution',
                            'Explain the benefits of your proposal'
                        ],
                        'tips': [
                            'Start with an attention-grabbing opening',
                            'Explain problems with real examples',
                            'Present the solution step-by-step',
                            'End with a request for a follow-up meeting'
                        ]
                    },
                    {
                        'title': 'Task 2: Letter of Recommendation',
                        'prompt_text': 'Your friend has applied for a job at a prestigious company. You have been asked to write a letter of recommendation for them. In this letter, describe their abilities and positive qualities.',
                        'requirements': [
                            'Write 50-150 words',
                            'Discuss your friend\'s qualities and abilities',
                            'Provide specific examples of their work',
                            'End the letter with a strong recommendation'
                        ],
                        'tips': [
                            'Write the letter formally and respectfully',
                            'Highlight specific experience and skills',
                            'Give real examples of good performance',
                            'End with a request for follow-up'
                        ]
                    }
                ]
            },
            {
                'title': 'Opinion Statement and Defense',
                'exam_type': TaskType.WRITING,
                'total_time': 1400,
                'difficulty': 3,
                'questions': [
                    {
                        'title': 'Task 1: Defend a Claim',
                        'prompt_text': 'Do you believe that online education is as effective as in-person education? State your opinion.',
                        'requirements': [
                            'Write 50-150 words',
                            'Clearly state your opinion',
                            'Provide at least three reasons to support your opinion',
                            'Address potential objections'
                        ],
                        'tips': [
                            'Take a clear and definitive position',
                            'Provide logical reasons',
                            'Use practical examples',
                            'Write a strong conclusion'
                        ]
                    },
                    {
                        'title': 'Task 2: Compare Two Solutions',
                        'prompt_text': 'To reduce city traffic, two solutions exist: 1) Increase and improve public transportation, 2) Restrict private cars from entering the city center. Which solution is better?',
                        'requirements': [
                            'Write 50-150 words',
                            'Analyze both solutions',
                            'Compare advantages and disadvantages',
                            'Justify your choice'
                        ],
                        'tips': [
                            'Examine both sides objectively',
                            'Name actual pros and cons',
                            'Use real-world examples',
                            'Support your conclusion with logical reasoning'
                        ]
                    }
                ]
            }
        ]
        
        for exam_data in writing_exams:
            questions_data = exam_data.pop('questions')
            exam = Exam.objects.create(
                title=exam_data['title'],
                exam_type=exam_data['exam_type'],
                total_time=exam_data['total_time'],
                total_questions=len(questions_data),
                difficulty=exam_data['difficulty']
            )
            
            for question_data in questions_data:
                Question.objects.create(
                    title=question_data['title'],
                    prompt_text=question_data['prompt_text'],
                    task_type=TaskType.WRITING,
                    mode='independent',
                    requirements=question_data.get('requirements', []),
                    tips=question_data.get('tips', []),
                    exam=exam
                )
            
            self.stdout.write(f'Created exam: {exam.title} with {len(questions_data)} questions')

    def seed_speaking_exams(self):
        """Seed speaking exams and their questions"""
        speaking_exams = [
            {
                'title': 'Describe a Personal Experience',
                'exam_type': TaskType.SPEAKING,
                'total_time': 900,
                'difficulty': 1,
                'questions': [
                    {
                        'title': 'Part 1: Personal Question',
                        'prompt_text': 'Talk about a teacher who had a positive impact on your life. Explain what this teacher did and why this impact was important to you.',
                        'requirements': [
                            'Introduce the teacher',
                            'Explain what they did',
                            'Describe their impact on your life',
                            'Speak clearly and fluently'
                        ],
                        'tips': [
                            'Use the preparation time to note key points',
                            'Organize your answer logically',
                            'Use specific examples',
                            'Speak calmly and confidently'
                        ]
                    },
                    {
                        'title': 'Part 2: Tell a Story',
                        'prompt_text': 'Talk about a memorable trip. Explain where you went, who was with you, what you did, and why that trip was special to you.',
                        'requirements': [
                            'Explain your destination',
                            'Introduce your travel companions',
                            'Describe the activities you did',
                            'Express your feelings and impressions'
                        ],
                        'tips': [
                            'Follow chronological order',
                            'Include interesting and engaging details',
                            'Use proper transitions',
                            'Vary your tone and pace'
                        ]
                    }
                ]
            },
            {
                'title': 'Discussion and Analysis',
                'exam_type': TaskType.SPEAKING,
                'total_time': 1200,
                'difficulty': 2,
                'questions': [
                    {
                        'title': 'Part 1: Problem Analysis',
                        'prompt_text': 'Many young people migrate to large cities for education and employment. Discuss this issue in small towns. Analyze the advantages and disadvantages of this migration.',
                        'requirements': [
                            'Define the problem clearly',
                            'Mention the advantages',
                            'Mention the disadvantages',
                            'Provide a solution or personal opinion'
                        ],
                        'tips': [
                            'Understand the topic well',
                            'Use real examples',
                            'Consider both sides of the issue',
                            'Stay focused on the main topic'
                        ]
                    }
                ]
            },
            {
                'title': 'Documenting Work Experience',
                'exam_type': TaskType.SPEAKING,
                'total_time': 900,
                'difficulty': 2,
                'questions': [
                    {
                        'title': 'Part 1: Explain Work Experience',
                        'prompt_text': 'Talk about one of your biggest work challenges that you successfully solved. What was the challenge, how did you face it, and what was the final result?',
                        'requirements': [
                            'Define the challenge clearly',
                            'Describe your actions',
                            'Explain the problem-solving process',
                            'State the result and lessons learned'
                        ],
                        'tips': [
                            'Use a real example',
                            'Maintain chronological order',
                            'Highlight your role',
                            'Emphasize positive results'
                        ]
                    },
                    {
                        'title': 'Part 2: Leadership and Teamwork',
                        'prompt_text': 'Talk about a time when you led a project or team. What was the project, what challenges did you face, and how did you guide your team to success?',
                        'requirements': [
                            'Describe the project clearly',
                            'Explain your leadership role',
                            'Describe how you motivated the team',
                            'State the results and achievements'
                        ],
                        'tips': [
                            'Emphasize your leadership abilities',
                            'Give specific examples of decisions',
                            'Talk about communication skills',
                            'Mention economic or operational results'
                        ]
                    }
                ]
            },
            {
                'title': 'Cultural and Social Perspectives',
                'exam_type': TaskType.SPEAKING,
                'total_time': 1050,
                'difficulty': 3,
                'questions': [
                    {
                        'title': 'Part 1: Cultural Difference',
                        'prompt_text': 'Choose an important cultural difference. Explain it, why you think this difference exists, and whether this difference is positive or negative for you.',
                        'requirements': [
                            'Describe the difference clearly',
                            'Explain its historical or cultural roots',
                            'Discuss its effects',
                            'Share your personal opinion'
                        ],
                        'tips': [
                            'Show respect for different cultures',
                            'Provide practical examples',
                            'Talk about research or personal experience',
                            'Provide a balanced conclusion'
                        ]
                    },
                    {
                        'title': 'Part 2: Social Issue',
                        'prompt_text': 'Choose an important social issue (such as climate change, educational inequality, or mental health). Explain it and share your opinion.',
                        'requirements': [
                            'Define the issue',
                            'Explain why it matters',
                            'Discuss its social impact',
                            'Suggest possible solutions'
                        ],
                        'tips': [
                            'Choose a specific topic',
                            'Reference statistics or evidence',
                            'Consider different perspectives',
                            'Call for action'
                        ]
                    }
                ]
            }
        ]
        
        for exam_data in speaking_exams:
            questions_data = exam_data.pop('questions')
            exam = Exam.objects.create(
                title=exam_data['title'],
                exam_type=exam_data['exam_type'],
                total_time=exam_data['total_time'],
                total_questions=len(questions_data),
                difficulty=exam_data['difficulty']
            )
            
            for question_data in questions_data:
                Question.objects.create(
                    title=question_data['title'],
                    prompt_text=question_data['prompt_text'],
                    task_type=TaskType.SPEAKING,
                    mode='independent',
                    requirements=question_data.get('requirements', []),
                    tips=question_data.get('tips', []),
                    exam=exam
                )
            
            self.stdout.write(f'Created exam: {exam.title} with {len(questions_data)} questions')
