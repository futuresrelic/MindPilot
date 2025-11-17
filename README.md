# 🧠 MindPilot - AI Habit & Mental Health Companion

<div align="center">

![MindPilot Logo](https://via.placeholder.com/150)

**Your intelligent companion for mental wellness, habit building, and emotional growth**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React Native](https://img.shields.io/badge/React_Native-0.73-61DAFB.svg)](https://reactnative.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)

</div>

---

## 📱 What is MindPilot?

MindPilot is a comprehensive mental wellness companion that combines AI-powered insights, habit tracking, and personalized support to help you build better mental health practices.

### ✨ Key Features

- **🎭 Mood Tracking** - Daily check-ins with AI-powered reflections
- **📝 AI Journaling** - Get intelligent summaries and CBT-style suggestions
- **✅ Habit Building** - Track habits with streaks and reminders
- **🎧 Guided Sessions** - Meditation, sleep, breathing exercises
- **📊 Insights & Analytics** - Visualize your wellness journey
- **💤 Sleep Tracking** - Monitor and improve sleep quality
- **🧘 CBT Support** - AI-powered cognitive behavioral therapy techniques
- **📈 Weekly Reports** - Personalized wellness summaries
- **💎 Premium Features** - Unlimited access to all content

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Anthropic Claude** - AI-powered insights and reflections
- **Stripe** - Payment processing
- **JWT** - Secure authentication

### Frontend
- **React Native** - Cross-platform mobile development
- **Expo** - React Native toolchain
- **TypeScript** - Type-safe JavaScript
- **Zustand** - State management
- **React Query** - Data fetching and caching
- **Victory Native** - Data visualization
- **Expo AV** - Audio player

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Expo CLI**
- **Anthropic API Key**
- **Stripe Account** (for subscriptions)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mindpilot.git
   cd mindpilot
   ```

2. **Setup Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database**
   ```bash
   createdb mindpilot
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

   Required variables:
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mindpilot
   JWT_SECRET_KEY=your-secret-key-min-32-characters
   ANTHROPIC_API_KEY=your-anthropic-api-key
   STRIPE_SECRET_KEY=your-stripe-secret-key
   STRIPE_WEBHOOK_SECRET=your-webhook-secret
   STRIPE_MONTHLY_PRICE_ID=price_xxxxx
   STRIPE_YEARLY_PRICE_ID=price_xxxxx
   ```

6. **Initialize database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

7. **Seed sample data**
   ```bash
   python seed.py
   ```

8. **Run the backend**
   ```bash
   uvicorn main:app --reload
   ```

   Backend will run at `http://localhost:8000`

   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   echo "EXPO_PUBLIC_API_URL=http://localhost:8000" > .env
   ```

4. **Start Expo**
   ```bash
   npx expo start
   ```

5. **Run on device/simulator**
   - **iOS**: Press `i` (requires Xcode)
   - **Android**: Press `a` (requires Android Studio)
   - **Expo Go**: Scan QR code with Expo Go app

---

## 📖 API Documentation

### Authentication

**Signup**
```bash
POST /auth/signup
{
  "email": "user@example.com",
  "password": "password123",
  "age_range": "25-34",
  "goals": ["stress", "mindfulness"]
}
```

**Login**
```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Mood Tracking

**Check-in**
```bash
POST /mood/checkin
Authorization: Bearer {token}
{
  "mood_value": 7,
  "tags": ["happy", "energized"],
  "note": "Great day!"
}
```

**Get History**
```bash
GET /mood/history?days=30
Authorization: Bearer {token}
```

### Journaling

**Create Entry**
```bash
POST /journal/entries
Authorization: Bearer {token}
{
  "text": "Today I felt grateful for..."
}
```

**Get Entries**
```bash
GET /journal/entries?limit=20&offset=0
Authorization: Bearer {token}
```

### Habits

**Create Habit**
```bash
POST /habits/
Authorization: Bearer {token}
{
  "title": "Morning Meditation",
  "description": "10 minutes of mindfulness",
  "recurrence": "daily"
}
```

**Complete Habit**
```bash
POST /habits/{habit_id}/complete
Authorization: Bearer {token}
```

See full API documentation at `/docs` when backend is running.

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest test_api.py -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🎨 Design System

MindPilot uses a calm, welcoming design inspired by Calm, Headspace, and Finch.

### Color Palette

- **Soft Blue**: `#6FA8FF` - Primary action color
- **Calm Pink**: `#FF9FB0` - Accent color
- **Lavender**: `#B8A2FF` - Secondary accent
- **Aqua**: `#74E4D4` - Success states
- **Midnight**: `#0A0F2B` - Dark backgrounds

### Typography

- **Headings**: Bold, clear, friendly
- **Body**: 16px, comfortable line height
- **Captions**: 12px, subtle secondary info

### Components

- **Cards**: Soft shadows, rounded corners (16px)
- **Buttons**: Gradient backgrounds, clear CTAs
- **Inputs**: Minimal borders, ample padding
- **Spacing**: 4px base unit, consistent rhythm

---

## 💎 Monetization

### Free Tier
- 1 journal entry/day
- 2 active habits
- Basic mood tracking
- Limited audio content

### Premium ($4.99/month or $39/year)
- Unlimited journals
- Unlimited habits
- All audio content
- Sleep analysis
- Weekly AI reports
- CBT sessions
- Priority support

**7-day free trial included**

---

## 🔒 Security

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - Bcrypt for password security
- **HTTPS Only** - SSL/TLS in production
- **Input Validation** - Pydantic models
- **SQL Injection Protection** - ORM queries
- **Rate Limiting** - API throttling
- **Secure Storage** - Expo SecureStore for tokens

---

## 📊 Database Schema

### Users
- id, email, password_hash
- age_range, goals, theme
- subscription_status, subscription_expires
- daily_streak, last_active

### Mood Logs
- id, user_id, mood_value (1-10)
- tags, note, ai_reflection
- created_at

### Journals
- id, user_id, text
- ai_summary, ai_cbt_suggestion
- sentiment, sentiment_score, themes
- created_at

### Habits
- id, user_id, title, description
- recurrence, reminders
- streak, best_streak, total_completions
- last_completed, is_active

### Sleep Logs
- id, user_id, hours, quality
- bedtime, waketime, notes

### Audio Content
- id, title, description, category
- duration_seconds, audio_url
- is_premium, tags

---

## 🚢 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Quick Deploy Options:**
- **Railway** - One-click deploy
- **Render** - Free tier available
- **AWS Lightsail** - $10/month
- **Vercel** (Frontend) + Supabase (Backend)

---

## 🛣️ Roadmap

### Phase 1 (Current)
- ✅ Core features (mood, journal, habits)
- ✅ AI integrations
- ✅ Audio library
- ✅ Stripe subscriptions

### Phase 2 (Q2 2024)
- [ ] Social features (optional community)
- [ ] Apple Health integration
- [ ] Google Fit integration
- [ ] Advanced analytics
- [ ] Therapist recommendations

### Phase 3 (Q3 2024)
- [ ] Group challenges
- [ ] Habit sharing
- [ ] Expert content
- [ ] Multi-language support

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude AI for intelligent reflections
- **Stripe** - Payment processing
- **Expo** - React Native development platform
- **FastAPI** - Modern Python web framework

---

## 📧 Support

- **Email**: support@mindpilot.app
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/mindpilot/issues)
- **Documentation**: [docs.mindpilot.app](https://docs.mindpilot.app)

---

## 🌟 Star History

If you find MindPilot helpful, please consider giving it a star ⭐

---

<div align="center">

**Built with ❤️ for mental wellness**

[Website](https://mindpilot.app) • [Twitter](https://twitter.com/mindpilot) • [Discord](https://discord.gg/mindpilot)

</div>
