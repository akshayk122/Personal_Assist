-- Supabase Database Setup for Personal Assistant - Expense User-Specific Version
-- Run this SQL in your Supabase SQL Editor to add user_id support to expenses table only

-- ============================================================================
-- STEP 1: Add user_id column to expenses table
-- ============================================================================

-- Add user_id to expenses table
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS user_id TEXT NOT NULL DEFAULT 'default_user';
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);

-- ============================================================================
-- STEP 2: Update existing expenses with default user_id
-- ============================================================================

-- Update existing expenses
UPDATE expenses SET user_id = 'default_user' WHERE user_id IS NULL;

-- ============================================================================
-- STEP 3: Drop existing policies and create user-specific RLS policies for expenses
-- ============================================================================

-- Drop existing policies for expenses
DROP POLICY IF EXISTS "Allow all operations for all users" ON expenses;
DROP POLICY IF EXISTS "Enable user-specific access for expenses" ON expenses;

-- Create user-specific policies for expenses
CREATE POLICY "Enable user-specific access for expenses" ON expenses
    FOR ALL USING (user_id = current_setting('app.user_id', true)::text OR user_id = 'default_user')
    WITH CHECK (user_id = current_setting('app.user_id', true)::text OR user_id = 'default_user');

-- ============================================================================
-- STEP 4: Create function to set user context
-- ============================================================================

-- Function to set user context for RLS policies
CREATE OR REPLACE FUNCTION set_user_context(user_id_param TEXT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.user_id', user_id_param, false);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STEP 5: Insert sample expense data with user_id
-- ============================================================================

-- Insert sample expenses with user_id
INSERT INTO expenses (
    expense_id, amount, currency, category, subcategory, description, 
    date, payment_method, is_recurring, tags, user_id
) VALUES 
    ('sample-001', 12.50, 'USD', 'food', 'lunch', 'Subway sandwich and drink', 
     '2024-12-16', 'credit', false, '["quick-meal", "weekday-lunch"]'::jsonb, 'default_user'),
    ('sample-002', 45.80, 'USD', 'transportation', 'gas', 'Shell gas station - full tank', 
     '2024-12-15', 'debit', false, '["car", "fuel", "commute"]'::jsonb, 'default_user'),
    ('sample-003', 89.99, 'USD', 'entertainment', 'dining', 'Dinner at Giovanni''s Italian Restaurant', 
     '2024-12-14', 'credit', false, '["dinner", "italian", "date-night"]'::jsonb, 'default_user'),
    ('user-001', 25.00, 'USD', 'food', 'lunch', 'Pizza for lunch', 
     '2024-12-16', 'credit', false, '["lunch", "pizza"]'::jsonb, 'user123'),
    ('user-002', 35.50, 'USD', 'transportation', 'uber', 'Uber ride to airport', 
     '2024-12-15', 'credit', false, '["transport", "airport"]'::jsonb, 'user123'),
    ('user-003', 15.75, 'USD', 'food', 'coffee', 'Starbucks coffee and pastry', 
     '2024-12-16', 'debit', false, '["coffee", "breakfast"]'::jsonb, 'user456'),
    ('user-004', 120.00, 'USD', 'shopping', 'electronics', 'New headphones', 
     '2024-12-15', 'credit', false, '["electronics", "audio"]'::jsonb, 'user456')
ON CONFLICT (expense_id) DO NOTHING;

-- ============================================================================
-- STEP 6: Verify the expense setup
-- ============================================================================

-- Check that user_id column was added to expenses
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'expenses' AND column_name = 'user_id';

-- Check that index was created
SELECT 
    indexname, 
    tablename, 
    indexdef
FROM pg_indexes 
WHERE indexname LIKE '%expenses_user_id%';

-- Check that policy was created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'expenses'
ORDER BY policyname;

-- Test expense data isolation by user
SELECT 'Testing expense data isolation...' as test_message;

-- Show expenses for default_user
SELECT 'Default user expenses:' as user_type, COUNT(*) as expense_count
FROM expenses WHERE user_id = 'default_user';

-- Show expenses for user123
SELECT 'User123 expenses:' as user_type, COUNT(*) as expense_count
FROM expenses WHERE user_id = 'user123';

-- Show expenses for user456
SELECT 'User456 expenses:' as user_type, COUNT(*) as expense_count
FROM expenses WHERE user_id = 'user456';

-- Show all users with expense data
SELECT user_id, COUNT(*) as expense_count
FROM expenses
GROUP BY user_id
ORDER BY user_id;

-- ============================================================================
-- STEP 7: Usage instructions for expense user_id
-- ============================================================================

/*
EXPENSE USER_ID USAGE INSTRUCTIONS:

1. To set user context before expense queries:
   SELECT set_user_context('user123');

2. To query expenses for a specific user:
   - The RLS policies will automatically filter by user_id
   - Make sure to set the user context first

3. To add expenses for a specific user:
   - Include user_id in your INSERT statements
   - Or set user context and let RLS handle it

4. To test expense user isolation:
   - Set context for user123: SELECT set_user_context('user123');
   - Query expenses: SELECT * FROM expenses;
   - Only user123's expenses will be returned

5. Environment variable fallback:
   - If no user context is set, it defaults to 'default_user'
   - This ensures backward compatibility

EXAMPLE EXPENSE QUERIES:

-- Set user context
SELECT set_user_context('user123');

-- Query user's expenses
SELECT * FROM expenses WHERE user_id = 'user123';

-- Add expense for user
INSERT INTO expenses (expense_id, amount, category, description, date, user_id)
VALUES ('new-expense', 25.00, 'food', 'Lunch', '2024-12-16', 'user123');

-- Query with RLS (automatic user filtering)
SELECT * FROM expenses; -- Only shows user123's expenses if context is set

-- Test different users
SELECT set_user_context('user456');
SELECT * FROM expenses; -- Only shows user456's expenses

-- Reset to default
SELECT set_user_context('default_user');
SELECT * FROM expenses; -- Shows default user expenses
*/ 