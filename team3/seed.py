# team3/seed_exams.py
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

from team3.models import Exam, Question, ExamSection, ExamSystem

def create_exam_with_questions(system, section, time_seconds, questions_data, exam_name=""):
    """Helper to create exam with questions if not exists"""
    exam, created = Exam.objects.get_or_create(
        section=section,
        system=system,
        defaults={'exam_time_seconds': time_seconds}
    )

    if created:
        questions = []
        for q_num, q_desc in questions_data:
            questions.append(Question(
                exam=exam,
                number=q_num,
                description=q_desc
            ))
        Question.objects.bulk_create(questions)

    return exam, created

def seed_ielts_exams():
    """Seed IELTS exams - ONLY Speaking and Writing"""
    print("🌐 Seeding IELTS Exams (Speaking & Writing Only)...")

    # IELTS Speaking Exam 1 - Daily Life
    speaking1_questions = [
        (1, "Part 1 (4-5 minutes):\n• Where is your hometown?\n• What do you like about living there?\n• How has your hometown changed in recent years?\n• Do you prefer living in a city or the countryside?"),
        (2, "Part 2 (3-4 minutes):\nDescribe a time you had to wait for something special.\nYou should say:\n• What you were waiting for\n• How long you had to wait\n• What you did while waiting\nAnd explain how you felt when it finally happened."),
        (3, "Part 3 (4-5 minutes):\n• Is patience important in modern life?\n• What are some situations where people need to be patient?\n• Do you think people are less patient now than in the past?\n• How can children learn to be more patient?")
    ]
    speaking1, created = create_exam_with_questions(
        ExamSystem.IELTS, ExamSection.SPEAKING, 840, speaking1_questions, "Daily Life"
    )
    if created:
        print("  ✅ IELTS Speaking 1: Daily Life (3 parts)")

    # IELTS Speaking Exam 2 - Technology
    speaking2_questions = [
        (1, "Part 1 (4-5 minutes):\n• How often do you use the internet?\n• What do you usually do online?\n• Do you prefer reading news online or in newspapers?\n• How has technology changed your life?"),
        (2, "Part 2 (3-4 minutes):\nDescribe a useful piece of technology you use regularly.\nYou should say:\n• What the technology is\n• How you use it\n• How long you have been using it\nAnd explain why you find it useful."),
        (3, "Part 3 (4-5 minutes):\n• What are the advantages of modern technology?\n• Are there any disadvantages of relying too much on technology?\n• How has technology changed education?\n• Do you think technology makes people more isolated?")
    ]
    speaking2, created = create_exam_with_questions(
        ExamSystem.IELTS, ExamSection.SPEAKING, 840, speaking2_questions, "Technology"
    )
    if created:
        print("  ✅ IELTS Speaking 2: Technology (3 parts)")

    # IELTS Speaking Exam 3 - Work & Studies
    speaking3_questions = [
        (1, "Part 1 (4-5 minutes):\n• Do you work or are you a student?\n• What do you like about your job/studies?\n• What would you like to change about your workplace/school?\n• Do you prefer working alone or in a team?"),
        (2, "Part 2 (3-4 minutes):\nDescribe a person who has been an important influence in your life.\nYou should say:\n• Who the person is\n• How long you have known them\n• What qualities this person has\nAnd explain why they have been important in your life."),
        (3, "Part 3 (4-5 minutes):\n• What qualities make someone a good leader?\n• Is it better to have young or old people in leadership positions?\n• How can people develop leadership skills?\n• What are the challenges of being a leader?")
    ]
    speaking3, created = create_exam_with_questions(
        ExamSystem.IELTS, ExamSection.SPEAKING, 840, speaking3_questions, "Work & Studies"
    )
    if created:
        print("  ✅ IELTS Speaking 3: Work & Studies (3 parts)")

    # IELTS Writing Exam 1 - Academic Task 1 + General Task 2
    writing1_questions = [
        (1, "Task 1 (Academic - 20 minutes):\nThe charts below show the percentage of water used for different purposes in six areas of the world.\n\nSummarize the information by selecting and reporting the main features, and make comparisons where relevant.\n\nWrite at least 150 words."),
        (2, "Task 2 (40 minutes):\nSome people believe that children should be allowed to stay at home and play until they are six or seven years old. Others believe that it is important for young children to go to school as early as possible.\n\nDiscuss both views and give your own opinion.\n\nWrite at least 250 words.")
    ]
    writing1, created = create_exam_with_questions(
        ExamSystem.IELTS, ExamSection.WRITING, 3600, writing1_questions, "Education & Resources"
    )
    if created:
        print("  ✅ IELTS Writing 1: Graph Analysis + Education Topic")

    # IELTS Writing Exam 2 - Academic Task 1 + General Task 2
    writing2_questions = [
        (1, "Task 1 (Academic - 20 minutes):\nThe diagram below shows the process by which bricks are manufactured for the building industry.\n\nSummarize the information by selecting and reporting the main features, and make comparisons where relevant.\n\nWrite at least 150 words."),
        (2, "Task 2 (40 minutes):\nSome people think that governments should give financial support to creative artists such as painters and musicians. Others believe that creative artists should be funded by alternative sources.\n\nDiscuss both views and give your own opinion.\n\nWrite at least 250 words.")
    ]
    writing2, created = create_exam_with_questions(
        ExamSystem.IELTS, ExamSection.WRITING, 3600, writing2_questions, "Process & Arts"
    )
    if created:
        print("  ✅ IELTS Writing 2: Process Diagram + Arts Funding")

    # IELTS Writing Exam 3 - Two Task 2 Essays
    writing3_questions = [
        (1, "Task 2 (40 minutes):\nIn some countries, the average weight of people is increasing and their levels of health and fitness are decreasing.\n\nWhat do you think are the causes of these problems and what measures could be taken to solve them?\n\nWrite at least 250 words."),
        (2, "Task 2 (40 minutes):\nSome people believe that we should not use animals for food, clothing, or any other purposes. Others believe that it is acceptable to use animals for human benefit.\n\nDiscuss both views and give your own opinion.\n\nWrite at least 250 words.")
    ]
    writing3, created = create_exam_with_questions(
        ExamSystem.IELTS, ExamSection.WRITING, 4800, writing3_questions, "Health & Ethics"
    )
    if created:
        print("  ✅ IELTS Writing 3: Health Issues + Animal Rights")

    return [speaking1, speaking2, speaking3], [writing1, writing2, writing3]

