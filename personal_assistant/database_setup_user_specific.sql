-- Add user_id support to expenses table
-- Run this SQL in your Supabase SQL Editor

-- Add user_id column to expenses table
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS user_id TEXT NOT NULL DEFAULT 'default_user';

-- Create index for user_id on expenses
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);

-- Update RLS policy for expenses to include user_id filtering
DROP POLICY IF EXISTS "Enable all access for expenses" ON expenses;
CREATE POLICY "Enable user-specific access for expenses" ON expenses
    FOR ALL USING (user_id = current_setting('app.user_id', true)::text);

-- Update existing expenses to have a default user_id (if any exist)
UPDATE expenses SET user_id = 'default_user' WHERE user_id IS NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'expenses' AND column_name = 'user_id'; 