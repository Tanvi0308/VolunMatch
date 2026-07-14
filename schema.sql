-- SQLite version of the schema

CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS volunteer_skills (
    volunteer_id INTEGER,
    skill_id INTEGER,
    PRIMARY KEY (volunteer_id, skill_id),
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_skills (
    project_id INTEGER,
    skill_id INTEGER,
    PRIMARY KEY (project_id, skill_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id INTEGER,
    project_id INTEGER,
    status TEXT DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id INTEGER,
    project_id INTEGER,
    score REAL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Insert predefined skills
INSERT OR IGNORE INTO skills (name) VALUES 
('Python'), ('Java'), ('HTML'), ('CSS'), ('JavaScript'), ('React'), ('Node.js'), ('Data Analysis'),
('Machine Learning'), ('Graphic Design'), ('Content Writing'), ('Social Media'), ('Marketing'),
('Project Management'), ('Public Speaking'), ('Event Planning'), ('Fundraising'), ('Accounting');

-- Insert dummy admin user
INSERT OR IGNORE INTO volunteers (name, email, password_hash, is_admin) VALUES
('Admin User', 'admin@example.com', 'scrypt:32768:8:1$hU6r9zGg4qB2M9jN$a9e4d5884e1b80db18c4c3756535df2a926a117b38466b048d42d1396a8be448', 1);

-- Insert sample volunteers
INSERT OR IGNORE INTO volunteers (name, email, password_hash, is_admin) VALUES
('Alice Smith', 'alice@example.com', 'dummy_hash', 0),
('Bob Jones', 'bob@example.com', 'dummy_hash', 0),
('Charlie Brown', 'charlie@example.com', 'dummy_hash', 0),
('Diana Prince', 'diana@example.com', 'dummy_hash', 0),
('Evan Wright', 'evan@example.com', 'dummy_hash', 0),
('Fiona Gallagher', 'fiona@example.com', 'dummy_hash', 0),
('George Miller', 'george@example.com', 'dummy_hash', 0),
('Hannah Abbott', 'hannah@example.com', 'dummy_hash', 0),
('Ian Malcolm', 'ian@example.com', 'dummy_hash', 0),
('Julia Child', 'julia@example.com', 'dummy_hash', 0);

-- Insert sample projects
INSERT OR IGNORE INTO projects (title, description) VALUES
('Community Garden Setup', 'We need help setting up a community garden. Requires planning, heavy lifting, and social media outreach to get volunteers.'),
('Tech Mentorship for Kids', 'Teach basic programming and web development (HTML, CSS, JavaScript) to middle school students.'),
('Local Food Bank Website', 'Redesign and develop a new website for our local food bank. Needs good UI/UX and responsive design.'),
('Data Analysis for Non-Profit', 'Analyze donor data and create reports to help us understand fundraising patterns. Python and Data Analysis skills required.'),
('Annual Charity Gala', 'Help organize our biggest event of the year. We need event planners, marketing experts, and accountants.');

-- Map skills to projects
INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (1, 16), (1, 12);
INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (2, 3), (2, 4), (2, 5), (2, 1);
INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (3, 10), (3, 6), (3, 7);
INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (4, 1), (4, 8), (4, 9);
INSERT OR IGNORE INTO project_skills (project_id, skill_id) VALUES (5, 16), (5, 13), (5, 18);

-- Map skills to volunteers
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (2, 1), (2, 8);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (3, 3), (3, 4), (3, 5), (3, 6);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (4, 16), (4, 15);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (5, 10), (5, 12);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (6, 7), (6, 9), (6, 1);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (7, 13), (7, 11);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (8, 18), (8, 14);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (9, 16), (9, 13), (9, 12);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (10, 8), (10, 1), (10, 2);
INSERT OR IGNORE INTO volunteer_skills (volunteer_id, skill_id) VALUES (11, 3), (11, 4), (11, 11);
