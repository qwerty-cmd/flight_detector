# Deployment Guide - Free Hosting

## 🚀 Deploy to Render.com (Free Tier)

Your dashboard is ready to deploy for FREE on Render.com!

### What You'll Get

- ✅ **Live Dashboard**: Public URL to view your flight tracker
- ✅ **Demo Mode**: Simulated aircraft data (no hardware needed)
- ✅ **Free Forever**: Render's free tier
- ✅ **Auto-Deploy**: Updates automatically from GitHub
- ✅ **HTTPS**: Secure connection included

### Demo Features

When deployed, the dashboard shows:
- **6 Demo Flights**: Realistic Australian flights
- **Overhead Aircraft**: 1-2 aircraft "flying over" Footscray
- **Live Updates**: Data updates every 5 seconds
- **Full UI**: All dashboard features working

Demo flights include:
- QFA94 (USA → Australia)
- VOZ863 (Australia → New Zealand)
- QFA432 (Domestic Australia)
- JST724 (Domestic Australia)
- QFA7 (UK → Australia)
- SIA231 (Singapore → Australia)

---

## Step-by-Step Deployment

### 1. Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended) or email
4. Verify your email

### 2. Connect Your Repository

1. In Render dashboard, click "**New +**"
2. Select "**Web Service**"
3. Click "**Connect account**" and authorize GitHub
4. Find and select `qwerty-cmd/flight_detector`
5. Click "**Connect**"

### 3. Configure Service

Render will auto-detect the `render.yaml` file. Verify settings:

- **Name**: `flight-tracker-dashboard` (or choose your own)
- **Region**: Oregon (or closest to you)
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
- **Plan**: **Free**

### 4. Environment Variables

Render automatically sets:
- `DEMO_MODE=true` (enables simulated data)
- `PORT` (auto-configured)

### 5. Deploy!

1. Click "**Create Web Service**"
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start the dashboard
   - Assign a public URL

**Deployment takes ~5-10 minutes**

### 6. Access Your Dashboard

Once deployed, you'll get a URL like:
```
https://flight-tracker-dashboard.onrender.com
```

Visit this URL to see your live dashboard! 🎉

---

## Alternative: Railway.app (Also Free)

### Quick Deploy to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `flight_detector`
5. Add environment variable: `DEMO_MODE=true`
6. Click "Deploy"

Railway will auto-detect Python and Flask!

---

## Alternative: Vercel (Free, Serverless)

Note: Vercel has some limitations with long-running processes, so updates may be slower.

1. Go to https://vercel.com
2. Import your GitHub repository
3. Framework Preset: **Other**
4. Build Command: `pip install -r requirements.txt`
5. Output Directory: `.`
6. Install Command: `pip install -r requirements.txt`
7. Add environment variable:
   - Key: `DEMO_MODE`
   - Value: `true`
8. Deploy

---

## Alternative: Heroku (Free Tier Ended)

Heroku no longer offers free tier, but if you have credits:

```bash
# Install Heroku CLI
heroku login
heroku create flight-tracker-dashboard
heroku config:set DEMO_MODE=true
git push heroku main
heroku open
```

---

## Demo Mode vs Production Mode

### Demo Mode (Cloud Deployment)
```yaml
Environment: DEMO_MODE=true
Features:
  - Simulated aircraft data
  - No hardware required
  - Perfect for demonstration
  - Works anywhere
```

### Production Mode (Raspberry Pi)
```yaml
Environment: DEMO_MODE=false (or not set)
Features:
  - Real ADS-B data
  - RTL-SDR dongle required
  - Actual aircraft tracking
  - Footscray, Melbourne location
```

---

## Customizing Your Deployment

### Change Location

Edit `config.yaml` before deployment:

```yaml
location:
  latitude: YOUR_LAT
  longitude: YOUR_LON
```

### Add More Demo Flights

Edit `src/demo_data.py`:

```python
DEMO_FLIGHTS = [
    {'icao': 'ABC123', 'callsign': 'TEST123', 'origin': 'Country', 'dest': 'Country'},
    # Add more...
]
```

### Adjust Update Speed

In `wsgi.py`, change:

```python
dashboard.start_background_updates(interval=5)  # seconds
```

