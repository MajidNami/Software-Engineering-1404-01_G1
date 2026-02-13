CREATE DATABASE ToeflListeningDb;
GO

SELECT name AS table_name
FROM sys.tables
WHERE name IN (
    'users', 'skills', 'difficulties', 'topics', 'listening_items',
    'item_topics', 'item_metadata', 'assessment_blueprints', 'blueprint_sections',
    'blueprint_items', 'assessment_attempts', 'item_responses', 'skill_results',
    'feedback_entries', 'integrity_events', 'audit_logs', 'item_flags',
    'performance_history', 'analytic_events'
)
ORDER BY name;


USE ToeflListeningDb;
GO






CREATE TABLE listening_items (
    item_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    audio_url NVARCHAR(500) NOT NULL,
    audio_format NVARCHAR(20) NOT NULL,
    audio_duration INT NOT NULL,
    transcript NVARCHAR(MAX) NOT NULL,
    metadata NVARCHAR(MAX),
    language_code NVARCHAR(10) NOT NULL DEFAULT 'en-US',
    accent NVARCHAR(50),
    avg_response_time INT,
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2,
    created_by INT,
    updated_by INT,
    is_deleted BIT NOT NULL DEFAULT 0
);


CREATE TABLE skills (
    skill_id int IDENTITY(1,1) NOT NULL,
    name NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX),

    CONSTRAINT PK_skills PRIMARY KEY NONCLUSTERED (skill_id),
    CONSTRAINT UQ_skills_name UNIQUE (name)
);


CREATE TABLE difficulties (
    difficulty_id int IDENTITY(1,1) NOT NULL,
    name NVARCHAR(50) NOT NULL,
    description NVARCHAR(MAX),

    CONSTRAINT PK_difficulties PRIMARY KEY NONCLUSTERED (difficulty_id),
    CONSTRAINT UQ_difficulties_name UNIQUE (name)
);


CREATE TABLE topics (
    topic_id int IDENTITY(1,1) NOT NULL,
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX),
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2,

    CONSTRAINT PK_topics PRIMARY KEY NONCLUSTERED (topic_id),
    CONSTRAINT UQ_topics_name UNIQUE (name)
);

CREATE TABLE users (
    user_id int IDENTITY(1,1) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    level NVARCHAR(50),
    preferences NVARCHAR(MAX),
    last_login_at DATETIME2,
    phone_verified BIT NOT NULL DEFAULT 0,
    email_verified BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2,
    is_deleted BIT NOT NULL DEFAULT 0,

    CONSTRAINT PK_users PRIMARY KEY NONCLUSTERED (user_id),
    CONSTRAINT UQ_users_email UNIQUE (email)
);

CREATE INDEX IX_users_email ON users(email);


CREATE TABLE listening_questions (
    question_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    item_id INT NOT NULL,                 
    skill_id INT NOT NULL,               
    question_text NVARCHAR(MAX) NOT NULL, 
    options NVARCHAR(MAX) NOT NULL,       
    correct_answer CHAR(1) NOT NULL,   
    explanation NVARCHAR(MAX),          
    avg_response_time INT,
    order_index INT NOT NULL DEFAULT 1,  
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2,
    is_deleted BIT NOT NULL DEFAULT 0,

    CONSTRAINT FK_questions_item FOREIGN KEY (item_id) REFERENCES listening_items(item_id),
    CONSTRAINT FK_questions_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);


CREATE TABLE item_topics (
    item_id int  NOT NULL,
    topic_id int NOT NULL,

    CONSTRAINT PK_item_topics PRIMARY KEY (item_id, topic_id),
    CONSTRAINT FK_item_topics_item FOREIGN KEY (item_id) REFERENCES listening_items(item_id),
    CONSTRAINT FK_item_topics_topic FOREIGN KEY (topic_id) REFERENCES topics(topic_id)
);

CREATE INDEX IX_item_topics_topic ON item_topics(topic_id);



