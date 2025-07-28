# 🔧 RLS Policy Troubleshooting Guide

## Issue: "Database security policy violation"

This error occurs when Supabase's Row Level Security (RLS) policies are blocking database operations.

## Quick Fix

### Step 1: Run the Fix Script
1. Go to your Supabase dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `fix_rls_policies.sql`
4. Click **Run** to execute the script

### Step 2: Verify the Fix
After running the script, you should see output showing the policies were created:
```
schemaname | tablename | policyname | permissive | roles | cmd | qual | with_check
-----------|-----------|------------|------------|-------|-----|------|------------
public     | expenses  | Allow all operations for all users | t | {} | ALL | true | true
public     | notes     | Allow all operations for all users | t | {} | ALL | true | true
public     | meetings  | Allow all operations for all users | t | {} | ALL | true | true
```

## Alternative Manual Fix

If the script doesn't work, manually run these commands in Supabase SQL Editor:

```sql
-- Drop existing policies
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON expenses;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON notes;
DROP POLICY IF EXISTS "Allow all operations for anonymous users" ON meetings;

-- Create new policies
CREATE POLICY "Allow all operations for all users" ON expenses 
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations for all users" ON notes 
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations for all users" ON meetings 
    FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions
GRANT ALL ON expenses TO anon;
GRANT ALL ON notes TO anon;
GRANT ALL ON meetings TO anon;
```

## What This Fix Does

1. **Removes conflicting policies**: Drops any existing RLS policies that might be causing conflicts
2. **Creates permissive policies**: Allows both anonymous and authenticated users to perform all operations
3. **Grants necessary permissions**: Ensures the `anon` role has full access to the tables

## Why This Happens

- Supabase enables RLS by default for security
- The default policies are often too restrictive for development
- Multiple policy definitions can conflict with each other
- Missing permissions for the `anon` role

## Testing the Fix

After applying the fix, test by:

1. **Adding a note**: Try adding a note through your application
2. **Adding an expense**: Try adding an expense through your application
3. **Checking logs**: Look for success messages instead of security policy errors

## For Production

⚠️ **Warning**: The policies created by this fix allow full access to all users. For production:

1. Implement proper user authentication
2. Create user-specific policies
3. Use the service role key for server-side operations
4. Consider using Supabase Auth for user management

## Still Having Issues?

If you're still experiencing problems:

1. **Check your environment variables**:
   ```bash
   echo $SUPABASE_URL
   echo $SUPABASE_API_KEY
   ```

2. **Verify table existence**:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public' AND table_name IN ('expenses', 'notes', 'meetings');
   ```

3. **Check RLS status**:
   ```sql
   SELECT schemaname, tablename, rowsecurity 
   FROM pg_tables 
   WHERE tablename IN ('expenses', 'notes', 'meetings');
   ```

4. **Test direct connection**:
   ```python
   from personal_assistant.utils.supabase_config import supabase_manager
   print(f"Connected: {supabase_manager.is_connected()}")
   ```

## Common Error Messages

| Error Message | Solution |
|---------------|----------|
| "security policy violation" | Run the fix script above |
| "permission denied" | Check if tables exist and permissions are granted |
| "table does not exist" | Run the full `database_setup.sql` script |
| "client not initialized" | Check your environment variables |

## Support

If you continue to have issues:
1. Check the server logs for detailed error messages
2. Verify your Supabase project settings
3. Ensure you're using the correct API key (anon key, not service role key) 