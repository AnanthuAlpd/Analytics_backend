-- 1. Insert new master values into EXISTING lead_status table safely
INSERT INTO lead_status (status_name, description, is_active) VALUES
('Active', 'Lead is in progress', 1),
('Converted', 'Lead successfully converted', 1),
('Dropped', 'Lead is no longer pursued', 1),
('On Hold', 'Temporarily paused', 1),
('Not Interested', 'Lead showed no interest', 1),
('Invalid', 'Incorrect or fake lead', 1)
ON DUPLICATE KEY UPDATE description=VALUES(description), is_active=VALUES(is_active);

-- 2. Create Lead Stage Master (CORE ENGINE)
CREATE TABLE IF NOT EXISTS lead_stage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stage_name VARCHAR(100) NOT NULL,
    day_number INT NOT NULL,
    order_no INT NOT NULL,
    next_stage_id INT,
    delay_days INT DEFAULT 1,
    is_active TINYINT DEFAULT 1
);

-- clear default stages if any, so we don't insert duplicate when retrying
TRUNCATE TABLE lead_stage;

-- Insert Pipeline logic
INSERT INTO lead_stage (id, stage_name, day_number, order_no, next_stage_id, delay_days) VALUES
(1, 'Initial Contact', 0, 1, 2, 1),
(2, 'Send Info Material', 1, 2, 3, 1),
(3, 'Soft Follow-up', 2, 3, 4, 1),
(4, 'Deep Dive Call', 3, 4, 5, 1),
(5, 'Pre-conditioning', 4, 5, 6, 1),
(6, 'Google Meet Demo', 5, 6, 7, 1),
(7, 'Post-Meet Follow-up', 6, 7, 8, 1),
(8, 'Quiz & Engagement', 7, 8, 9, 1),
(9, 'Micro Task', 8, 9, 10, 2),
(10, 'Feedback & Doubt Clearing', 10, 10, 11, 1),
(11, 'Future Vision Push', 11, 11, 12, 1),
(12, 'Decision Push', 12, 12, 13, 1),
(13, 'Final Call', 13, 13, 14, 1),
(14, 'Onboarding', 14, 14, NULL, 0);

-- 3. Create Stage Actions (TASKS TO DO)
CREATE TABLE IF NOT EXISTS stage_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stage_id INT NOT NULL,
    action_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_mandatory TINYINT DEFAULT 1,
    FOREIGN KEY (stage_id) REFERENCES lead_stage(id) ON DELETE CASCADE
);

TRUNCATE TABLE stage_actions;

-- Insert Action data
INSERT INTO stage_actions (stage_id, action_name, description) VALUES
(1, 'Initial Call', 'Make a short intro call to create curiosity'),
(2, 'Send Info Material', 'Send PDF or video explaining concept'),
(3, 'Follow-up Message', 'Check if lead reviewed the material'),
(4, 'Detailed Discussion Call', 'Explain business model and earnings'),
(5, 'Invite for Demo', 'Invite to Google Meet session'),
(6, 'Conduct Demo', 'Show product, explain workflow, answer questions'),
(7, 'Post Demo Follow-up', 'Ask feedback and key takeaway'),
(8, 'Engagement Quiz', 'Check understanding via questions'),
(9, 'Assign Micro Task', 'Give small task to increase involvement'),
(10, 'Collect Feedback', 'Resolve doubts and confusion'),
(11, 'Explain Growth Plan', 'Show long-term benefits'),
(12, 'Ask for Decision', 'Push for commitment'),
(13, 'Final Objection Handling', 'Clear last doubts'),
(14, 'Onboarding Process', 'Add to system and assign first task');

-- 4. Create Activity Type Master (SCALABLE LOGS)
CREATE TABLE IF NOT EXISTS activity_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Insert Activity values (Use ignore to prevent duplicate key errors)
INSERT IGNORE INTO activity_type (name) VALUES
('Lead Created'),
('Stage Progressed'),
('Status Change'),
('Note Added'),
('Call Made'),
('Message Sent'),
('Demo Conducted'),
('Follow-up'),
('Task Completed');

-- 5. Link Existing Tables (MIGRATION)
-- We use a structured approach here to add the columns only if they don't exist

-- Connect newly created `lead_stage` to `leads`
set @exist := (select count(*) from information_schema.columns where table_name = 'leads' and column_name = 'stage_id' and table_schema = 'prabha');
set @sqlstmt := if( @exist <= 0, 'ALTER TABLE leads ADD COLUMN stage_id INT DEFAULT 1', 'select ''Column Exists''');
prepare stmt from @sqlstmt;
execute stmt;

set @exist_fk := (select count(*) from information_schema.table_constraints where constraint_name = 'fk_lead_stage' and table_schema = 'prabha');
set @sqlstmt_fk := if( @exist_fk <= 0, 'ALTER TABLE leads ADD CONSTRAINT fk_lead_stage FOREIGN KEY (stage_id) REFERENCES lead_stage(id)', 'select ''FK Exists''');
prepare stmt_fk from @sqlstmt_fk;
execute stmt_fk;


-- Evolve `lead_activity_logs`
set @exist_act := (select count(*) from information_schema.columns where table_name = 'lead_activity_logs' and column_name = 'activity_type_id' and table_schema = 'prabha');
set @sqlstmt_act := if( @exist_act <= 0, 'ALTER TABLE lead_activity_logs ADD COLUMN activity_type_id INT', 'select ''Column Exists''');
prepare stmt_act from @sqlstmt_act;
execute stmt_act;

set @exist_fk2 := (select count(*) from information_schema.table_constraints where constraint_name = 'fk_activity_type' and table_schema = 'prabha');
set @sqlstmt_fk2 := if( @exist_fk2 <= 0, 'ALTER TABLE lead_activity_logs ADD CONSTRAINT fk_activity_type FOREIGN KEY (activity_type_id) REFERENCES activity_type(id)', 'select ''FK Exists''');
prepare stmt_fk2 from @sqlstmt_fk2;
execute stmt_fk2;

