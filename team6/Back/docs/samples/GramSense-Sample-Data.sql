BEGIN;

-- 1. Add user
INSERT INTO grammar_users (username, password, email)
VALUES ('test_user', 'test_pass', 'test_user@gramsense.app');

-- 2. Add examples (EASY, MEDIUM, HARD)
INSERT INTO examples (grammar_topic, grammar_level, sentence, explanation) VALUES
('PRESENT_SIMPLE', 'EASY',
 'She works in an office.',
 'Third-person singular verbs take -s in the present simple.'),

('PRESENT_SIMPLE', 'MEDIUM',
 'They play football every weekend.',
 'Present simple is used for habitual actions.'),

('PRESENT_SIMPLE', 'HARD',
 'He rarely eats fast food.',
 'Adverbs of frequency are commonly used with the present simple.');

-- 3. Add exercises (9 total)

INSERT INTO exercises
(grammar_topic, exercise_type, grammar_level, question, correct_answer, options)
VALUES

-- EASY
('PRESENT_SIMPLE', 'FILL_BLANK', 'EASY',
 'She ___ to school every day',
 'She goes to school every day',
 '["go", "goes"]'),

('PRESENT_SIMPLE', 'MULTIPLE_CHOICE', 'EASY',
 'He ___ coffee every morning',
 'He drinks coffee every morning',
 '["drink", "drinks", "drinking"]'),

('PRESENT_SIMPLE', 'FULL_SENTENCE', 'EASY',
 'Write a correct sentence using she like apples',
 'She likes apples',
 '["she", "like", "apples"]'),

-- MEDIUM
('PRESENT_SIMPLE', 'FILL_BLANK', 'MEDIUM',
 'They ___ TV after dinner',
 'They watch TV after dinner',
 '["watch", "watches"]'),

('PRESENT_SIMPLE', 'MULTIPLE_CHOICE', 'MEDIUM',
 'We ___ to work by bus',
 'We go to work by bus',
 '["go", "goes", "going"]'),

('PRESENT_SIMPLE', 'FULL_SENTENCE', 'MEDIUM',
 'Write a sentence using he not play chess',
 'He does not play chess',
 '["he", "not", "play", "chess"]'),

-- HARD
('PRESENT_SIMPLE', 'FILL_BLANK', 'HARD',
 'She usually ___ up at 6 am',
 'She usually wakes up at 6 am',
 '["wake", "wakes"]'),

('PRESENT_SIMPLE', 'MULTIPLE_CHOICE', 'HARD',
 'How often ___ he travel abroad',
 'How often does he travel abroad',
 '["do", "does", "is"]'),

('PRESENT_SIMPLE', 'FULL_SENTENCE', 'HARD',
 'Write a sentence using they rarely eat meat',
 'They rarely eat meat',
 '["they", "rarely", "eat", "meat"]');

COMMIT;