CREATE TABLE assessment_attempts (
    attempt_id int IDENTITY(1,1) NOT NULL,
    user_id int NOT NULL,
    blueprint_id int NOT NULL,
    attempt_mode NVARCHAR(20) NOT NULL,
    start_time DATETIME2 NOT NULL,
    end_time DATETIME2,
    status NVARCHAR(20) NOT NULL,
    settings NVARCHAR(MAX) NOT NULL,
    settings_version INT NOT NULL DEFAULT 1,
    raw_score INT,
    scaled_score INT,
    time_spent INT,
    time_remaining INT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2,
    is_deleted BIT NOT NULL DEFAULT 0,

    CONSTRAINT PK_assessment_attempts PRIMARY KEY NONCLUSTERED (attempt_id),
    CONSTRAINT FK_assessment_attempts_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IX_attempts_user ON assessment_attempts(user_id);
CREATE INDEX IX_attempts_status ON assessment_attempts(status);


CREATE TABLE item_responses (
    response_id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    attempt_id INT NOT NULL,              
    question_id INT NOT NULL,              
    selected_answer CHAR(1),              
    is_correct BIT,
    response_time_ms INT NOT NULL DEFAULT 0,
    answered_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL,

    CONSTRAINT UQ_attempt_question UNIQUE (attempt_id, question_id),
    CONSTRAINT FK_item_responses_attempt FOREIGN KEY (attempt_id) REFERENCES assessment_attempts(attempt_id),
    CONSTRAINT FK_item_responses_question FOREIGN KEY (question_id) REFERENCES listening_questions(question_id)
);


CREATE INDEX IX_item_responses_correct ON item_responses(is_correct);


CREATE TABLE skill_results (
    result_id int IDENTITY(1,1) NOT NULL,
    attempt_id int NOT NULL,
    skill_id int NOT NULL,
    correct_count INT,
    total_count INT,
    percentage FLOAT,
    feedback NVARCHAR(MAX),
    created_at DATETIME2 NOT NULL,

    CONSTRAINT PK_skill_results PRIMARY KEY NONCLUSTERED (result_id),
    CONSTRAINT UQ_attempt_skill UNIQUE (attempt_id, skill_id),
    CONSTRAINT FK_skill_results_attempt FOREIGN KEY (attempt_id) REFERENCES assessment_attempts(attempt_id),
    CONSTRAINT FK_skill_results_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);


CREATE TABLE feedback_entries (
    feedback_id int IDENTITY(1,1) NOT NULL,
    response_id int NOT NULL,
    feedback_type NVARCHAR(50),
    content NVARCHAR(MAX) NOT NULL,
    highlighted_segments NVARCHAR(MAX),
    created_at DATETIME2 NOT NULL,

    CONSTRAINT PK_feedback_entries PRIMARY KEY NONCLUSTERED (feedback_id),
    CONSTRAINT FK_feedback_entries_response FOREIGN KEY (response_id) REFERENCES item_responses(response_id)
);



CREATE TABLE integrity_events (
    event_id int IDENTITY(1,1) NOT NULL,
    attempt_id int NOT NULL,
    event_type NVARCHAR(50),
    severity NVARCHAR(20),
    details NVARCHAR(MAX),
    occurred_at DATETIME2 NOT NULL,

    CONSTRAINT PK_integrity_events PRIMARY KEY NONCLUSTERED (event_id),
    CONSTRAINT FK_integrity_events_attempt FOREIGN KEY (attempt_id) REFERENCES assessment_attempts(attempt_id)
);



CREATE TABLE item_metadata (
    item_id int IDENTITY(1,1) NOT NULL,
    language NVARCHAR(50),
    level NVARCHAR(50),
    source NVARCHAR(255),
    created_at DATETIME2,
    updated_at DATETIME2,

    CONSTRAINT PK_item_metadata PRIMARY KEY NONCLUSTERED (item_id),
    CONSTRAINT FK_item_metadata_item FOREIGN KEY (item_id) REFERENCES listening_items(item_id)
);

CREATE TABLE assessment_blueprints (
    blueprint_id int IDENTITY(1,1) NOT NULL,
    title NVARCHAR(255) NOT NULL,
    description NVARCHAR(MAX),
    creator_id int NOT NULL,
    created_by int NOT NULL,
    updated_by int,
    assessment_mode NVARCHAR(20) NOT NULL,
    difficulty_id int,
    total_duration INT,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL,
    updated_at DATETIME2,
    is_deleted BIT NOT NULL DEFAULT 0,

    CONSTRAINT PK_assessment_blueprints PRIMARY KEY NONCLUSTERED (blueprint_id),
    CONSTRAINT FK_blueprints_creator FOREIGN KEY (creator_id) REFERENCES users(user_id),
    CONSTRAINT FK_blueprints_created_by FOREIGN KEY (created_by) REFERENCES users(user_id),
    CONSTRAINT FK_blueprints_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id),
    CONSTRAINT FK_blueprints_difficulty FOREIGN KEY (difficulty_id) REFERENCES difficulties(difficulty_id)
);

