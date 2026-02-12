"""
Create sample listening tests, items, questions and options.
Run: python manage.py load_sample_data
Creates 1 test with 5 items (stages), each with 5 questions (25 questions total).
"""
from django.core.management.base import BaseCommand
from listening.models import ListeningTest, ListeningItem, Question, ChoiceOption


def add_options(question, correct_label, options_texts):
    labels = ['A', 'B', 'C', 'D']
    for i, (label, text) in enumerate(zip(labels, options_texts)):
        ChoiceOption.objects.create(
            question=question,
            label=label,
            text=text,
            is_correct=(label == correct_label),
            order=i + 1,
        )


# Conversations (two people): each with 5 questions. Used for stages 1 and 3.
CONVERSATIONS = [
    {
        'topic': 'Student & Professor - Office Hours',
        'transcript': """Narrator: Listen to a conversation between a student and a professor.
Student: Hi, Professor Martinez. Do you have a minute? I'm confused about the assignment for next week.
Professor: Of course. Which part is unclear?
Student: The essay—you said we need two primary sources, but the library database only shows one that's relevant to my topic.
Professor: Try the archive section on the second floor. They have older documents that aren't fully digitized. Also, you can use one primary and one secondary source if you cite the secondary properly.
Student: So one primary and one secondary would be okay?
Professor: Yes. Just make sure the secondary source is academic—a journal article or a book from a university press, not a website.
Student: Thanks, that helps a lot.""",
        'questions': [
            ('Why does the student go to see the professor?', 'main_idea', 'B',
             ['To get a book.', 'To clarify the assignment requirements.', 'To hand in an essay.', 'To discuss the library.']),
            ('What does the professor suggest about the library?', 'detail', 'C',
             ['Avoid the second floor.', 'Use only the database.', 'Check the archive section on the second floor.', 'Everything is digitized.']),
            ('According to the professor, what is acceptable for the assignment?', 'detail', 'A',
             ['One primary and one academic secondary source.', 'Only primary sources.', 'Any website.', 'Only books.']),
            ('What can be inferred about the student\'s topic?', 'inference', 'D',
             ['It is too narrow.', 'The professor dislikes it.', 'There are too many sources.', 'Relevant primary sources may be limited.']),
            ('Why does the professor mention a university press?', 'pragmatic', 'B',
             ['To recommend a publisher.', 'To give an example of an acceptable secondary source.', 'To discuss careers.', 'To explain archives.']),
        ],
    },
    {
        'topic': 'Two Students - Campus Cafeteria',
        'transcript': """Narrator: Listen to a conversation between two students at the campus cafeteria.
Lisa: I can't believe we have three exams in one week. How are you managing?
Jake: I'm not. I've been pulling all-nighters. I wish I'd spread my study schedule out.
Lisa: Same. I heard the study group for Biology meets on Tuesdays. Maybe we could join and split the material.
Jake: Good idea. But isn't the library closed late on Tuesdays?
Lisa: Yeah, but the student center stays open until midnight. We could book a room there. I'll check if there's space.
Jake: Perfect. And we still have to finish that lab report for Thursday.
Lisa: Right. I'll do the graphs if you write the analysis. We can swap drafts tomorrow.
Jake: Deal. Let's meet at the student center at seven.""",
        'questions': [
            ('What is the conversation mainly about?', 'main_idea', 'C',
             ['Cafeteria food.', 'Library hours.', 'Managing exams and coordinating study plans.', 'Lab reports only.']),
            ('What does Lisa suggest they do?', 'detail', 'A',
             ['Join a Biology study group and use the student center.', 'Study alone.', 'Skip the lab report.', 'Only meet on Thursdays.']),
            ('Why does Jake mention the library?', 'detail', 'B',
             ['To praise it.', 'To point out it might be closed when they want to study.', 'To suggest moving there.', 'To discuss booking.']),
            ('What can be inferred about the lab report?', 'inference', 'D',
             ['Only one person will do it.', 'It is not due soon.', 'They will not work together.', 'They plan to divide the work and exchange drafts.']),
            ('What do the students agree to do at the end?', 'pragmatic', 'A',
             ['Meet at the student center at seven.', 'Skip the study group.', 'Meet on Thursday only.', 'Close the library.']),
        ],
    },
]

