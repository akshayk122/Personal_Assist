-- Supabase Database Setup for Personal Assistant
-- Run this SQL in your Supabase SQL Editor

-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id BIGSERIAL PRIMARY KEY,
    expense_id TEXT UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    category TEXT NOT NULL,
    subcategory TEXT DEFAULT '',
    description TEXT NOT NULL,
    date DATE NOT NULL,
    payment_method TEXT DEFAULT 'credit',
    is_recurring BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id BIGSERIAL PRIMARY KEY,
    note_id TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    isCompleted BOOLEAN DEFAULT FALSE
);

-- Create health_goals table
CREATE TABLE IF NOT EXISTS health_goals (
    id BIGSERIAL PRIMARY KEY,
    goal_id TEXT UNIQUE NOT NULL,
    goal_type TEXT NOT NULL,
    target_value DECIMAL(10,2) NOT NULL,
    current_value DECIMAL(10,2) DEFAULT 0.0,
    description TEXT DEFAULT '',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create food_logs table
CREATE TABLE IF NOT EXISTS food_logs (
    id BIGSERIAL PRIMARY KEY,
    food_id TEXT UNIQUE NOT NULL,
    meal_type TEXT NOT NULL,
    food_item TEXT NOT NULL,
    calories INTEGER,
    date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_amount ON expenses(amount);
CREATE INDEX IF NOT EXISTS idx_expenses_expense_id ON expenses(expense_id);

-- Create indexes for health_goals
CREATE INDEX IF NOT EXISTS idx_health_goals_goal_type ON health_goals(goal_type);
CREATE INDEX IF NOT EXISTS idx_health_goals_is_active ON health_goals(is_active);
CREATE INDEX IF NOT EXISTS idx_health_goals_goal_id ON health_goals(goal_id);

-- Create indexes for food_logs
CREATE INDEX IF NOT EXISTS idx_food_logs_date ON food_logs(date);
CREATE INDEX IF NOT EXISTS idx_food_logs_meal_type ON food_logs(meal_type);
CREATE INDEX IF NOT EXISTS idx_food_logs_food_id ON food_logs(food_id);

-- Create meetings table
CREATE TABLE IF NOT EXISTS meetings (
    id BIGSERIAL PRIMARY KEY,
    meeting_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    attendees JSONB DEFAULT '[]'::jsonb,
    location TEXT DEFAULT '',
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for meetings
CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date);
CREATE INDEX IF NOT EXISTS idx_meetings_meeting_id ON meetings(meeting_id);
CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at for expenses
CREATE TRIGGER update_expenses_updated_at 
    BEFORE UPDATE ON expenses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to automatically update updated_at for meetings
CREATE TRIGGER update_meetings_updated_at 
    BEFORE UPDATE ON meetings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to automatically update updated_at for health_goals
CREATE TRIGGER update_health_goals_updated_at 
    BEFORE UPDATE ON health_goals 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;

-- Drop existing policies to avoid conflicts
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON expenses;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON notes;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON health_goals;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON food_logs;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON meetings;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON expenses;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON notes;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON health_goals;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON food_logs;
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON meetings;
DROP POLICY IF EXISTS "Allow all operations for all users" ON expenses;
DROP POLICY IF EXISTS "Allow all operations for all users" ON notes;
DROP POLICY IF EXISTS "Allow all operations for all users" ON health_goals;
DROP POLICY IF EXISTS "Allow all operations for all users" ON food_logs;
DROP POLICY IF EXISTS "Allow all operations for all users" ON meetings;

-- Create comprehensive policies for development (allows both anonymous and authenticated access)
-- For expenses table
CREATE POLICY "Allow all operations for all users" ON expenses 
    FOR ALL USING (true) WITH CHECK (true);

-- For notes table  
CREATE POLICY "Allow all operations for all users" ON notes 
    FOR ALL USING (true) WITH CHECK (true);

-- For health_goals table
CREATE POLICY "Allow all operations for all users" ON health_goals 
    FOR ALL USING (true) WITH CHECK (true);

-- For food_logs table
CREATE POLICY "Allow all operations for all users" ON food_logs 
    FOR ALL USING (true) WITH CHECK (true);

-- For meetings table
CREATE POLICY "Allow all operations for all users" ON meetings 
    FOR ALL USING (true) WITH CHECK (true);

-- Grant necessary permissions
GRANT ALL ON expenses TO authenticated;
GRANT ALL ON expenses TO anon;
GRANT ALL ON notes TO authenticated;
GRANT ALL ON notes TO anon;
GRANT ALL ON health_goals TO authenticated;
GRANT ALL ON health_goals TO anon;
GRANT ALL ON food_logs TO authenticated;
GRANT ALL ON food_logs TO anon;
GRANT ALL ON meetings TO authenticated;
GRANT ALL ON meetings TO anon;

-- Grant sequence permissions
GRANT USAGE, SELECT ON SEQUENCE expenses_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE expenses_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE notes_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE notes_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE health_goals_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE health_goals_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE food_logs_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE food_logs_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE meetings_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE meetings_id_seq TO anon;

-- Create some sample data (optional)
-- This matches the structure of your existing JSON data
INSERT INTO expenses (
    expense_id, amount, currency, category, subcategory, description, 
    date, payment_method, is_recurring, tags
) VALUES 
    ('sample-001', 12.50, 'USD', 'food', 'lunch', 'Subway sandwich and drink', 
     '2024-12-16', 'credit', false, '["quick-meal", "weekday-lunch"]'::jsonb),
    ('sample-002', 45.80, 'USD', 'transportation', 'gas', 'Shell gas station - full tank', 
     '2024-12-15', 'debit', false, '["car", "fuel", "commute"]'::jsonb),
    ('sample-003', 89.99, 'USD', 'entertainment', 'dining', 'Dinner at Giovanni''s Italian Restaurant', 
     '2024-12-14', 'credit', false, '["dinner", "italian", "date-night"]'::jsonb)
ON CONFLICT (expense_id) DO NOTHING;

-- Insert sample meetings
INSERT INTO meetings (
    meeting_id, title, date, time, duration_minutes, attendees,
    location, description, status
) VALUES 
    ('sample-m001', 'Team Standup', '2024-12-16', '09:00', 30, 
     '["john@company.com", "sarah@company.com"]'::jsonb,
     'Conference Room A', 'Daily team sync', 'scheduled'),
    ('sample-m002', 'Client Presentation', '2024-12-16', '14:00', 60, 
     '["client@external.com"]'::jsonb,
     'Virtual - Zoom', 'Q4 results presentation', 'scheduled')
ON CONFLICT (meeting_id) DO NOTHING;

-- Insert sample notes
INSERT INTO notes (
    note_id, content, iscompleted
) VALUES 
    ('sample-n001', 'Meeting with John about the project', false),
    ('sample-n002', 'Review the expense report for the month', false)
ON CONFLICT (note_id) DO NOTHING;

-- Insert sample health goals
INSERT INTO health_goals (
    goal_id, goal_type, target_value, current_value, description
) VALUES 
    ('sample-g001', 'weight', 170.0, 175.0, 'Target weight loss goal'),
    ('sample-g002', 'calories', 2000.0, 0.0, 'Daily calorie target')
ON CONFLICT (goal_id) DO NOTHING;

-- Insert sample food logs
INSERT INTO food_logs (
    food_id, meal_type, food_item, calories, date
) VALUES 
    ('sample-f001', 'breakfast', 'Oatmeal with berries', 320, '2024-12-16'),
    ('sample-f002', 'lunch', 'Grilled chicken salad', 450, '2024-12-16'),
    ('sample-f003', 'dinner', 'Salmon with vegetables', 680, '2024-12-16')
ON CONFLICT (food_id) DO NOTHING; 