def seed_toefl_exams():
    """Seed TOEFL exams - ONLY Speaking and Writing"""
    print("\n🇺🇸 Seeding TOEFL Exams (Speaking & Writing Only)...")

    # TOEFL Speaking Exam 1 - Education
    speaking1_questions = [
        (1, "Independent Task (15s prep, 45s speak):\nSome students prefer to study alone, while others prefer to study in groups. Which method do you prefer and why? Use specific reasons and examples to support your answer."),
        (2, "Integrated Task (45s read, 60s listen, 30s prep, 60s speak):\nReading: University plans to require all first-year students to take a public speaking course.\nListening: Two students discuss the announcement.\nQuestion: The man expresses his opinion about the plan. State his opinion and explain the reasons he gives for holding that opinion."),
        (3, "Integrated Task (90s listen, 20s prep, 60s speak):\nListen to part of a lecture in a psychology class about memory consolidation.\nQuestion: Using points and examples from the lecture, explain how sleep affects memory consolidation."),
        (4, "Integrated Task (90s listen, 20s prep, 60s speak):\nListen to a conversation between two students about a problem with a group project.\nQuestion: The students discuss two possible solutions. Describe the problem and the two solutions. Then explain which solution you prefer and why.")
    ]
    speaking1, created = create_exam_with_questions(
        ExamSystem.TOEFL, ExamSection.SPEAKING, 1020, speaking1_questions, "Education Focus"
    )
    if created:
        print("  ✅ TOEFL Speaking 1: Education Topics (4 tasks)")

    # TOEFL Speaking Exam 2 - Technology & Society
    speaking2_questions = [
        (1, "Independent Task (15s prep, 45s speak):\nDo you agree or disagree with the following statement? 'Technology has made our lives easier but less meaningful.' Use specific reasons and examples to support your answer."),
        (2, "Integrated Task (45s read, 60s listen, 30s prep, 60s speak):\nReading: Proposal to limit social media use on campus Wi-Fi during class hours.\nListening: Two students discuss the proposal.\nQuestion: The woman expresses her opinion about the proposal. State her opinion and explain the reasons she gives for holding that opinion."),
        (3, "Integrated Task (90s listen, 20s prep, 60s speak):\nListen to part of a lecture in a sociology class about urbanization trends.\nQuestion: Using points and examples from the lecture, explain two effects of rapid urbanization mentioned by the professor."),
        (4, "Integrated Task (90s listen, 20s prep, 60s speak):\nListen to a conversation between a student and a professor about a research paper topic.\nQuestion: The professor suggests two possible approaches. Describe the student's situation and the two suggestions. Then explain which suggestion you think is better and why.")
    ]
    speaking2, created = create_exam_with_questions(
        ExamSystem.TOEFL, ExamSection.SPEAKING, 1020, speaking2_questions, "Technology & Society"
    )
    if created:
        print("  ✅ TOEFL Speaking 2: Technology & Society (4 tasks)")

    # TOEFL Writing Exam 1 - Academic Integration
    writing1_questions = [
        (1, "Integrated Task (20 minutes):\nReading: The article presents three benefits of remote learning for university students.\nListening: The professor challenges each of these benefits with counterarguments.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they cast doubt on the specific benefits presented in the reading passage."),
        (2, "Independent Task (30 minutes):\nDo you agree or disagree with the following statement?\n'It is better to have a few close friends than to have many casual acquaintances.'\n\nUse specific reasons and examples to support your answer.")
    ]
    writing1, created = create_exam_with_questions(
        ExamSystem.TOEFL, ExamSection.WRITING, 3000, writing1_questions, "Education & Relationships"
    )
    if created:
        print("  ✅ TOEFL Writing 1: Remote Learning + Friendship")

    # TOEFL Writing Exam 2 - Science & Ethics
    writing2_questions = [
        (1, "Integrated Task (20 minutes):\nReading: The article discusses three potential benefits of genetic engineering in agriculture.\nListening: The professor raises concerns about each of these benefits.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they challenge the specific benefits presented in the reading passage."),
        (2, "Independent Task (30 minutes):\nDo you agree or disagree with the following statement?\n'Governments should spend more money on space exploration than on solving problems on Earth.'\n\nUse specific reasons and examples to support your answer.")
    ]
    writing2, created = create_exam_with_questions(
        ExamSystem.TOEFL, ExamSection.WRITING, 3000, writing2_questions, "Science & Ethics"
    )
    if created:
        print("  ✅ TOEFL Writing 2: Genetic Engineering + Space Exploration")

    # TOEFL Writing Exam 3 - Business & Environment
    writing3_questions = [
        (1, "Integrated Task (20 minutes):\nReading: The article presents three arguments in favor of corporate social responsibility programs.\nListening: The professor questions the effectiveness of these programs.\n\nQuestion: Summarize the points made in the lecture, being sure to explain how they cast doubt on the arguments presented in the reading passage."),
        (2, "Independent Task (30 minutes):\nSome people believe that economic growth is the most important goal for a country. Others believe that protecting the environment should be given higher priority.\n\nDiscuss both views and give your own opinion.")
    ]
    writing3, created = create_exam_with_questions(
        ExamSystem.TOEFL, ExamSection.WRITING, 3000, writing3_questions, "Business & Environment"
    )
    if created:
        print("  ✅ TOEFL Writing 3: Corporate Responsibility + Economy vs Environment")

    return [speaking1, speaking2], [writing1, writing2, writing3]

