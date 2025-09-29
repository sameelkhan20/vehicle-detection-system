# 🆓 Free Database Setup Guide

## Option 1: PlanetScale (Recommended) - 100% Free

### Step 1: Create Account
1. Go to [planetscale.com](https://planetscale.com)
2. Click "Start for free"
3. Sign up with GitHub account
4. **No credit card required!**

### Step 2: Create Database
1. Click "Create new database"
2. Choose "Create new database"
3. Name: `vehicle_detection`
4. Region: Choose closest to you
5. Click "Create database"

### Step 3: Get Connection Details
1. Go to your database dashboard
2. Click "Connect"
3. Choose "General purpose"
4. Copy connection details:
   ```
   Host: [your-host].planetscale.com
   Username: [your-username]
   Password: [your-password]
   Database: vehicle_detection
   Port: 3306
   ```

### Step 4: Set Environment Variables
In Hugging Face Spaces, add these environment variables:
```
DB_HOST=[your-host].planetscale.com
DB_USER=[your-username]
DB_PASSWORD=[your-password]
DB_NAME=vehicle_detection
DB_PORT=3306
```

---

## Option 2: Railway (Free Tier)

### Step 1: Create Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. **No credit card required!**

### Step 2: Create Project
1. Click "New Project"
2. Choose "Provision MySQL"
3. Wait for database to be created

### Step 3: Get Connection Details
1. Click on your MySQL service
2. Go to "Connect" tab
3. Copy connection details:
   ```
   Host: [your-host].railway.app
   Username: root
   Password: [your-password]
   Database: railway
   Port: [your-port]
   ```

### Step 4: Set Environment Variables
```
DB_HOST=[your-host].railway.app
DB_USER=root
DB_PASSWORD=[your-password]
DB_NAME=railway
DB_PORT=[your-port]
```

---

## Option 3: Supabase (PostgreSQL) - Alternative

### Step 1: Create Account
1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub
3. **No credit card required!**

### Step 2: Create Project
1. Click "New project"
2. Choose organization
3. Name: `vehicle-detection`
4. Database password: [create strong password]
5. Region: Choose closest
6. Click "Create new project"

### Step 3: Get Connection Details
1. Go to Settings > Database
2. Copy connection details:
   ```
   Host: [your-host].supabase.co
   Username: postgres
   Password: [your-password]
   Database: postgres
   Port: 5432
   ```

### Step 4: Set Environment Variables
```
DB_HOST=[your-host].supabase.co
DB_USER=postgres
DB_PASSWORD=[your-password]
DB_NAME=postgres
DB_PORT=5432
```

---

## Option 4: Neon (PostgreSQL) - Alternative

### Step 1: Create Account
1. Go to [neon.tech](https://neon.tech)
2. Sign up with GitHub
3. **No credit card required!**

### Step 2: Create Database
1. Click "Create Database"
2. Name: `vehicle-detection`
3. Region: Choose closest
4. Click "Create"

### Step 3: Get Connection Details
1. Go to Dashboard
2. Copy connection string:
   ```
   postgresql://[username]:[password]@[host]/[database]?sslmode=require
   ```

### Step 4: Set Environment Variables
```
DB_HOST=[your-host]
DB_USER=[username]
DB_PASSWORD=[password]
DB_NAME=[database]
DB_PORT=5432
```

---

## 🚀 Hugging Face Spaces Deployment

### Step 1: Create Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Name: `vehicle-detection-system`
4. SDK: Docker
5. Visibility: Public
6. Click "Create Space"

### Step 2: Connect Repository
1. Connect your GitHub repository
2. Set environment variables in Space settings
3. Deploy!

### Step 3: Environment Variables
Add these in Space settings:
```
DB_HOST=[your-database-host]
DB_USER=[your-username]
DB_PASSWORD=[your-password]
DB_NAME=[your-database-name]
DB_PORT=[your-port]
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

---

## 🔧 Local Development (No Database Required)

If you want to test locally without setting up a database:

1. **No environment variables needed**
2. **SQLite will be used automatically**
3. **Database file**: `vehicle_detection.db` (created automatically)
4. **All features work** including analytics dashboard

---

## ✅ Verification

After setup, check if database is working:

1. **Check logs** in Hugging Face Spaces
2. **Look for**: "✅ Database connected successfully"
3. **Test analytics** at `/analytics`
4. **Process a video** and check if data is saved

---

## 🆘 Troubleshooting

### Common Issues:
1. **Connection timeout**: Check host and port
2. **Authentication failed**: Verify username/password
3. **Database not found**: Check database name
4. **SSL required**: Add `?sslmode=require` to connection string

### Fallback:
If MySQL fails, the system automatically falls back to SQLite for local development.

---

**All these options are 100% free with no credit card required!** 🎉