CREATE TABLE blueprint_sections (
    section_id int IDENTITY(1,1) NOT NULL,
    blueprint_id int NOT NULL,
    title NVARCHAR(255),
    instructions NVARCHAR(MAX),
    section_type NVARCHAR(50) NOT NULL,
    order_index INT NOT NULL,
    duration INT,

    CONSTRAINT PK_blueprint_sections PRIMARY KEY NONCLUSTERED (section_id),
    CONSTRAINT FK_blueprint_sections_blueprint FOREIGN KEY (blueprint_id) REFERENCES assessment_blueprints(blueprint_id)
);

CREATE TABLE blueprint_items (
    blueprint_id int IDENTITY(1,1) NOT NULL,
    item_id int NOT NULL,
    section_id int,
    item_order INT NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    created_at DATETIME2 NOT NULL,

    CONSTRAINT PK_blueprint_items PRIMARY KEY (blueprint_id, item_id),
    CONSTRAINT FK_blueprint_items_blueprint FOREIGN KEY (blueprint_id) REFERENCES assessment_blueprints(blueprint_id),
    CONSTRAINT FK_blueprint_items_item FOREIGN KEY (item_id) REFERENCES listening_items(item_id),
    CONSTRAINT FK_blueprint_items_section FOREIGN KEY (section_id) REFERENCES blueprint_sections(section_id)
);

CREATE TABLE audit_logs (
    log_id int IDENTITY(1,1) NOT NULL,
    user_id int,
    action NVARCHAR(100) NOT NULL,
    entity_type NVARCHAR(50),
    entity_id int,
    details NVARCHAR(MAX),
    ip_address NVARCHAR(50),
    user_agent NVARCHAR(MAX),
    created_at DATETIME2 NOT NULL,

    CONSTRAINT PK_audit_logs PRIMARY KEY NONCLUSTERED (log_id),
    CONSTRAINT FK_audit_logs_user FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE item_flags (
    user_id int NOT NULL,
    item_id int NOT NULL,
    flag_type NVARCHAR(50),
    created_at DATETIME2 NOT NULL,

    CONSTRAINT PK_item_flags PRIMARY KEY (user_id, item_id),
    CONSTRAINT FK_item_flags_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT FK_item_flags_item FOREIGN KEY (item_id) REFERENCES listening_items(item_id)
);

CREATE TABLE performance_history (
    history_id int IDENTITY(1,1) NOT NULL,
    user_id int NOT NULL,
    topic_id int,
    skill_id int,
    total_attempts INT,
    correct_attempts INT,
    last_attempt DATETIME2,

    CONSTRAINT PK_performance_history PRIMARY KEY NONCLUSTERED (history_id),
    CONSTRAINT FK_performance_history_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT FK_performance_history_topic FOREIGN KEY (topic_id) REFERENCES topics(topic_id),
    CONSTRAINT FK_performance_history_skill FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);

CREATE TABLE analytic_events (
    event_id int IDENTITY(1,1) NOT NULL,
    user_id int,
    event_type NVARCHAR(100) NOT NULL,
    session_id int,
    attempt_id int,
    details NVARCHAR(MAX),
    browser_info NVARCHAR(MAX),
    device_type NVARCHAR(50),
    screen_resolution NVARCHAR(20),
    created_at DATETIME2 NOT NULL,

    CONSTRAINT PK_analytic_events PRIMARY KEY NONCLUSTERED (event_id),
    CONSTRAINT FK_analytic_events_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT FK_analytic_events_attempt FOREIGN KEY (attempt_id) REFERENCES assessment_attempts(attempt_id)
);



CREATE TABLE refresh_tokens (
    token NVARCHAR(255) PRIMARY KEY,
    user_id INT NOT NULL,
    expires_at DATETIME2 NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    revoked_at DATETIME2 NULL,
    replaced_by_token NVARCHAR(255) NULL,
    reason_revoked NVARCHAR(100) NULL,
    ip_address NVARCHAR(45) NULL,
    
    CONSTRAINT FK_refresh_tokens_users FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE
);


CREATE INDEX IX_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IX_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX IX_refresh_tokens_created_at ON refresh_tokens(created_at);

ALTER TABLE refresh_tokens 
ADD user_agent NVARCHAR(500) NULL,
    device_id NVARCHAR(255) NULL;

CREATE INDEX IX_refresh_tokens_device_id ON refresh_tokens(device_id);
