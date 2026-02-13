from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from team15.models import Test, Passage, Question, TestAttempt, Answer

TEST_USER_EMAIL = "team15@test.local"
TEST_USER_PASSWORD = "Team15@12345"


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
        {
            "id": 4,
            "title": "TOEFL Reading Exam Simulation 2",
            "mode": "exam",
            "time_limit": 36,
            "is_active": True,
            "passages": [
                {
                    "title": "Urban Heat Islands",
                    "order": 1,
                    "content": (
                        "An urban heat island is a metropolitan area that is significantly warmer than nearby "
                        "rural regions. The effect occurs because city surfaces such as asphalt, concrete, and "
                        "dark roofs absorb and store large amounts of solar energy during the day. At night, "
                        "these surfaces slowly release the stored heat, keeping urban air temperatures higher "
                        "than surrounding countryside.\n\n"
                        "Another important cause is the reduction of vegetation. Trees and plants cool the air "
                        "through shade and evapotranspiration, but densely built cities often replace natural "
                        "land cover with roads and buildings. In addition, waste heat from vehicles, factories, "
                        "and air-conditioning systems further raises local temperatures, especially in districts "
                        "with heavy traffic and high energy use.\n\n"
                        "Urban heat islands can increase electricity demand, worsen air pollution, and elevate "
                        "health risks during heat waves. City planners use several strategies to reduce this "
                        "effect, including planting street trees, creating green roofs, and installing high-albedo "
                        "(reflective) materials that bounce sunlight back into the atmosphere instead of absorbing it."
                    ),
                    "questions": [
                        {
                            "question_text": "What is the main idea of the passage?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Cities are always colder than rural areas",
                                "B) Urban heat islands result from human-made surfaces and can be mitigated",
                                "C) Heat waves are caused only by air conditioners",
                                "D) Rural regions produce more waste heat than cities",
                            ],
                            "correct_answer": "B) Urban heat islands result from human-made surfaces and can be mitigated",
                            "order": 1,
                        },
                        {
                            "question_text": "Why do city temperatures often remain high at night?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Urban surfaces release heat they stored during the day",
                                "B) Wind speed always increases after sunset",
                                "C) Rural vegetation emits more heat than concrete",
                                "D) Traffic stops completely at night",
                            ],
                            "correct_answer": "A) Urban surfaces release heat they stored during the day",
                            "order": 2,
                        },
                        {
                            "question_text": "According to the passage, what cooling role does vegetation play?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) It reflects all sunlight",
                                "B) It cools through shade and evapotranspiration",
                                "C) It reduces electricity demand by producing power",
                                "D) It removes all air pollution",
                            ],
                            "correct_answer": "B) It cools through shade and evapotranspiration",
                            "order": 3,
                        },
                        {
                            "question_text": "Which of the following is listed as a mitigation strategy?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Expanding asphalt parking lots",
                                "B) Increasing factory heat output",
                                "C) Installing reflective roof materials",
                                "D) Reducing all public transportation",
                            ],
                            "correct_answer": "C) Installing reflective roof materials",
                            "order": 4,
                        },
                        {
                            "question_text": "What is one consequence of urban heat islands mentioned in the passage?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Lower electricity demand",
                                "B) Reduced health risks during heat waves",
                                "C) Improved air quality in all districts",
                                "D) Higher health risks during extreme heat",
                            ],
                            "correct_answer": "D) Higher health risks during extreme heat",
                            "order": 5,
                        },
                    ],
                },
                {
                    "title": "The Silk Road and Cultural Exchange",
                    "order": 2,
                    "content": (
                        "The Silk Road was not a single road but a vast network of trade routes connecting East "
                        "Asia, Central Asia, the Middle East, and Europe. Although silk was one of the most famous "
                        "goods traded, merchants also exchanged spices, glassware, metals, textiles, and paper. "
                        "Trade along these routes expanded significantly during the Han Dynasty and later under "
                        "various empires that protected caravan travel.\n\n"
                        "The network encouraged more than commercial activity. Religious beliefs such as Buddhism, "
                        "Islam, and Christianity moved across regions through monks, scholars, and travelers. "
                        "Artistic styles, architectural techniques, and scientific knowledge were also shared. "
                        "For example, papermaking and printing methods traveled westward over time, while new crops "
                        "and medical ideas moved in multiple directions.\n\n"
                        "Despite its importance, Silk Road trade involved substantial risk. Merchants crossed deserts, "
                        "high mountains, and politically unstable territories. To reduce danger, traders often relied "
                        "on caravanserais, fortified inns that provided shelter, supplies, and opportunities to exchange "
                        "information. These stations helped maintain long-distance connections for centuries."
                    ),
                    "questions": [
                        {
                            "question_text": "According to the passage, the Silk Road is best described as:",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) A single highway used only for silk transport",
                                "B) A maritime route between Africa and Europe",
                                "C) A network of overland trade routes",
                                "D) A military road built by one empire",
                            ],
                            "correct_answer": "C) A network of overland trade routes",
                            "order": 1,
                        },
                        {
                            "question_text": "Which statement is supported by the passage?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Only silk was exchanged on the Silk Road",
                                "B) Religious and cultural ideas spread along trade routes",
                                "C) Trade became safer because deserts disappeared",
                                "D) Caravanserais were used only for religious ceremonies",
                            ],
                            "correct_answer": "B) Religious and cultural ideas spread along trade routes",
                            "order": 2,
                        },
                        {
                            "question_text": "What was one function of caravanserais?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) They produced silk for export",
                                "B) They served as fortified rest stations for traders",
                                "C) They replaced all local marketplaces",
                                "D) They blocked communication between regions",
                            ],
                            "correct_answer": "B) They served as fortified rest stations for traders",
                            "order": 3,
                        },
                        {
                            "question_text": "Why does the author mention mountains and deserts?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) To explain why sea trade was always preferred",
                                "B) To illustrate the hazards of long-distance trade",
                                "C) To describe where silk was manufactured",
                                "D) To compare climate zones in Europe",
                            ],
                            "correct_answer": "B) To illustrate the hazards of long-distance trade",
                            "order": 4,
                        },
                        {
                            "question_text": "What can be inferred about Silk Road exchange?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) It involved only goods, not knowledge",
                                "B) It was limited to one historical period",
                                "C) It facilitated multidirectional transfers of technology and ideas",
                                "D) It ended immediately after the Han Dynasty",
                            ],
                            "correct_answer": "C) It facilitated multidirectional transfers of technology and ideas",
                            "order": 5,
                        },
                    ],
                },
            ],
        },
        {
            "id": 5,
            "title": "TOEFL Reading Practice Test 3",
            "mode": "practice",
            "time_limit": 0,
            "is_active": True,
            "passages": [
                {
                    "title": "Plate Tectonics and Continental Drift",
                    "order": 1,
                    "content": (
                        "The theory of plate tectonics explains that Earth's outer shell is divided into large, "
                        "moving plates. These tectonic plates float on a softer layer of the mantle and shift "
                        "slowly over geological time. Their motion helps explain earthquakes, volcanic activity, "
                        "and the formation of mountain ranges.\n\n"
                        "Earlier in the twentieth century, Alfred Wegener proposed continental drift, the idea that "
                        "today's continents were once joined in a supercontinent called Pangaea. At first, many "
                        "scientists rejected his proposal because he could not explain the force that moved continents. "
                        "Later discoveries of seafloor spreading and magnetic patterns in oceanic crust provided strong "
                        "evidence that plates move and carry continents with them.\n\n"
                        "At divergent boundaries, plates move apart and new crust forms. At convergent boundaries, "
                        "plates collide; one plate may sink beneath another in a process called subduction. At "
                        "transform boundaries, plates slide past each other, often generating earthquakes. Together, "
                        "these boundary interactions shape Earth's surface continuously."
                    ),
                    "questions": [
                        {
                            "question_text": "What does the passage identify as Earth's outer shell being divided into?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Atmospheric layers",
                                "B) Tectonic plates",
                                "C) Magnetic zones",
                                "D) Ocean basins",
                            ],
                            "correct_answer": "B) Tectonic plates",
                            "order": 1,
                        },
                        {
                            "question_text": "Why was Wegener's idea initially criticized?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) He denied that continents had changed position",
                                "B) He claimed earthquakes never occur",
                                "C) He lacked a convincing mechanism for continental movement",
                                "D) He ignored evidence from ocean floors",
                            ],
                            "correct_answer": "C) He lacked a convincing mechanism for continental movement",
                            "order": 2,
                        },
                        {
                            "question_text": "Which boundary type is associated with plate collision?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Divergent boundary",
                                "B) Convergent boundary",
                                "C) Transform boundary",
                                "D) Passive boundary",
                            ],
                            "correct_answer": "B) Convergent boundary",
                            "order": 3,
                        },
                        {
                            "question_text": "What is subduction according to the passage?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) The creation of new crust at mid-ocean ridges",
                                "B) The sliding of plates past one another",
                                "C) The sinking of one plate beneath another",
                                "D) The complete stopping of plate movement",
                            ],
                            "correct_answer": "C) The sinking of one plate beneath another",
                            "order": 4,
                        },
                    ],
                },
            ],
        },
        {
            "id": 6,
            "title": "TOEFL Reading Exam Simulation 3",
            "mode": "exam",
            "time_limit": 36,
            "is_active": True,
            "passages": [
                {
                    "title": "Mangrove Forests and Coastal Protection",
                    "order": 1,
                    "content": (
                        "Mangroves are salt-tolerant trees that grow in tropical and subtropical coastal zones, "
                        "especially where rivers meet the sea. Their dense root systems trap sediments and stabilize "
                        "shorelines. Because mangroves slow wave energy, they can reduce coastal erosion and protect "
                        "inland communities from storm surges.\n\n"
                        "Mangrove ecosystems also provide important habitat for fish, crustaceans, birds, and other "
                        "wildlife. Many marine species use mangrove roots as nursery grounds, where young organisms "
                        "can shelter from predators. In addition, mangroves store substantial amounts of carbon in "
                        "soil and biomass, making them valuable for climate-change mitigation.\n\n"
                        "Despite these benefits, mangrove forests have declined in many regions due to aquaculture "
                        "expansion, urban development, and pollution. Restoration projects now combine replanting "
                        "with improved coastal management, but long-term success depends on protecting water quality "
                        "and natural tidal flow."
                    ),
                    "questions": [
                        {
                            "question_text": "According to the passage, where do mangroves commonly grow?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) High-altitude mountain valleys",
                                "B) Polar coastlines",
                                "C) Tropical and subtropical coastal zones",
                                "D) Deep ocean trenches",
                            ],
                            "correct_answer": "C) Tropical and subtropical coastal zones",
                            "order": 1,
                        },
                        {
                            "question_text": "How do mangroves help reduce coastal damage?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) By increasing offshore wind speed",
                                "B) By slowing wave energy and stabilizing shorelines",
                                "C) By replacing all man-made sea walls",
                                "D) By preventing all storms from forming",
                            ],
                            "correct_answer": "B) By slowing wave energy and stabilizing shorelines",
                            "order": 2,
                        },
                        {
                            "question_text": "What ecological role of mangrove roots is mentioned?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) They function as nursery habitat for juvenile marine species",
                                "B) They eliminate predator populations",
                                "C) They prevent fish migration",
                                "D) They reduce river flow to zero",
                            ],
                            "correct_answer": "A) They function as nursery habitat for juvenile marine species",
                            "order": 3,
                        },
                        {
                            "question_text": "Which human activity is identified as a cause of mangrove decline?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Forest fire suppression",
                                "B) Aquaculture expansion",
                                "C) Increased tidal flow",
                                "D) Glacier retreat",
                            ],
                            "correct_answer": "B) Aquaculture expansion",
                            "order": 4,
                        },
                        {
                            "question_text": "What does the final paragraph suggest about restoration?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Replanting alone guarantees success",
                                "B) Restoration is unnecessary where erosion is low",
                                "C) Long-term results require broader coastal management conditions",
                                "D) Pollution has no effect on mangrove recovery",
                            ],
                            "correct_answer": "C) Long-term results require broader coastal management conditions",
                            "order": 5,
                        },
                    ],
                },
                {
                    "title": "The Printing Press and the Spread of Knowledge",
                    "order": 2,
                    "content": (
                        "Before the fifteenth century, books in Europe were copied by hand, usually by trained scribes. "
                        "This process was slow and expensive, so books were relatively rare. In the mid-1400s, Johannes "
                        "Gutenberg introduced a system of movable metal type that allowed printers to assemble, reuse, "
                        "and rearrange individual letters efficiently.\n\n"
                        "The new printing method reduced production costs and increased the number of books available "
                        "to scholars, merchants, and eventually broader segments of society. As printed materials became "
                        "more common, literacy expanded in many urban centers. Standardized texts also improved the "
                        "consistency of scientific and legal communication.\n\n"
                        "Printing technology did not transform Europe overnight, but it accelerated long-term change. "
                        "Religious debates, political ideas, and scientific findings could circulate more quickly across "
                        "regions. Historians therefore view the printing press as one of the key technologies behind the "
                        "early modern expansion of knowledge networks."
                    ),
                    "questions": [
                        {
                            "question_text": "What problem did pre-printing book production face?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Books were too cheap to produce",
                                "B) Copying by hand was slow and costly",
                                "C) Metal type was difficult to transport",
                                "D) Literacy was universal and demand was low",
                            ],
                            "correct_answer": "B) Copying by hand was slow and costly",
                            "order": 1,
                        },
                        {
                            "question_text": "What was distinctive about Gutenberg's method?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) It used handwritten illustrations only",
                                "B) It required one-time wooden blocks for each page",
                                "C) It used reusable movable metal type",
                                "D) It depended on oral recitation rather than text",
                            ],
                            "correct_answer": "C) It used reusable movable metal type",
                            "order": 2,
                        },
                        {
                            "question_text": "According to the passage, what was one social effect of printing?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) Declining literacy in cities",
                                "B) Greater access to books for more people",
                                "C) Elimination of all manuscript culture immediately",
                                "D) Reduced circulation of scientific ideas",
                            ],
                            "correct_answer": "B) Greater access to books for more people",
                            "order": 3,
                        },
                        {
                            "question_text": "Why were standardized texts important?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) They improved consistency in scientific and legal communication",
                                "B) They replaced the need for education",
                                "C) They limited the spread of new ideas",
                                "D) They removed regional languages from Europe",
                            ],
                            "correct_answer": "A) They improved consistency in scientific and legal communication",
                            "order": 4,
                        },
                        {
                            "question_text": "What is the author's view of the printing press?",
                            "question_type": "multiple_choice",
                            "choices": [
                                "A) It had little historical significance",
                                "B) It created immediate uniformity across all regions",
                                "C) It was a key driver in expanding knowledge networks",
                                "D) It mainly affected agricultural production",
                            ],
                            "correct_answer": "C) It was a key driver in expanding knowledge networks",
                            "order": 5,
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

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            email=TEST_USER_EMAIL,
            defaults={
                "first_name": "Team15",
                "last_name": "Tester",
                "is_active": True,
            },
        )
        user.is_active = True
        user.set_password(TEST_USER_PASSWORD)
        user.save(update_fields=["is_active", "password"])

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(
            f"Test user {action}: {TEST_USER_EMAIL} / {TEST_USER_PASSWORD}"
        ))