# 10 lectures, each with 5 questions (text, type, correct_label, [A, B, C, D])
LECTURES = [
    {
        'topic': 'Biology',
        'transcript': """Narrator: Listen to part of a lecture in a biology class.
Professor: Today we'll look at how certain plants adapt to dry environments. One key mechanism is crassulacean acid metabolism, or CAM. In CAM plants, the stomata open at night to take in carbon dioxide and close during the day to reduce water loss. The cactus is a classic example. Other CAM plants include pineapple and agave. By storing CO2 at night and using it for photosynthesis during the day, these plants can survive with very little water.""",
        'questions': [
            ('What is the main idea of the lecture?', 'main_idea', 'C',
             ['Cacti are the only plants that survive in deserts.', 'Stomata always open during the day.',
              'CAM allows plants to conserve water in dry environments.', 'Pineapple and agave are not related to cacti.']),
            ('When do CAM plants open their stomata?', 'detail', 'B',
             ['Only in the morning.', 'At night.', 'During the afternoon.', 'They never close.']),
            ('According to the professor, which is an example of a CAM plant?', 'detail', 'A',
             ['Cactus.', 'Oak tree.', 'Rose.', 'Fern.']),
            ('What can be inferred about photosynthesis in CAM plants?', 'inference', 'D',
             ['It does not require CO2.', 'It happens only at night.', 'It is slower than in other plants.', 'It uses CO2 stored at night.']),
            ('Why does the professor mention pineapple and agave?', 'organization', 'B',
             ['To contrast them with cacti.', 'To give more examples of CAM plants.', 'To discuss tropical agriculture.', 'To explain crop rotation.']),
        ],
    },
    {
        'topic': 'History',
        'transcript': """Narrator: Listen to part of a lecture in a history class.
Professor: The Silk Road was not a single road but a network of trade routes connecting East and West. Silk was one of the main commodities, but spices, glass, and ideas also traveled along these routes. Buddhism spread from India to China largely through Silk Road contact. The routes declined when sea trade became safer and faster. Marco Polo's travels in the 13th century were along these same networks.""",
        'questions': [
            ('What is the main point of the lecture?', 'main_idea', 'B',
             ['Silk was the only product traded.', 'The Silk Road was a network that moved goods and ideas.', 'Marco Polo built the Silk Road.', 'Sea trade caused the Silk Road to open.']),
            ('According to the professor, what besides goods traveled the Silk Road?', 'detail', 'C',
             ['Soldiers.', 'Disease only.', 'Ideas and religion.', 'Gold and silver only.']),
            ('Why did the Silk Road decline?', 'detail', 'A',
             ['Sea trade became safer and faster.', 'War destroyed the routes.', 'Silk became worthless.', 'Marco Polo died.']),
            ('What can be inferred about Buddhism and the Silk Road?', 'inference', 'D',
             ['Buddhism ended trade.', 'Buddhism was only in India.', 'The Silk Road was built for Buddhism.', 'Contact along the routes helped spread Buddhism.']),
            ('Why does the professor mention Marco Polo?', 'organization', 'B',
             ['To criticize his accounts.', 'To connect the routes to a well-known traveler.', 'To discuss the 13th century.', 'To compare land and sea travel.']),
        ],
    },
    {
        'topic': 'Psychology',
        'transcript': """Narrator: Listen to part of a lecture in a psychology class.
Professor: Classical conditioning was first demonstrated by Ivan Pavlov. He noticed that dogs salivated not only when they saw food but also when they heard the footsteps of the person who fed them. He then paired a neutral stimulus—a bell—with the presentation of food. After repeated pairings, the dogs salivated at the sound of the bell alone. The bell had become a conditioned stimulus. This principle has been used in advertising, education, and therapy.""",
        'questions': [
            ('What is the lecture mainly about?', 'main_idea', 'A',
             ['How a neutral stimulus can become associated with a response.', 'Why dogs are used in experiments.', 'The history of advertising.', 'Food and digestion.']),
            ('What did Pavlov use as a neutral stimulus?', 'detail', 'B',
             ['Food.', 'A bell.', 'Footsteps.', 'A light.']),
            ('According to the professor, where has classical conditioning been applied?', 'detail', 'D',
             ['Only in labs.', 'Only with animals.', 'Only in Russia.', 'In advertising, education, and therapy.']),
            ('What can be inferred about the dogs before the experiment?', 'inference', 'C',
             ['They did not like bells.', 'They were hungry all the time.', 'The bell initially did not cause salivation.', 'They were trained to eat on command.']),
            ('Why does the professor mention footsteps?', 'pragmatic', 'A',
             ['To show the dogs had already begun to associate a sound with food.', 'To explain why Pavlov used a bell.', 'To discuss the lab setting.', 'To compare different stimuli.']),
        ],
    },
    {
        'topic': 'Astronomy',
        'transcript': """Narrator: Listen to part of a lecture in an astronomy class.
Professor: Black holes are regions of spacetime where gravity is so strong that nothing, not even light, can escape. They form when massive stars collapse at the end of their life cycle. The boundary beyond which nothing can escape is called the event horizon. Although we cannot see black holes directly, we detect them by observing their effects on nearby matter and light. Supermassive black holes are thought to exist at the centers of most galaxies.""",
        'questions': [
            ('What is the main idea of the lecture?', 'main_idea', 'B',
             ['Light can escape black holes.', 'Black holes are regions where gravity prevents escape.', 'All stars become black holes.', 'Galaxies have no center.']),
            ('What is the event horizon?', 'detail', 'C',
             ['The center of a black hole.', 'A type of star.', 'The boundary beyond which nothing can escape.', 'A galaxy.']),
            ('How do scientists detect black holes?', 'detail', 'A',
             ['By observing their effects on nearby matter and light.', 'By sending probes into them.', 'By seeing them directly.', 'By measuring gravity on Earth.']),
            ('What can be inferred about massive stars?', 'inference', 'D',
             ['They never die.', 'They always become visible.', 'They do not have gravity.', 'They can collapse and form black holes.']),
            ('Why does the professor mention galaxies?', 'organization', 'B',
             ['To contrast them with black holes.', 'To note that supermassive black holes may be at their centers.', 'To discuss the Milky Way only.', 'To explain the event horizon.']),
        ],
    },
    {
        'topic': 'Environmental Science',
        'transcript': """Narrator: Listen to part of a lecture in an environmental science class.
Professor: Coral reefs are often called the rainforests of the sea. They support a huge diversity of life and protect coastlines from erosion. Coral bleaching occurs when water temperatures rise and the coral expels the symbiotic algae living in its tissues, causing it to turn white. Without the algae, the coral may die. Ocean acidification, caused by increased CO2 absorption, weakens coral skeletons. Both warming and acidification threaten reef survival worldwide.""",
        'questions': [
            ('What is the lecture mainly about?', 'main_idea', 'C',
             ['Rainforests and coral.', 'Coastline erosion only.', 'Coral reefs and threats to their survival.', 'Algae and fish.']),
            ('What causes coral bleaching?', 'detail', 'B',
             ['Pollution only.', 'Rising water temperatures.', 'Too many fish.', 'Ocean currents.']),
            ('What is ocean acidification linked to?', 'detail', 'A',
             ['Increased CO2 absorption by the ocean.', 'Coral reproduction.', 'Algae growth.', 'Coastal development.']),
            ('What can be inferred when coral expels its algae?', 'inference', 'D',
             ['The coral is healthy.', 'The water is too cold.', 'The coral is growing.', 'The coral is under stress and may die.']),
            ('Why does the professor compare reefs to rainforests?', 'organization', 'B',
             ['They are on land.', 'Both support high biodiversity.', 'They have the same climate.', 'They are the same age.']),
        ],
    },
    {
        'topic': 'Economics',
        'transcript': """Narrator: Listen to part of a lecture in an economics class.
Professor: Supply and demand determine market price. When demand exceeds supply, prices tend to rise. When supply exceeds demand, prices tend to fall. Elasticity measures how much quantity demanded or supplied changes when price changes. Inelastic goods, like basic food or medicine, see relatively small changes in quantity when price changes. Governments sometimes set price ceilings or floors to protect consumers or producers.""",
        'questions': [
            ('What is the main point of the lecture?', 'main_idea', 'A',
             ['Supply and demand affect price; elasticity and policy can too.', 'Prices never change.', 'Governments always set prices.', 'Elasticity is the same for all goods.']),
            ('When do prices tend to rise?', 'detail', 'B',
             ['When supply exceeds demand.', 'When demand exceeds supply.', 'When elasticity is low.', 'When there are no governments.']),
            ('What are inelastic goods?', 'detail', 'C',
             ['Goods that change a lot with price.', 'Goods with no demand.', 'Goods whose quantity changes little when price changes.', 'Goods that are illegal.']),
            ('What can be inferred about price ceilings?', 'inference', 'D',
             ['They always help producers.', 'They have no effect.', 'They raise prices.', 'They are used to try to help some groups.']),
            ('Why does the professor mention medicine?', 'pragmatic', 'A',
             ['As an example of an inelastic good.', 'To discuss healthcare policy.', 'To compare with food.', 'To explain supply.']),
        ],
    },
    {
        'topic': 'Literature',
        'transcript': """Narrator: Listen to part of a lecture in a literature class.
Professor: The unreliable narrator is a character who tells the story but whose account the reader cannot fully trust. They may be lying, mistaken, or biased. This technique creates tension and makes the reader work to interpret events. Famous examples include the narrator in Poe's "The Tell-Tale Heart" and the narrator in Gillian Flynn's "Gone Girl." It forces us to question what really happened and to think about perspective and truth in storytelling.""",
        'questions': [
            ('What is the lecture mainly about?', 'main_idea', 'C',
             ['Poe and Flynn.', 'How to write stories.', 'The unreliable narrator as a literary technique.', 'Truth in real life.']),
            ('According to the professor, why might a narrator be unreliable?', 'detail', 'B',
             ['They are always the hero.', 'They may be lying, mistaken, or biased.', 'They never speak.', 'They are not characters.']),
            ('What effect does an unreliable narrator have?', 'detail', 'A',
             ['It can create tension and make the reader interpret.', 'It makes the story shorter.', 'It guarantees the truth.', 'It removes perspective.']),
            ('What can be inferred about "The Tell-Tale Heart"?', 'inference', 'D',
             ['It has no narrator.', 'The narrator is fully trusted.', 'It is not literature.', 'The narrator may not be trustworthy.']),
            ('Why does the professor mention "Gone Girl"?', 'organization', 'B',
             ['To criticize it.', 'As another example of an unreliable narrator.', 'To discuss film only.', 'To define perspective.']),
        ],
    },
    {
        'topic': 'Geology',
        'transcript': """Narrator: Listen to part of a lecture in a geology class.
Professor: Plate tectonics explains the movement of Earth's lithosphere. The lithosphere is broken into plates that float on the asthenosphere. Where plates meet, we get earthquakes, volcanoes, and mountain building. Divergent boundaries are where plates move apart, like at the Mid-Atlantic Ridge. Convergent boundaries are where plates collide; one may subduct under the other. Transform boundaries are where plates slide past each other, like the San Andreas Fault.""",
        'questions': [
            ('What is the main idea of the lecture?', 'main_idea', 'A',
             ['Plate tectonics explains lithosphere movement and geologic activity.', 'Earthquakes only happen in one place.', 'The asthenosphere does not move.', 'Plates are all the same size.']),
            ('What happens at divergent boundaries?', 'detail', 'C',
             ['Plates collide.', 'Plates slide past each other.', 'Plates move apart.', 'Nothing.']),
            ('Where is the San Andreas Fault an example of?', 'detail', 'D',
             ['Divergent boundary.', 'Convergent boundary.', 'Subduction.', 'Transform boundary.']),
            ('What can be inferred about the Mid-Atlantic Ridge?', 'inference', 'B',
             ['It is where plates collide.', 'It is a place where plates are moving apart.', 'It is not related to plates.', 'It is on land only.']),
            ('Why does the professor mention subduction?', 'organization', 'A',
             ['To describe what can happen at convergent boundaries.', 'To define the lithosphere.', 'To explain the San Andreas Fault.', 'To discuss the Mid-Atlantic Ridge.']),
        ],
    },
    {
        'topic': 'Sociology',
        'transcript': """Narrator: Listen to part of a lecture in a sociology class.
Professor: Social norms are unwritten rules that guide behavior in a group. They vary by culture and context. Norms can be formal, like laws, or informal, like etiquette. When someone breaks a norm, they may face sanctions—from a frown to legal punishment. Norms help maintain order and predictability. Studying how norms form and change helps us understand society and why people conform or deviate.""",
        'questions': [
            ('What is the lecture mainly about?', 'main_idea', 'B',
             ['Laws only.', 'Social norms and their role in society.', 'Punishment only.', 'Individual behavior only.']),
            ('According to the professor, what are social norms?', 'detail', 'C',
             ['Always written down.', 'The same in every culture.', 'Unwritten rules that guide behavior.', 'Only about law.']),
            ('What can happen when someone breaks a norm?', 'detail', 'A',
             ['They may face sanctions.', 'Nothing.', 'They are always arrested.', 'Norms change immediately.']),
            ('What can be inferred about norms and order?', 'inference', 'D',
             ['Norms cause chaos.', 'Norms are unimportant.', 'Only laws matter.', 'Norms help maintain order and predictability.']),
            ('Why does the professor mention etiquette?', 'pragmatic', 'B',
             ['To define law.', 'As an example of informal norms.', 'To discuss culture only.', 'To explain sanctions.']),
        ],
    },
    {
        'topic': 'Physics',
        'transcript': """Narrator: Listen to part of a lecture in a physics class.
Professor: Newton's first law says that an object at rest stays at rest and an object in motion stays in motion at constant velocity unless acted on by an external force. This is the law of inertia. Friction is a force that opposes motion, so in the real world objects slow down. In space, with little friction, objects can keep moving for a long time. The first law is essential for understanding how forces change motion, which we describe further in the second law.""",
        'questions': [
            ('What is the main point of the lecture?', 'main_idea', 'C',
             ['Friction is the only force.', 'Space has no motion.', 'Newton\'s first law describes inertia; objects keep their state unless a force acts.', 'Velocity never changes.']),
            ('What is inertia?', 'detail', 'A',
             ['The tendency of an object to keep its state of rest or motion.', 'A type of force.', 'The same as friction.', 'Only in space.']),
            ('Why do objects on Earth slow down?', 'detail', 'B',
             ['Because of the first law.', 'Because of forces like friction.', 'Because they have no mass.', 'Because of space.']),
            ('What can be inferred about motion in space?', 'inference', 'D',
             ['It does not exist.', 'It always stops quickly.', 'Forces are stronger there.', 'With little friction, motion can continue.']),
            ('Why does the professor mention the second law?', 'organization', 'B',
             ['To replace the first law.', 'To connect the first law to how forces change motion.', 'To define friction.', 'To discuss space only.']),
        ],
    },
]


