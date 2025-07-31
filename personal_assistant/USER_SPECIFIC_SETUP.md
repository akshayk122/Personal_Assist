# User-Specific Expense Setup Guide

## Overview
This guide explains how to set up and use the user-specific expense tracking functionality. Each user's expenses are now isolated and stored separately in the database.

## Setup Steps

### 1. Database Changes
Run the following SQL in your Supabase SQL Editor:
```sql
-- Add user_id support to expenses table
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS user_id TEXT NOT NULL DEFAULT 'default_user';

-- Create index for user_id on expenses
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);

-- Update RLS policy for expenses to include user_id filtering
DROP POLICY IF EXISTS "Enable all access for expenses" ON expenses;
CREATE POLICY "Enable user-specific access for expenses" ON expenses
    FOR ALL USING (user_id = current_setting('app.user_id', true)::text);

-- Update existing expenses to have a default user_id (if any exist)
UPDATE expenses SET user_id = 'default_user' WHERE user_id IS NULL;
```

### 2. Environment Configuration
Add your user ID to your `.env` file:
```bash
# Add this line to your .env file
USER_ID=your_unique_user_id
```

Example user IDs:
- `USER_ID=john_doe`
- `USER_ID=alice_smith`
- `USER_ID=user_123`

### 3. Testing the Setup
Run the test script to verify everything works:
```bash
cd personal_assistant
python test_user_specific_expenses.py
```

## How It Works

### User Isolation
- Each user's expenses are stored with their unique `user_id`
- Users can only see and modify their own expenses
- No cross-contamination between users

### Database Structure
```sql
-- Example expense record
{
  "id": 1,
  "expense_id": "uuid-123",
  "user_id": "john_doe",  -- User-specific identifier
  "amount": 25.50,
  "category": "food",
  "description": "Lunch",
  "date": "2024-12-15",
  -- ... other fields
}
```

### API Changes
All expense operations now include user_id filtering:
- `add_expense()`: Automatically adds user_id to new expenses
- `get_expenses()`: Only returns expenses for the current user
- `update_expense()`: Only updates user's own expenses
- `delete_expense()`: Only deletes user's own expenses

## Usage Examples

### Single User Setup
```bash
# Set user ID in environment
export USER_ID=john_doe

# Run the expense server
python servers/expense_server.py
```

### Multiple Users (Different Instances)
```bash
# Terminal 1 - User Alice
USER_ID=alice python servers/expense_server.py

# Terminal 2 - User Bob  
USER_ID=bob python servers/expense_server.py
```

### Testing Different Users
```python
# Test script example
import os

# Test Alice's expenses
os.environ['USER_ID'] = 'alice'
alice_expenses = get_expenses()  # Only Alice's expenses

# Test Bob's expenses
os.environ['USER_ID'] = 'bob'
bob_expenses = get_expenses()    # Only Bob's expenses
```

## Benefits

1. **Data Privacy**: Each user's data is completely isolated
2. **Scalability**: Easy to add more users
3. **Security**: RLS policies prevent unauthorized access
4. **Flexibility**: Can run multiple user instances
5. **Backward Compatible**: Existing data can be migrated

## Troubleshooting

### Common Issues

1. **"No expenses found" for existing user**
   - Check if `USER_ID` is set correctly in `.env`
   - Verify the user has expenses in the database

2. **"Database security policy violation"**
   - Run the SQL setup script in Supabase
   - Check RLS policies are properly configured

3. **Cross-user data contamination**
   - Ensure `user_id` is being passed correctly
   - Verify database queries include user filtering

### Debug Commands
```bash
# Check current user ID
echo $USER_ID

# Test database connection
python test_user_specific_expenses.py

# Check environment variables
python -c "import os; print('USER_ID:', os.getenv('USER_ID'))"
```

## Next Steps

1. **Test the setup** with the provided test script
2. **Add more users** by setting different `USER_ID` values
3. **Extend to other features** (notes, health, meetings)
4. **Add user management UI** (future enhancement)

## Migration from Existing Data

If you have existing expense data without user_id:
1. Run the SQL setup script (it sets default user_id)
2. Update your `.env` file with your desired user_id
3. Test that your existing data is accessible

The system will automatically handle new expenses with the correct user_id. 