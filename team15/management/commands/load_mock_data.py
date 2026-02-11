from django.core.management.base import BaseCommand
from team15.models import Test, Passage, Question, TestAttempt, Answer


MOCK_DATA = {
    "tests": [
        {
            "id": 1,
            "title": "TOEFL Reading Practice Test 1",
            "mode": "practice",
            "time_limit": 0,
            "is_active": True,
            "passages": [
                {
                    "title": "The History of Coffee",
                    "order": 1,
                    "content": (
                        "Coffee is one of the most widely consumed beverages in the world today, "
                        "but its origins trace back to ancient Ethiopia. According to legend, a goat "
                        "herder named Kaldi discovered coffee when he noticed his goats became unusually "
                        "energetic after eating berries from a certain tree. Kaldi reported his findings "
                        "to the abbot of a local monastery, who made a drink from the berries and found "
                        "that it kept him alert during long hours of evening prayer.\n\n"
                        "Word of the energizing effects of these berries spread rapidly. By the 15th century, "
                        "coffee was being cultivated in the Yemeni district of Arabia. By the 16th century, "
                        "it had spread to Persia, Egypt, Syria, and Turkey. Coffee houses, known as 'qahveh khaneh,' "
                        "began to appear in cities across the Near East. These establishments became important "
                        "centers for social activity and communication.\n\n"
                        "Coffee arrived in Europe in the 17th century and quickly became popular across the "
                        "continent. Some people reacted with suspicion, calling it the 'bitter invention of Satan.' "
                        "However, Pope Clement VIII was asked to intervene and found the beverage so satisfying "
                        "that he gave it papal approval. Coffee houses rapidly became centers of social activity "
                        "in major cities of England, Austria, France, Germany, and Holland."
                    ),
                    "questions": [
                        {
                            "question_text": "According to the passage, who is credited with the discovery of coffee?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) A monastery abbot",
                                "B) A goat herder named Kaldi",
                                "C) Pope Clement VIII",
                                "D) Yemeni traders",
                            ],
                            "correct_answer": "B) A goat herder named Kaldi",
                            "order": 1,
                        },
                        {
                            "question_text": "What was the initial reaction to coffee in some parts of Europe?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) It was immediately embraced by all",
                                "B) It was banned by the Pope",
                                "C) Some viewed it with suspicion",
                                "D) It was considered a medicine",
                            ],
                            "correct_answer": "C) Some viewed it with suspicion",
                            "order": 2,
                        },
                        {
                            "question_text": "What role did 'qahveh khaneh' play in Near Eastern cities?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) They served as religious centers",
                                "B) They were centers for social activity and communication",
                                "C) They were used as trading posts",
                                "D) They functioned as government buildings",
                            ],
                            "correct_answer": "B) They were centers for social activity and communication",
                            "order": 3,
                        },
                        {
                            "question_text": "By which century was coffee being cultivated in Arabia?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) 13th century",
                                "B) 14th century",
                                "C) 15th century",
                                "D) 17th century",
                            ],
                            "correct_answer": "C) 15th century",
                            "order": 4,
                        },
                    ],
                },
                {
                    "title": "Photosynthesis and Plant Biology",
                    "order": 2,
                    "content": (
                        "Photosynthesis is the biological process by which green plants and certain other "
                        "organisms convert light energy into chemical energy. During photosynthesis, plants "
                        "capture sunlight using chlorophyll, a green pigment found in chloroplasts. This "
                        "light energy is then used to convert carbon dioxide from the atmosphere and water "
                        "from the soil into glucose, a type of sugar that serves as food for the plant.\n\n"
                        "The process of photosynthesis can be divided into two main stages: the light-dependent "
                        "reactions and the light-independent reactions (also known as the Calvin cycle). "
                        "The light-dependent reactions take place in the thylakoid membranes of the chloroplasts "
                        "and require direct light to produce ATP and NADPH. The Calvin cycle occurs in the "
                        "stroma of the chloroplasts and uses the ATP and NADPH produced in the light-dependent "
                        "reactions to fix carbon dioxide into glucose.\n\n"
                        "Photosynthesis is essential for life on Earth. It produces the oxygen that most "
                        "living organisms need to survive and forms the base of nearly all food chains. "
                        "Without photosynthesis, the atmosphere would lack sufficient oxygen, and most "
                        "life forms would cease to exist."
                    ),
                    "questions": [
                        {
                            "question_text": "What is the primary pigment involved in photosynthesis?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Carotene",
                                "B) Xanthophyll",
                                "C) Chlorophyll",
                                "D) Anthocyanin",
                            ],
                            "correct_answer": "C) Chlorophyll",
                            "order": 1,
                        },
                        {
                            "question_text": "Where do the light-dependent reactions of photosynthesis occur?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) In the stroma",
                                "B) In the thylakoid membranes",
                                "C) In the cell wall",
                                "D) In the nucleus",
                            ],
                            "correct_answer": "B) In the thylakoid membranes",
                            "order": 2,
                        },
                        {
                            "question_text": "What are the two main products used by the Calvin cycle?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Oxygen and water",
                                "B) ATP and NADPH",
                                "C) Glucose and carbon dioxide",
                                "D) Chlorophyll and sunlight",
                            ],
                            "correct_answer": "B) ATP and NADPH",
                            "order": 3,
                        },
                    ],
                },
            ],
        },
        {
            "id": 2,
            "title": "TOEFL Reading Exam Simulation 1",
            "mode": "exam",
            "time_limit": 36,
            "is_active": True,
            "passages": [
                {
                    "title": "The Development of Writing Systems",
                    "order": 1,
                    "content": (
                        "The invention of writing is one of the most significant milestones in human history. "
                        "The earliest known writing system, cuneiform, was developed by the Sumerians in "
                        "Mesopotamia around 3400 BCE. Cuneiform began as a system of pictographs — simple "
                        "pictures representing objects — but gradually evolved into a more abstract system "
                        "of wedge-shaped marks pressed into clay tablets.\n\n"
                        "Around the same time, the ancient Egyptians developed their own writing system known "
                        "as hieroglyphics. Unlike cuneiform, hieroglyphics retained their pictorial quality "
                        "throughout much of their history. Egyptian scribes used hieroglyphics for religious "
                        "texts and monumental inscriptions, while a simplified script called hieratic was "
                        "used for everyday purposes.\n\n"
                        "The development of alphabetic writing represented a major breakthrough. The Phoenicians, "
                        "a seafaring people from the eastern Mediterranean, created the first widely used "
                        "alphabet around 1050 BCE. This alphabet consisted of 22 consonant letters and was "
                        "adapted by the Greeks, who added vowels to create the first true alphabet. The Greek "
                        "alphabet later influenced the development of the Latin alphabet, which is the most "
                        "widely used writing system in the world today."
                    ),
                    "questions": [
                        {
                            "question_text": "What was the earliest known writing system?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Hieroglyphics",
                                "B) The Phoenician alphabet",
                                "C) Cuneiform",
                                "D) The Greek alphabet",
                            ],
                            "correct_answer": "C) Cuneiform",
                            "order": 1,
                        },
                        {
                            "question_text": "How did cuneiform initially represent information?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Through abstract symbols",
                                "B) Through simple pictures (pictographs)",
                                "C) Through an alphabet",
                                "D) Through numerical codes",
                            ],
                            "correct_answer": "B) Through simple pictures (pictographs)",
                            "order": 2,
                        },
                        {
                            "question_text": "What innovation did the Greeks add to the Phoenician alphabet?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Consonant letters",
                                "B) Pictographic symbols",
                                "C) Vowels",
                                "D) Punctuation marks",
                            ],
                            "correct_answer": "C) Vowels",
                            "order": 3,
                        },
                        {
                            "question_text": "What was hieratic script used for in ancient Egypt?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Religious texts only",
                                "B) Monumental inscriptions",
                                "C) Everyday purposes",
                                "D) Communication with other civilizations",
                            ],
                            "correct_answer": "C) Everyday purposes",
                            "order": 4,
                        },
                        {
                            "question_text": "How many consonant letters were in the Phoenician alphabet?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) 20",
                                "B) 22",
                                "C) 24",
                                "D) 26",
                            ],
                            "correct_answer": "B) 22",
                            "order": 5,
                        },
                    ],
                },
                {
                    "title": "Ocean Currents and Climate",
                    "order": 2,
                    "content": (
                        "Ocean currents are continuous, directed movements of seawater generated by forces "
                        "acting upon the water, including wind, the Coriolis effect, temperature and salinity "
                        "differences, and the gravitational pull of the moon. Ocean currents play a crucial "
                        "role in regulating Earth's climate by transferring heat from the equator toward the "
                        "poles.\n\n"
                        "The Gulf Stream is one of the most well-known ocean currents. Originating in the "
                        "Gulf of Mexico, it flows northward along the eastern coast of the United States "
                        "before crossing the Atlantic Ocean toward Europe. The Gulf Stream carries warm water "
                        "and warm air to northwestern Europe, which is why countries like the United Kingdom "
                        "and Norway have relatively mild winters compared to other regions at similar latitudes.\n\n"
                        "El Niño is a climate pattern that describes the unusual warming of surface waters "
                        "in the eastern tropical Pacific Ocean. El Niño events occur irregularly, approximately "
                        "every two to seven years, and can have dramatic effects on weather patterns worldwide. "
                        "During an El Niño event, the normal trade winds weaken, allowing warm water to shift "
                        "eastward. This can lead to increased rainfall in South America, droughts in Australia "
                        "and Southeast Asia, and disruptions to marine ecosystems."
                    ),
                    "questions": [
                        {
                            "question_text": "What forces generate ocean currents?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Only wind and temperature",
                                "B) Wind, Coriolis effect, temperature/salinity differences, and gravity",
                                "C) Only the gravitational pull of the moon",
                                "D) Volcanic activity and earthquakes",
                            ],
                            "correct_answer": "B) Wind, Coriolis effect, temperature/salinity differences, and gravity",
                            "order": 1,
                        },
                        {
                            "question_text": "Why does northwestern Europe have relatively mild winters?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Because of volcanic activity",
                                "B) Due to its low latitude",
                                "C) Because the Gulf Stream carries warm water and air",
                                "D) Because of El Niño events",
                            ],
                            "correct_answer": "C) Because the Gulf Stream carries warm water and air",
                            "order": 2,
                        },
                        {
                            "question_text": "How often do El Niño events typically occur?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Every year",
                                "B) Every two to seven years",
                                "C) Every decade",
                                "D) Every twenty years",
                            ],
                            "correct_answer": "B) Every two to seven years",
                            "order": 3,
                        },
                        {
                            "question_text": "What happens to trade winds during an El Niño event?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) They strengthen significantly",
                                "B) They reverse direction",
                                "C) They weaken",
                                "D) They remain unchanged",
                            ],
                            "correct_answer": "C) They weaken",
                            "order": 4,
                        },
                        {
                            "question_text": "Where does the Gulf Stream originate?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) The Mediterranean Sea",
                                "B) The North Atlantic",
                                "C) The Gulf of Mexico",
                                "D) The Pacific Ocean",
                            ],
                            "correct_answer": "C) The Gulf of Mexico",
                            "order": 5,
                        },
                    ],
                },
            ],
        },
        {
            "id": 3,
            "title": "TOEFL Reading Practice Test 2",
            "mode": "practice",
            "time_limit": 0,
            "is_active": True,
            "passages": [
                {
                    "title": "The Human Immune System",
                    "order": 1,
                    "content": (
                        "The human immune system is a complex network of cells, tissues, and organs that "
                        "work together to defend the body against harmful invaders such as bacteria, viruses, "
                        "and parasites. The immune system can be broadly divided into two categories: the "
                        "innate immune system and the adaptive immune system.\n\n"
                        "The innate immune system is the body's first line of defense. It includes physical "
                        "barriers like the skin and mucous membranes, as well as various immune cells such "
                        "as neutrophils and macrophages that can quickly respond to threats. The innate "
                        "immune response is non-specific, meaning it does not target particular pathogens "
                        "but rather provides a general defense against all foreign substances.\n\n"
                        "The adaptive immune system, in contrast, develops a targeted response to specific "
                        "pathogens. When the body encounters a new pathogen, specialized cells called "
                        "lymphocytes (B cells and T cells) learn to recognize it. B cells produce antibodies "
                        "that bind to the pathogen, while T cells can directly destroy infected cells. "
                        "Importantly, the adaptive immune system has memory: after fighting off an infection, "
                        "it can mount a faster and stronger response if the same pathogen is encountered again. "
                        "This principle is the basis of vaccination."
                    ),
                    "questions": [
                        {
                            "question_text": "What are the two main categories of the human immune system?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Physical and chemical",
                                "B) Innate and adaptive",
                                "C) Internal and external",
                                "D) Active and passive",
                            ],
                            "correct_answer": "B) Innate and adaptive",
                            "order": 1,
                        },
                        {
                            "question_text": "What characterizes the innate immune response?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) It targets specific pathogens",
                                "B) It is non-specific and provides general defense",
                                "C) It produces antibodies",
                                "D) It has immunological memory",
                            ],
                            "correct_answer": "B) It is non-specific and provides general defense",
                            "order": 2,
                        },
                        {
                            "question_text": "What is the role of B cells in the adaptive immune system?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) They directly destroy infected cells",
                                "B) They produce antibodies",
                                "C) They form physical barriers",
                                "D) They act as the first line of defense",
                            ],
                            "correct_answer": "B) They produce antibodies",
                            "order": 3,
                        },
                        {
                            "question_text": "What principle of the adaptive immune system is the basis of vaccination?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Non-specific response",
                                "B) Physical barriers",
                                "C) Immunological memory",
                                "D) Neutrophil activation",
                            ],
                            "correct_answer": "C) Immunological memory",
                            "order": 4,
                        },
                    ],
                },
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Load mock data for team15 TOEFL Reading tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before loading",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing team15 data...")
            Answer.objects.all().delete()
            TestAttempt.objects.all().delete()
            Question.objects.all().delete()
            Passage.objects.all().delete()
            Test.objects.all().delete()
            self.stdout.write(self.style.WARNING("All team15 data cleared."))

        tests_created = 0
        passages_created = 0
        questions_created = 0

        for test_data in MOCK_DATA["tests"]:
            test, created = Test.objects.get_or_create(
                title=test_data["title"],
                defaults={
                    "mode": test_data["mode"],
                    "time_limit": test_data["time_limit"],
                    "is_active": test_data["is_active"],
                },
            )
            if created:
                tests_created += 1
            else:
                self.stdout.write(f"  Test '{test.title}' already exists, skipping.")
                continue

            for passage_data in test_data["passages"]:
                passage = Passage.objects.create(
                    test=test,
                    title=passage_data["title"],
                    content=passage_data["content"],
                    order=passage_data["order"],
                )
                passages_created += 1

                for q_data in passage_data["questions"]:
                    Question.objects.create(
                        passage=passage,
                        question_text=q_data["question_text"],
                        question_type=q_data["question_type"],
                        choices=q_data["choices"],
                        correct_answer=q_data["correct_answer"],
                        order=q_data["order"],
                    )
                    questions_created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done! Created {tests_created} tests, {passages_created} passages, {questions_created} questions."
        ))
