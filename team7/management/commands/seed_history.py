"""
Django management command to seed test evaluation history data into the database.
Creates 10 writing and 10 speaking evaluation records with fake data for testing.

Usage:
    python manage.py seed_history                           # Uses a default test user UUID
    python manage.py seed_history --user-id YOUR_UUID       # Uses a specific user UUID
    python manage.py seed_history --list-users              # Lists all available users
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random
import uuid as uuid_lib
from team7.models import Exam, Question, Evaluation, DetailedScore, TaskType
from core.models import User


class Command(BaseCommand):
    help = 'Seed test evaluation history data into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=str,
            help='UUID of the user to seed history for'
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='List all available users'
        )

    def handle(self, *args, **options):
        # Handle list-users command
        if options.get('list_users'):
            self.list_users()
            return
        
        # Get user ID
        user_id = options.get('user_id')
        if not user_id:
            # Try to get the first user
            first_user = User.objects.first()
            if first_user:
                user_id = str(first_user.id)
                self.stdout.write(f'No user specified. Using first user: {user_id}')
            else:
                self.stdout.write(self.style.ERROR('No users found in database! Please create a user first.'))
                self.stdout.write('Run: python manage.py createsuperuser')
                return
        
        self.stdout.write(f'Starting to seed test history data for user: {user_id}')
        
        with transaction.atomic():
            self.seed_writing_history(user_id)
            self.seed_speaking_history(user_id)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded test history data for user {user_id}'))
    
    def list_users(self):
        """List all users in the system"""
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('No users found in database'))
            return
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('Available Users:')
        self.stdout.write('=' * 80)
        
        for user in users:
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'UUID: {user.id}')
            self.stdout.write(f'Name: {user.first_name} {user.last_name}')
            self.stdout.write('-' * 80)
        
        self.stdout.write(f'Total: {users.count()} user(s)\n')

    def seed_writing_history(self, user_id):
        """Seed 10 writing evaluation records"""
        # Get a writing question to link to
        writing_question = Question.objects.filter(task_type=TaskType.WRITING).first()
        if not writing_question:
            self.stdout.write(self.style.WARNING('No writing questions found, skipping writing history'))
            return
        
        for i in range(10):
            # Create evaluation with random data
            eval_score = round(random.uniform(2.0, 5.0), 1)
            days_ago = random.randint(0, 60)
            
            evaluation = Evaluation.objects.create(
                user_id=user_id,
                question=writing_question,
                task_type=TaskType.WRITING,
                submitted_text=self._generate_essay(),
                overall_score=eval_score,
                ai_feedback=self._generate_feedback('writing'),
                created_at=timezone.now() - timedelta(days=days_ago)
            )
            
            # Add detailed scores
            criteria = ['Grammar', 'Vocabulary', 'Organization', 'Topic Development']
            for criterion in criteria:
                DetailedScore.objects.create(
                    evaluation=evaluation,
                    criterion=criterion,
                    score_value=round(random.uniform(2.0, 5.0), 1),
                    comment=f'Good performance in {criterion}'
                )
            
            self.stdout.write(f'Created writing evaluation {i+1}/10')

    def seed_speaking_history(self, user_id):
        """Seed 10 speaking evaluation records"""
        # Get a speaking question to link to
        speaking_question = Question.objects.filter(task_type=TaskType.SPEAKING).first()
        if not speaking_question:
            self.stdout.write(self.style.WARNING('No speaking questions found, skipping speaking history'))
            return
        
        for i in range(10):
            # Create evaluation with random data
            eval_score = round(random.uniform(2.0, 5.0), 1)
            days_ago = random.randint(0, 60)
            
            evaluation = Evaluation.objects.create(
                user_id=user_id,
                question=speaking_question,
                task_type=TaskType.SPEAKING,
                audio_path=f'/media/audio/speaking_test_{i}.wav',
                transcript_text=self._generate_transcript(),
                overall_score=eval_score,
                ai_feedback=self._generate_feedback('speaking'),
                created_at=timezone.now() - timedelta(days=days_ago)
            )
            
            # Add detailed scores
            criteria = ['Delivery', 'Language Use', 'Fluency', 'Coherence']
            for criterion in criteria:
                DetailedScore.objects.create(
                    evaluation=evaluation,
                    criterion=criterion,
                    score_value=round(random.uniform(2.0, 5.0), 1),
                    comment=f'Good performance in {criterion}'
                )
            
            self.stdout.write(f'Created speaking evaluation {i+1}/10')

    def _generate_essay(self):
        """Generate a sample essay text"""
        essays = [
            "Technology has revolutionized modern education in many ways. First, it provides access to unlimited information and resources. Second, it enables interactive learning experiences. Finally, technology allows for personalized education paths tailored to individual needs. However, we must also consider the challenges such as digital divide and screen fatigue.",
            "Online education offers several advantages over traditional classroom learning. Students can learn at their own pace and schedule. Additionally, there is no need for commuting, saving time and money. Interactive online platforms provide engaging learning experiences. Nevertheless, the lack of face-to-face interaction remains a significant concern.",
            "Global warming is one of the most pressing issues of our time. Rising temperatures affect weather patterns, causing more frequent natural disasters. The melting of polar ice caps threatens coastal cities. We must adopt renewable energy sources and reduce carbon emissions. International cooperation is essential to address this challenge.",
            "The importance of mental health cannot be overstated. Mental health affects our relationships, work performance, and overall quality of life. Society must reduce stigma around mental illness and provide better access to mental healthcare. Schools should include mental health education in their curriculum.",
            "Artificial intelligence is transforming various industries including healthcare, transportation, and finance. AI can improve diagnostic accuracy in medicine and enhance productivity. However, we must address concerns about job displacement and ethical use of AI data.",
            "Social media has become an integral part of modern society, connecting billions of people worldwide. While it enables communication and business opportunities, excessive use can lead to addiction and mental health issues. We need to establish healthy guidelines for social media usage.",
            "Remote work has become increasingly popular, especially post-pandemic. It offers flexibility and reduces office overhead costs. However, isolation and difficulty in collaboration can be challenges. A hybrid model might be the best approach.",
            "Renewable energy sources like solar and wind power are crucial for sustainable development. They reduce carbon emissions and create new job opportunities. Investment in renewable energy infrastructure is essential for a green future.",
            "Education should focus on developing critical thinking skills rather than rote memorization. Students need to learn how to analyze information, solve problems, and adapt to changing circumstances. This prepares them better for modern careers.",
            "Cybersecurity is increasingly important as more aspects of life move online. Protecting personal data and preventing cyber attacks requires strong security measures. Individuals and organizations must invest in cybersecurity awareness and infrastructure."
        ]
        return random.choice(essays)

    def _generate_transcript(self):
        """Generate a sample transcript text"""
        transcripts = [
            "I really enjoyed that speaking task. Let me describe a memorable experience from my childhood. When I was about ten years old, I went on a trip to the mountains with my family. It was an amazing adventure where we hiked through beautiful landscapes and stayed in a small village. The local people were very friendly and helped us understand their culture better.",
            "Thank you for this opportunity. I would like to talk about an important person in my life. My teacher had a significant impact on my academic journey. She was very patient and always encouraged us to think critically. Her dedication to teaching inspired me to pursue further education.",
            "Technology has changed our lives dramatically. For example, smartphones allow us to stay connected with people across the world. Online learning platforms have made education more accessible. However, we must balance technology use with real-world interaction.",
            "I think environmental conservation is crucial for our future. We should support renewable energy and reduce plastic consumption. Individuals can contribute by recycling and making sustainable choices in their daily lives.",
            "Social interactions are important for personal development. Working in teams teaches us collaboration and communication skills. Building relationships helps us grow emotionally and intellectually.",
            "I believe education should be practical and relevant to real life. Students should learn skills that are applicable in the job market. Combining theoretical knowledge with practical experience is the best approach.",
            "Traveling has broadened my perspective on different cultures. I visited several countries and learned about their unique traditions and values. These experiences made me more empathetic and understanding of global diversity.",
            "Work-life balance is essential for well-being. People should have time for family, hobbies, and rest. Companies should support flexible working arrangements to help employees maintain a healthy balance.",
            "I think innovation drives progress in society. New technologies and ideas help us solve problems more efficiently. Encouraging creativity and experimentation is important in schools and workplaces.",
            "Health is the most important aspect of life. We should exercise regularly and maintain a balanced diet. Mental health is equally important, so we should seek help when needed and support others."
        ]
        return random.choice(transcripts)

    def _generate_feedback(self, exam_type):
        """Generate sample feedback"""
        writing_feedbacks = [
            "Your essay demonstrates good organization and clear main ideas. Consider adding more specific examples to strengthen your arguments.",
            "Excellent use of vocabulary and varied sentence structures. Pay attention to minor grammar issues in some sentences.",
            "Strong thesis statement and logical progression of ideas. The conclusion effectively summarizes your main points.",
            "Good attempt at balancing multiple perspectives. Provide more detailed evidence to support each claim.",
            "Clear writing style that is easy to follow. Consider developing your supporting paragraphs with more depth.",
        ]
        
        speaking_feedbacks = [
            "Good fluency and clear pronunciation. Work on varying your intonation and speaking pace for more engagement.",
            "Excellent vocabulary and natural speech patterns. Minor grammar mistakes did not affect overall understanding.",
            "Clear and organized response with good examples. Slow down occasionally to ensure better articulation.",
            "Confident delivery with appropriate use of linking words. Add more specific details to strengthen your response.",
            "Good coherence and logical flow of ideas. Practice speaking more smoothly to reduce hesitation.",
        ]
        
        if exam_type == 'writing':
            return random.choice(writing_feedbacks)
        else:
            return random.choice(speaking_feedbacks)
