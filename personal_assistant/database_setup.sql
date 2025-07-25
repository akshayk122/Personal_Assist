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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_amount ON expenses(amount);
CREATE INDEX IF NOT EXISTS idx_expenses_expense_id ON expenses(expense_id);

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

-- Enable Row Level Security (RLS)
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings ENABLE ROW LEVEL SECURITY;

-- For development, enable anonymous access
-- In production, you should use proper authentication
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON expenses;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON meetings;

CREATE POLICY "Allow all operations for anonymous users" ON expenses FOR ALL USING (true);
CREATE POLICY "Allow all operations for anonymous users" ON meetings FOR ALL USING (true);

-- Later, for production, you can switch to authenticated users only:
-- DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON expenses;
-- DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON meetings;
-- CREATE POLICY "Allow all operations for authenticated users" ON expenses
--     FOR ALL USING (auth.role() = 'authenticated');
-- CREATE POLICY "Allow all operations for authenticated users" ON meetings
--     FOR ALL USING (auth.role() = 'authenticated');

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
-- Grant necessary permissions
-- These are typically handled automatically in Supabase, but included for completeness
GRANT ALL ON expenses TO authenticated;
GRANT ALL ON expenses TO anon;
GRANT ALL ON meetings TO authenticated;
GRANT ALL ON meetings TO anon;
GRANT USAGE, SELECT ON SEQUENCE expenses_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE expenses_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE meetings_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE meetings_id_seq TO anon; 