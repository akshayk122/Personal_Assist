# 🗄️ Supabase Integration Setup

This guide helps you set up Supabase as the database backend for expense storage in your Personal Assistant system.

## 📋 Prerequisites

- A Supabase account (sign up at [supabase.com](https://supabase.com))
- Your Personal Assistant system set up and running

## 🚀 Quick Setup

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `personal-assistant` (or your preferred name)
   - **Database Password**: Create a strong password
   - **Region**: Choose the closest region to you
5. Click "Create new project"

### 2. Get Your Project Credentials

After your project is created:

1. Go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (under "Project URL")
   - **anon public** key (under "Project API keys")

### 3. Set Up Environment Variables

Update your `.env` file with Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_API_KEY=your-anon-key-here
```

### 4. Create the Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `database_setup.sql` from this project
3. Paste and run the SQL script
4. Verify the `expenses` table was created in **Table Editor**

## 📊 Database Schema

The expenses table includes:

```sql
CREATE TABLE expenses (
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
```

## 🔧 How It Works

### Automatic Fallback System

The system is designed with automatic fallback:

1. **Primary**: Try to use Supabase database
2. **Fallback**: Use local JSON files if Supabase is unavailable
3. **Indicators**: The UI shows which storage method is being used

### Response Indicators

When using the expense tools, you'll see indicators like:

- `💾 Supabase` - Data stored/retrieved from Supabase
- `📁 Local Storage` - Using JSON files as fallback
- `📁 Local Storage (Supabase not available)` - Supabase credentials missing
- `📁 Local Storage (DB Error: ...)` - Supabase error occurred

## 🧪 Testing the Integration

### 1. Test Adding Expenses

```bash
# Start your servers
make meeting expense orchestrator streamlit

# In the Streamlit UI, try adding an expense:
"I spent $15.99 on coffee this morning"
```

### 2. Verify in Supabase

1. Go to **Table Editor** in your Supabase dashboard
2. View the `expenses` table
3. You should see your new expense entry

### 3. Test Queries

Try these example queries:

- "Show me all my expenses this month"
- "How much did I spend on food?"
- "Give me an expense summary"

## 🔒 Security Configuration

### Row Level Security (RLS)

The setup includes Row Level Security for data protection:

```sql
-- For authenticated users only
CREATE POLICY "Allow all operations for authenticated users" ON expenses
    FOR ALL USING (auth.role() = 'authenticated');

-- For development (anonymous access)
-- CREATE POLICY "Allow all operations for anonymous users" ON expenses FOR ALL USING (true);
```

### Development vs Production

**For Development:**
- You can use the anonymous key and allow anonymous access
- Uncomment the anonymous policy in the SQL setup

**For Production:**
- Use proper authentication
- Implement user-specific policies
- Consider using the service role key for server-side operations

## 🛠️ Troubleshooting

### Common Issues

**1. "Supabase client not initialized"**
- Check your `SUPABASE_URL` and `SUPABASE_API_KEY` in `.env`
- Ensure the values don't have quotes or extra spaces

**2. "Table 'expenses' doesn't exist"**
- Run the `database_setup.sql` script in Supabase SQL Editor
- Check Table Editor to verify the table was created

**3. "Permission denied"**
- Check your RLS policies
- For development, you might need to enable anonymous access

**4. Expenses still going to JSON files**
- Check the response messages for indicators
- Verify Supabase connection in server logs

### Debug Mode

To check if Supabase is connected:

```python
# In Python console
from personal_assistant.utils.supabase_config import supabase_manager
print(f"Supabase connected: {supabase_manager.is_connected()}")
```

## 📈 Benefits of Supabase Integration

### ✅ Advantages

- **Real-time sync**: Multiple users can share expense data
- **Backup & Recovery**: Cloud-based storage with automatic backups
- **Scalability**: Handle thousands of expenses efficiently
- **Advanced Queries**: Complex filtering and analytics
- **Data Security**: Row-level security and authentication
- **API Access**: Direct database access via REST/GraphQL APIs

### 🔄 Migration

Your existing JSON data remains as a fallback. To migrate existing expenses to Supabase:

1. The system will continue using JSON files for historical data
2. New expenses will be stored in Supabase
3. Both sources are queried for comprehensive results

## 🚀 Next Steps

1. **User Authentication**: Implement user-specific expense tracking
2. **Real-time Updates**: Add real-time expense notifications
3. **Advanced Analytics**: Use Supabase functions for complex calculations
4. **Mobile App**: Connect mobile apps to the same database
5. **Sharing**: Allow expense sharing between family members

## 📞 Support

- [Supabase Documentation](https://supabase.com/docs)
- [Personal Assistant Issues](https://github.com/your-repo/issues)
- Check server logs for detailed error messages 