def seed_general_english_exams():
    """Seed General English exams - ONLY Speaking and Writing"""
    print("\n🌍 Seeding General English Exams (Speaking & Writing Only)...")

    # General Speaking Exam 1 - Travel & Culture
    speaking1_questions = [
        (1, "Part 1 (4-5 minutes):\n• Have you ever traveled to another country?\n• What type of holiday do you prefer?\n• Do you like trying new foods when you travel?\n• What's the most interesting place you've visited?"),
        (2, "Part 2 (3-4 minutes):\nDescribe a traditional festival in your country.\nYou should say:\n• What the festival is\n• When it is celebrated\n• What people do during this festival\nAnd explain why this festival is important in your culture."),
        (3, "Part 3 (4-5 minutes):\n• Why are traditional festivals important?\n• How have festivals changed over time?\n• Do you think young people are losing interest in traditional festivals?\n• What can be done to preserve cultural traditions?")
    ]
    speaking1, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.SPEAKING, 840, speaking1_questions, "Travel & Culture"
    )
    if created:
        print("  ✅ General Speaking 1: Travel & Culture (3 parts)")

    # General Speaking Exam 2 - Work & Communication
    speaking2_questions = [
        (1, "Part 1 (4-5 minutes):\n• What do you do for a living?\n• What skills are important for your job?\n• Do you prefer email or phone calls for work communication?\n• How important is teamwork in your workplace?"),
        (2, "Part 2 (3-4 minutes):\nDescribe a time you had to communicate in a foreign language.\nYou should say:\n• Where you were\n• Who you were talking to\n• What you were talking about\nAnd explain how you felt about the experience."),
        (3, "Part 3 (4-5 minutes):\n• Why is learning foreign languages important?\n• What are the challenges of learning a new language?\n• How has technology helped language learning?\n• Do you think everyone should learn at least one foreign language?")
    ]
    speaking2, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.SPEAKING, 840, speaking2_questions, "Work & Communication"
    )
    if created:
        print("  ✅ General Speaking 2: Work & Communication (3 parts)")

    # General Speaking Exam 3 - Hobbies & Entertainment
    speaking3_questions = [
        (1, "Part 1 (4-5 minutes):\n• What do you do in your free time?\n• Do you prefer indoor or outdoor activities?\n• How often do you watch movies?\n• What kind of music do you like?"),
        (2, "Part 2 (3-4 minutes):\nDescribe a book you recently read and enjoyed.\nYou should say:\n• What the book is about\n• Why you decided to read it\n• What you liked about it\nAnd explain why you would recommend it to others."),
        (3, "Part 3 (4-5 minutes):\n• Do people read less now than in the past?\n• What are the benefits of reading?\n• How has digital technology affected reading habits?\n• Should children be encouraged to read more?")
    ]
    speaking3, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.SPEAKING, 840, speaking3_questions, "Hobbies & Entertainment"
    )
    if created:
        print("  ✅ General Speaking 3: Hobbies & Entertainment (3 parts)")

    # General Writing Exam 1 - Formal Letters
    writing1_questions = [
        (1, "Task 1 (Letter - 20 minutes):\nYou recently stayed at a hotel for a business trip. The service was excellent, but there was a problem with the billing.\n\nWrite a letter to the hotel manager. In your letter:\n• Thank them for the good service\n• Explain the billing problem\n• Provide details of what should be corrected\n• Suggest a solution"),
        (2, "Task 2 (Essay - 40 minutes):\nSome people think that the government should provide free housing for everyone. Others believe that individuals should be responsible for their own housing.\n\nDiscuss both views and give your own opinion.")
    ]
    writing1, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.WRITING, 3600, writing1_questions, "Business & Housing"
    )
    if created:
        print("  ✅ General Writing 1: Hotel Complaint + Housing Policy")

    # General Writing Exam 2 - Job Applications
    writing2_questions = [
        (1, "Task 1 (Letter - 20 minutes):\nYou saw an advertisement for a part-time job at a local bookstore. You are interested in applying.\n\nWrite a letter to the bookstore manager. In your letter:\n• Express your interest in the position\n• Describe your relevant experience\n• Explain why you would be suitable for the job\n• Suggest a time for an interview"),
        (2, "Task 2 (Essay - 40 minutes):\nSome people believe that job satisfaction is more important than a high salary. Others argue that a good salary leads to better quality of life.\n\nDiscuss both views and give your own opinion.")
    ]
    writing2, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.WRITING, 3600, writing2_questions, "Job Applications"
    )
    if created:
        print("  ✅ General Writing 2: Job Application + Salary vs Satisfaction")

    # General Writing Exam 3 - Community Issues
    writing3_questions = [
        (1, "Task 1 (Letter - 20 minutes):\nYou are concerned about a dangerous intersection near your home where several accidents have occurred.\n\nWrite a letter to the local council. In your letter:\n• Explain the location of the intersection\n• Describe the problem and recent accidents\n• Suggest solutions to improve safety\n• Request action from the council"),
        (2, "Task 2 (Essay - 40 minutes):\nIn many cities, traffic congestion is becoming a serious problem.\n\nWhat are the causes of this problem?\nWhat measures can be taken to solve it?\n\nGive reasons for your answer and include any relevant examples.")
    ]
    writing3, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.WRITING, 3600, writing3_questions, "Community & Traffic"
    )
    if created:
        print("  ✅ General Writing 3: Safety Complaint + Traffic Solutions")

    # General Writing Exam 4 - Environment
    writing4_questions = [
        (1, "Task 1 (Letter - 20 minutes):\nYou recently organized a community clean-up event that was very successful.\n\nWrite a letter to a local newspaper. In your letter:\n• Describe the event and its purpose\n• Explain how many people participated\n• Mention what was achieved\n• Encourage others to organize similar events"),
        (2, "Task 2 (Essay - 40 minutes):\nSome people believe that individuals can do little to improve the environment, and that only governments and large companies can make a real difference.\n\nTo what extent do you agree or disagree with this statement?")
    ]
    writing4, created = create_exam_with_questions(
        ExamSystem.GENERAL, ExamSection.WRITING, 3600, writing4_questions, "Environment"
    )
    if created:
        print("  ✅ General Writing 4: Community Event + Environmental Responsibility")

    return [speaking1, speaking2, speaking3], [writing1, writing2, writing3, writing4]