---

## Troubleshooting

### Deployment Failed

**Check Logs**:
- Render: Click on service → "Logs" tab
- Railway: Click on deployment → "View Logs"

**Common Issues**:

1. **Build failed**
   - Check `requirements.txt` is valid
   - Ensure all files committed to GitHub

2. **Application error**
   - Check `DEMO_MODE=true` is set
   - Verify `config.yaml` exists

3. **Port binding error**
   - Render/Railway auto-set PORT
   - wsgi.py reads from environment

### Dashboard Shows Errors

1. Check browser console (F12)
2. Verify API endpoints respond:
   - `/api/status`
   - `/api/stats`
   - `/api/aircraft`

### No Aircraft Showing

**In Demo Mode**: Should always show 3-6 aircraft
- Refresh page
- Check browser console for errors
- View deployment logs

**In Production Mode**: Need real ADS-B data
- Ensure `DEMO_MODE=false`
- Connect RTL-SDR hardware
- Start readsb service

---

## Monitoring Your Deployment

### Render.com

- **Dashboard**: View service status
- **Logs**: Real-time application logs
- **Metrics**: Request counts, response times
- **Custom Domain**: Add your own domain (free)

### Railway.app

- **Deployment Logs**: Build and runtime logs
- **Metrics**: CPU, memory, bandwidth
- **Environment**: Manage environment variables

---

## Updating Your Deployment

### Automatic Updates (Recommended)

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```
3. Render/Railway auto-deploys!

### Manual Deploy

- **Render**: Click "Manual Deploy" → "Deploy latest commit"
- **Railway**: Click "Redeploy"

---

## Free Tier Limits

### Render.com Free Tier
- ✅ 750 hours/month
- ✅ Automatic HTTPS
- ✅ Custom domains
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Slower build times

**Pro Tip**: Service wakes up automatically when visited (30-60s delay)

### Railway.app Free Tier
- ✅ $5 free credit/month
- ✅ Fast deployments
- ✅ No sleep mode
- ⚠️ Credit limited

### Vercel Free Tier
- ✅ Unlimited deployments
- ✅ Very fast
- ⚠️ Serverless limitations

---

## Upgrade Options

If you love the dashboard and want more:

### Render Paid ($7/month)
- No sleep mode
- Faster builds
- More resources

### Railway Paid ($5+/month)
- More credits
- Priority support
- Dedicated resources

---

## Production Deployment (Raspberry Pi)

For real aircraft tracking with hardware:

1. Set up Raspberry Pi with RTL-SDR
2. Follow main README.md installation
3. Set `DEMO_MODE=false` (or remove variable)
4. Run dashboard locally or on your network
5. Optional: Use Cloudflare Tunnel for remote access

---

## Security Notes

### Demo Mode (Public)
- ✅ Safe to share publicly
- ✅ No sensitive data
- ✅ Simulated data only

### Production Mode (Private)
- ⚠️ Shows real aircraft positions
- ⚠️ Reveals your location
- ⚠️ Add authentication if public
- Recommended: Keep on local network only

---

## Success Checklist

After deployment, verify:

- [ ] Dashboard loads at your URL
- [ ] System Status shows "Running"
- [ ] Statistics update every 5 seconds
- [ ] Aircraft list shows 3-6 aircraft
- [ ] Overhead section shows 0-2 aircraft
- [ ] Recent flights populate over time
- [ ] Configuration shows Footscray location
- [ ] All API endpoints respond
- [ ] No errors in browser console

---

## Getting Help

**Deployment Issues**:
- Check platform documentation (Render, Railway, Vercel)
- Review deployment logs
- Verify GitHub repository is public

**Application Issues**:
- Check DASHBOARD_README.md
- Review browser console
- Check application logs

**Questions**:
- Open issue on GitHub
- Check README.md troubleshooting

---

## Next Steps

1. ✅ Deploy to your chosen platform
2. ✅ Share your dashboard URL
3. ✅ Monitor the demo aircraft
4. ⭐ Star the GitHub repository
5. 🚀 Deploy to Raspberry Pi for real tracking

---

**Your dashboard is ready for the world!** 🌍✈️

*Live demo of Melbourne airspace in Footscray, VIC*