class Command(BaseCommand):
    help = 'Load sample TOEFL Listening test: 5 stages (2 conversations, 3 lectures), 5 questions each (25 total)'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete existing tests before loading')

    def handle(self, *args, **options):
        if options.get('clear'):
            ListeningTest.objects.all().delete()
            self.stdout.write('Cleared existing tests.')

        if ListeningTest.objects.exists():
            self.stdout.write(self.style.WARNING('Tests already exist. Use --clear to replace.'))
            return

        test = ListeningTest.objects.create(
            title='REAL 1',
            version_id='v1',
            total_items=0,
            is_active=True,
        )

        # 5 stages: Conversation, Lecture, Conversation, Lecture, Lecture (25 questions total, 5 per stage)
        stage_specs = [
            (CONVERSATIONS[0], 'conversation'),
            (LECTURES[0], 'lecture'),
            (CONVERSATIONS[1], 'conversation'),
            (LECTURES[1], 'lecture'),
            (LECTURES[2], 'lecture'),
        ]
        for order, (content, item_type) in enumerate(stage_specs, start=1):
            item = ListeningItem.objects.create(
                test=test,
                difficulty='medium',
                topic_tag=content['topic'],
                transcript=content['transcript'],
                item_type=item_type,
                order=order,
            )
            for q_order, (q_text, q_type, correct, options) in enumerate(content['questions'], start=1):
                q = Question.objects.create(
                    item=item,
                    text=q_text,
                    question_type=q_type,
                    score_weight=1,
                    order=q_order,
                    explanation='',
                )
                add_options(q, correct, options)

        test.total_items = test.items.count()
        test.save(update_fields=['total_items'])

        self.stdout.write(self.style.SUCCESS(
            f'Created 1 test with 5 stages (2 conversations, 3 lectures), '
            f'{Question.objects.count()} questions, {ChoiceOption.objects.count()} options.'
        ))
