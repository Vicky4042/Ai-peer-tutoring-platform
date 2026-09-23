-- Review-2 database schema
-- AI-Based Peer Tutoring Matching Platform
--
-- Scope: minimum structure needed for learner/tutor profiles,
-- subjects/skills, learning preference, availability, and matching.
-- Intentionally NOT over-engineered — session management, feedback,
-- auth, etc. are Part 2 / future work.

CREATE DATABASE IF NOT EXISTS peer_tutoring_db;
USE peer_tutoring_db;

-- ---------------------------------------------------------------
-- Reference table: reusable list of subjects/skills
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- ---------------------------------------------------------------
-- Learners
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    learning_preference VARCHAR(50) NOT NULL,   -- e.g. Visual, Reading/Writing, Auditory, Kinesthetic
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learner <-> Subject (many-to-many): subjects/topics the learner needs help with
CREATE TABLE IF NOT EXISTS learner_subjects (
    learner_id INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (learner_id, subject_id),
    FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Learner availability slots (e.g. Morning, Evening, Weekend)
CREATE TABLE IF NOT EXISTS learner_availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    learner_id INT NOT NULL,
    slot VARCHAR(50) NOT NULL,
    FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------------
-- Tutors
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tutors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    expertise_level INT NOT NULL DEFAULT 1,      -- 1 (beginner-friendly) - 5 (highly experienced)
    teaching_preference VARCHAR(50) NOT NULL,    -- e.g. Visual, Reading/Writing, Auditory, Kinesthetic
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (expertise_level BETWEEN 1 AND 5)
);

-- Tutor <-> Subject (many-to-many): subjects/skills the tutor teaches
CREATE TABLE IF NOT EXISTS tutor_subjects (
    tutor_id INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (tutor_id, subject_id),
    FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Tutor availability slots
CREATE TABLE IF NOT EXISTS tutor_availability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tutor_id INT NOT NULL,
    slot VARCHAR(50) NOT NULL,
    FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE CASCADE
);

-- Helpful indexes for lookups used by the matching query
CREATE INDEX idx_learner_subjects_learner ON learner_subjects(learner_id);
CREATE INDEX idx_tutor_subjects_tutor ON tutor_subjects(tutor_id);