def run_seed():
    """Run all seed functions"""
    print("=" * 70)
    print("📚 SEEDING SPEAKING & WRITING EXAMS (NO READING/LISTENING)")
    print("=" * 70)

    # Seed all exam types
    ielts_speaking, ielts_writing = seed_ielts_exams()
    toefl_speaking, toefl_writing = seed_toefl_exams()
    general_speaking, general_writing = seed_general_english_exams()

    # Summary
    print("\n" + "=" * 70)
    print("📊 SEEDING COMPLETE - SPEAKING & WRITING ONLY")
    print("=" * 70)

    total_exams = Exam.objects.count()
    total_questions = Question.objects.count()

    print(f"\n🎯 Total Exams Created: {total_exams}")
    print(f"🎯 Total Questions Created: {total_questions}")

    # Detailed breakdown
    print("\n📋 EXAM BREAKDOWN:")

    for system_code, system_name in ExamSystem.choices:
        exams = Exam.objects.filter(system=system_code)
        if exams.exists():
            speaking_count = exams.filter(section=ExamSection.SPEAKING).count()
            writing_count = exams.filter(section=ExamSection.WRITING).count()
            print(f"\n  {system_name.upper()}:")
            print(f"    • Speaking Exams: {speaking_count}")
            print(f"    • Writing Exams: {writing_count}")

    print("\n💬 SPEAKING EXAM FORMATS:")
    print("  IELTS: 3 parts (Introduction, Long Turn, Discussion) - 11-14 minutes")
    print("  TOEFL: 4 tasks (Independent + 3 Integrated) - 17 minutes")
    print("  General: 3 parts (same as IELTS) - 11-14 minutes")

    print("\n✍️  WRITING EXAM FORMATS:")
    print("  IELTS: Task 1 (150 words, 20min) + Task 2 (250 words, 40min)")
    print("  TOEFL: Integrated (20min) + Independent (30min)")
    print("  General: Letter (150 words, 20min) + Essay (250 words, 40min)")

    print("\n✅ READY FOR USE:")
    print("  Run: python manage.py shell -c \"from team3.models import Exam, Question; print(f'Exams: {Exam.objects.count()}, Questions: {Question.objects.count()}')\"")
    print("  Or visit: http://localhost:8000/team3/")

if __name__ == "__main__":
    run_seed()