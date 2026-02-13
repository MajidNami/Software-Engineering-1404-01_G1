CREATE TABLE grammar_users
(
    id         BIGSERIAL PRIMARY KEY,
    username   VARCHAR(50) UNIQUE  NOT NULL,
    password   VARCHAR(256)        NOT NULL,
    email      VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE examples
(
    id            BIGSERIAL PRIMARY KEY,
    grammar_topic VARCHAR(50) NOT NULL,
    grammar_level VARCHAR(25) NOT NULL,
    sentence      TEXT        NOT NULL,
    explanation   TEXT, -- Optional explanation
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exercises
(
    id             BIGSERIAL PRIMARY KEY,
    grammar_topic  VARCHAR(50) NOT NULL,
    exercise_type  VARCHAR(25) NOT NULL,
    grammar_level  VARCHAR(25) NOT NULL,
    question       TEXT        NOT NULL,
    correct_answer TEXT        NOT NULL,
    -- store multiple choice options as JSON string like ["go", "goes"]
    options        TEXT,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evaluations
(
    id                     BIGSERIAL PRIMARY KEY,
    grammar_user_id        INT         NOT NULL REFERENCES grammar_users (id),
    grammar_topic          VARCHAR(50) NOT NULL, -- topic detected by AI
    detected_grammar_level VARCHAR(25) NOT NULL, -- grammar_level estimated by AI
    evaluation_type        VARCHAR(10) NOT NULL,
    original_sentence      TEXT        NOT NULL,
    corrected_sentence     TEXT,                 -- NULL if original was correct
    is_correct             BOOLEAN     NOT NULL,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- tracks which examples a user has seen to ensure freshness
CREATE TABLE user_example_history
(
    id              BIGSERIAL PRIMARY KEY,
    grammar_user_id INT NOT NULL NOT NULL REFERENCES grammar_users (id),
    example_id      INT NOT NULL REFERENCES examples (id),
    seen_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (grammar_user_id, example_id)
);

-- tracks seen exercises AND whether they were solved correctly
CREATE TABLE user_exercise_history
(
    id              BIGSERIAL PRIMARY KEY,
    grammar_user_id INT     NOT NULL REFERENCES grammar_users (id),
    exercise_id     INT     NOT NULL REFERENCES exercises (id),
    user_answer     TEXT    NOT NULL,
    is_correct      BOOLEAN NOT NULL, -- Did user solve it correctly?
    attempted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (grammar_user_id, exercise_id)
);

-- optimized table for the Profile Stats view.
-- updated via Application Logic
CREATE TABLE user_stats
(
    id                        BIGSERIAL PRIMARY KEY,
    grammar_user_id           INT         NOT NULL REFERENCES grammar_users (id),
    grammar_topic             VARCHAR(50) NOT NULL,
    grammar_level             VARCHAR(25) NOT NULL,
    total_sent_evaluations    INT DEFAULT 0,
    total_correct_evaluations INT DEFAULT 0, -- Sentences requiring no correction
    total_seen_examples       INT DEFAULT 0,
    total_attempted_exercises INT DEFAULT 0,
    total_correct_exercises   INT DEFAULT 0, -- Exercises answered correctly

    updated_at                TIMESTAMP,
    UNIQUE (grammar_user_id, grammar_topic, grammar_level)
);
