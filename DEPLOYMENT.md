# MindPilot Deployment Guide

Complete guide for deploying MindPilot to production.

---

## Table of Contents

1. [Backend Deployment](#backend-deployment)
2. [Database Setup](#database-setup)
3. [Frontend Deployment](#frontend-deployment)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment](#post-deployment)

---

## Backend Deployment

### Option 1: Deploy to Railway

1. **Create Railway Account**
   - Visit https://railway.app
   - Sign up with GitHub

2. **Deploy Backend**
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

3. **Add PostgreSQL Database**
   - In Railway dashboard, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

4. **Set Environment Variables**
   - Go to your project → Variables
   - Add all variables from `.env.example`

5. **Deploy**
   ```bash
   railway up
   ```

### Option 2: Deploy to Render

1. **Create Render Account**
   - Visit https://render.com

2. **Create Web Service**
   - New → Web Service
   - Connect your GitHub repo
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL Database**
   - New → PostgreSQL
   - Copy the Internal Database URL

4. **Set Environment Variables**
   - Go to your web service → Environment
   - Add variables from `.env.example`
   - Set `DATABASE_URL` to your PostgreSQL URL

### Option 3: AWS Lightsail

1. **Create Lightsail Instance**
   - Choose OS: Ubuntu 22.04
   - Choose plan: $10/month or higher

2. **SSH into Instance**
   ```bash
   ssh ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv postgresql nginx -y
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/mindpilot.git
   cd mindpilot/backend
   ```

5. **Setup Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Setup PostgreSQL**
   ```bash
   sudo -u postgres createdb mindpilot
   sudo -u postgres psql
   CREATE USER mindpilot WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE mindpilot TO mindpilot;
   \q
   ```

7. **Create Environment File**
   ```bash
   nano .env
   # Add all environment variables
   ```

8. **Run with Systemd**
   ```bash
   sudo nano /etc/systemd/system/mindpilot.service
   ```

   Add:
   ```ini
   [Unit]
   Description=MindPilot API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/mindpilot/backend
   Environment="PATH=/home/ubuntu/mindpilot/backend/venv/bin"
   ExecStart=/home/ubuntu/mindpilot/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable mindpilot
   sudo systemctl start mindpilot
   sudo systemctl status mindpilot
   ```

9. **Setup Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/mindpilot
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/mindpilot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Database Setup

### PostgreSQL Production Setup

1. **Create Database**
   ```sql
   CREATE DATABASE mindpilot_prod;
   ```

2. **Run Migrations**
   ```bash
   cd backend
   python -c "from database import init_db; init_db()"
   ```

3. **Seed Data** (Audio Content)
   ```bash
   python seed.py
   ```

4. **Backup Strategy**
   ```bash
   # Daily backups
   pg_dump mindpilot_prod > backup_$(date +%Y%m%d).sql
   ```

---

## Frontend Deployment

### Build for Production

1. **Install EAS CLI**
   ```bash
   npm install -g eas-cli
   ```

2. **Configure EAS**
   ```bash
   cd frontend
   eas login
   eas build:configure
   ```

3. **Update API URL**
   Create `.env.production`:
   ```bash
   EXPO_PUBLIC_API_URL=https://your-api-domain.com
   ```

### iOS Deployment

1. **Build for iOS**
   ```bash
   eas build --platform ios
   ```

2. **Submit to App Store**
   ```bash
   eas submit --platform ios
   ```

### Android Deployment

1. **Build for Android**
   ```bash
   eas build --platform android
   ```

2. **Submit to Google Play**
   ```bash
   eas submit --platform android
   ```

### OTA Updates

```bash
eas update --branch production --message "Bug fixes and improvements"
```

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/mindpilot

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_MONTHLY_PRICE_ID=price_xxxxx
STRIPE_YEARLY_PRICE_ID=price_xxxxx

# Environment
ENV=production
```

### Frontend (.env.production)

```bash
EXPO_PUBLIC_API_URL=https://api.mindpilot.com
```

---

## Post-Deployment

### 1. Setup Monitoring

**Backend Monitoring (Sentry)**
```bash
pip install sentry-sdk
```

In `main.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

**Frontend Monitoring**
```bash
npx expo install sentry-expo
```

### 2. Setup SSL/HTTPS

**Let's Encrypt (Free SSL)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Configure Stripe Webhooks

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-api.com/subscription/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

### 4. Test Production

```bash
# Test API
curl https://your-api.com/health

# Test authentication
curl -X POST https://your-api.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### 5. Setup Backups

**Automated Database Backups**
```bash
# Add to crontab
0 2 * * * pg_dump mindpilot_prod | gzip > /backups/mindpilot_$(date +\%Y\%m\%d).sql.gz
```

### 6. Performance Optimization

**Backend**
- Enable GZIP compression
- Use connection pooling
- Add Redis for caching (optional)

**Frontend**
- Optimize images
- Enable Hermes engine
- Use ProGuard for Android

---

## Scaling

### Horizontal Scaling

1. **Load Balancer** (AWS ALB, Nginx)
2. **Multiple Backend Instances**
3. **Database Read Replicas**
4. **CDN** for static assets

### Database Scaling

- Add read replicas
- Use connection pooling (PgBouncer)
- Implement caching (Redis)

---

## Troubleshooting

### Backend Issues

```bash
# Check logs
tail -f /var/log/mindpilot/api.log

# Check service status
sudo systemctl status mindpilot

# Restart service
sudo systemctl restart mindpilot
```

### Database Issues

```bash
# Check connections
SELECT * FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('mindpilot_prod'));
```

---

## Security Checklist

- ✅ Use HTTPS/SSL
- ✅ Secure environment variables
- ✅ Enable CORS properly
- ✅ Use strong JWT secrets
- ✅ Rate limiting on API
- ✅ Input validation
- ✅ SQL injection protection (use ORM)
- ✅ Regular security updates

---

## Support

For deployment issues:
- Check logs first
- Review error messages
- Consult platform documentation
- Open GitHub issue if needed

**Production is live! 🎉**
