# 🪟 MindPilot - Windows Setup Guide

Super simple setup for Windows 11 with Docker!

---

## 📋 Prerequisites

**You need:**
1. ✅ **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
2. ✅ **Anthropic API Key** - [Get free key here](https://console.anthropic.com)

That's it! Docker will handle everything else.

---

## 🚀 Quick Start (5 minutes)

### Step 1: Make Sure Docker is Running

1. Open **Docker Desktop**
2. Wait for it to say "Docker Desktop is running"
3. You should see the whale icon in your system tray

### Step 2: Get Your API Key

1. Go to https://console.anthropic.com
2. Sign up for a free account
3. Create an API key
4. **Copy the key** - it looks like: `sk-ant-xxxxx...`

### Step 3: Run the Setup Script

Open **PowerShell** in the MindPilot folder and run:

```powershell
.\setup-windows.ps1
```

The script will:
- ✅ Check if Docker is running
- ✅ Ask for your API key
- ✅ Start the database
- ✅ Start the backend API
- ✅ Set everything up automatically

**That's it!** 🎉

---

## 🌐 Access MindPilot

Once setup is complete:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (interactive testing!)
- **Database**: localhost:5432

---

## 📱 Testing the API

### Option 1: Use the Built-in API Docs

1. Open your browser
2. Go to: http://localhost:8000/docs
3. You'll see a beautiful interface to test all endpoints!

### Option 2: Test with PowerShell

**Create a test account:**
```powershell
$body = @{
    email = "test@example.com"
    password = "testpass123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/signup" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**Check health:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

---

## 🎮 Useful Docker Commands

Open PowerShell in the MindPilot folder:

### View logs (see what's happening)
```powershell
docker-compose logs -f
```
Press `Ctrl+C` to stop viewing logs

### Stop MindPilot
```powershell
docker-compose down
```

### Start MindPilot again
```powershell
docker-compose up -d
```

### Restart everything
```powershell
docker-compose restart
```

### Check status
```powershell
docker-compose ps
```

### View database logs
```powershell
docker-compose logs db
```

### View backend logs
```powershell
docker-compose logs backend
```

### Start fresh (delete everything and restart)
```powershell
docker-compose down -v
docker-compose up -d --build
```

---

## 🔧 Configuration

### Edit Environment Variables

Edit the `.env` file in the MindPilot folder:

```powershell
notepad .env
```

**Required:**
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Optional (for payment features):**
- `STRIPE_SECRET_KEY` - From https://stripe.com
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_MONTHLY_PRICE_ID`
- `STRIPE_YEARLY_PRICE_ID`

After editing, restart:
```powershell
docker-compose restart backend
```

---

## 📖 API Endpoints Overview

All endpoints are available at http://localhost:8000/docs

**Main Features:**

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `GET /auth/me` - Get your profile

### Mood Tracking
- `POST /mood/checkin` - Log your mood (gets AI reflection!)
- `GET /mood/history` - See past moods
- `GET /mood/patterns` - Get mood analysis

### AI Journaling
- `POST /journal/entries` - Write journal entry (gets AI analysis!)
- `GET /journal/entries` - Read past entries
- `GET /journal/weekly-summary` - AI weekly summary (premium)

### Habits
- `POST /habits/` - Create new habit
- `GET /habits/` - List your habits
- `POST /habits/{id}/complete` - Mark habit as done

### Insights
- `GET /insights/dashboard` - Your wellness dashboard
- `GET /insights/weekly` - Weekly wellness report (premium)

### Audio
- `GET /audio/content` - Browse meditation sessions
- `POST /audio/sessions` - Log listening session

---

## 🐛 Troubleshooting

### "Port 8000 is already in use"

Something else is using port 8000. Fix it:

```powershell
# Find what's using the port
netstat -ano | findstr :8000

# Stop MindPilot
docker-compose down

# Start again
docker-compose up -d
```

### "Docker is not running"

1. Open **Docker Desktop**
2. Wait for it to fully start
3. Try the setup script again

### "Cannot connect to database"

```powershell
# Restart the database
docker-compose restart db

# Check database logs
docker-compose logs db

# If that doesn't work, start fresh
docker-compose down -v
docker-compose up -d
```

### "API returns 500 errors"

Check the logs:
```powershell
docker-compose logs backend
```

Common causes:
- Missing or invalid API key in `.env`
- Database not ready yet (wait 30 seconds after startup)

### Completely Start Over

```powershell
# Stop everything
docker-compose down -v

# Remove all containers and images
docker system prune -a

# Start fresh
.\setup-windows.ps1
```

---

## 💡 Tips

1. **Keep Docker Desktop running** while using MindPilot
2. **Check logs** if something isn't working: `docker-compose logs -f`
3. **Test the API** at http://localhost:8000/docs
4. **Database data persists** even when you stop Docker (it's saved in a Docker volume)

---

## 🎯 What's Running?

When you start MindPilot, Docker creates 2 containers:

1. **mindpilot-db** (PostgreSQL database)
   - Stores all your data
   - Port 5432

2. **mindpilot-backend** (FastAPI server)
   - The API and AI features
   - Port 8000

You can see them in Docker Desktop or run:
```powershell
docker-compose ps
```

---

## 📊 View Database (Optional)

Want to see the data? Install a database viewer:

**Option 1: DBeaver (Free)**
- Download: https://dbeaver.io
- Connect to: `localhost:5432`
- Database: `mindpilot`
- User: `postgres`
- Password: `postgres123`

**Option 2: Use Docker**
```powershell
docker exec -it mindpilot-db psql -U postgres -d mindpilot
```

---

## 🔐 Security Notes

**For development (what you're doing now):**
- Everything runs on localhost
- Only you can access it
- No internet exposure

**Before production:**
- Change all passwords
- Use real secrets
- Enable HTTPS
- See DEPLOYMENT.md

---

## ✅ Checklist

- [ ] Docker Desktop installed and running
- [ ] Got Anthropic API key from https://console.anthropic.com
- [ ] Ran `.\setup-windows.ps1`
- [ ] Added API key to `.env` file
- [ ] Visited http://localhost:8000/docs
- [ ] Tested signup endpoint
- [ ] Everything working! 🎉

---

## 🆘 Need Help?

1. **Check the logs**: `docker-compose logs -f`
2. **Restart everything**: `docker-compose restart`
3. **Start fresh**: `docker-compose down -v && docker-compose up -d`
4. **Still stuck?** Open a GitHub issue with your logs

---

## 🎉 You're Ready!

Your MindPilot backend is now running!

Next steps:
1. Test the API at http://localhost:8000/docs
2. Build the mobile app (see frontend folder)
3. Or integrate with any app/service that can make HTTP requests

**Happy wellness tracking! 🧠✨**
