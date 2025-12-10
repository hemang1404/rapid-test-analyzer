# Quick Setup: Split Frontend & Backend

## 🎯 Goal
Stop showing Render's default loading screen. Show YOUR custom loading screen instead.

## ⚡ 2-Minute Setup

### 1. Update Backend URL in Loader

Edit `frontend/index.html` line 168:

```javascript
const BACKEND_URL = 'https://rapid-test-analyzer.onrender.com'; // ← YOUR Render URL here
```

### 2. Deploy Frontend to Netlify (Drag & Drop)

1. Go to: https://app.netlify.com/drop
2. Drag the `frontend/` folder
3. Drop it
4. Done! You get a URL like: `https://random-name.netlify.app`

### 3. Test It

Visit your Netlify URL:
- ✅ You should see YOUR loading screen immediately
- ✅ It pings your Render backend
- ✅ After 30-60s, backend wakes up
- ✅ Redirects to main app

---

## 📁 What Each File Does

**Frontend Files (Static - Deploy to Netlify):**
- `index.html` - Custom loading screen that pings backend (ENTRY POINT)
- `app.html` - Main app interface
- `result.html` - Results display
- `analyze.js` - Main app logic
- `config.js` - Backend URL configuration
- `netlify.toml` - Netlify deployment config

**Backend Files (API - Already on Render):**
- `app.py` - Flask server
- `*_analyzer.py` - Analysis logic
- All Python files

---

## 🔧 How It Works

```
User visits: https://rapid-test-analyzer.netlify.app
         ↓
Netlify serves index.html instantly (< 1 second)
         ↓
index.html shows spinning logo + "Waking up server..."
         ↓
JavaScript pings: https://rapid-test-analyzer.onrender.com/health
         ↓
Render backend wakes up (30-60 seconds on free tier)
         ↓
Backend responds: { "status": "healthy" }
         ↓
index.html redirects to app.html
         ↓
User can now analyze images!
```

---

## 🚀 Quick Test Locally

**Option A: Using Flask to serve everything (Recommended)**

```bash
# Just run the Flask backend - it serves frontend files too!
python app.py

# Visit: http://localhost:5000/app.html
# Or test loader: http://localhost:5000/index.html
```

**Option B: Separate frontend/backend (simulates production)**

```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend (new terminal)
cd frontend
python -m http.server 8000

# Visit: http://localhost:8000/index.html (loader)
# Or: http://localhost:8000/app.html (main app, but backend needs to be awake)
```

⚠️ **Note:** With Option B, make sure `index.html` line 168 has:
```javascript
const BACKEND_URL = 'http://localhost:5000';
```

---

## 🐛 Troubleshooting

**Issue: "Connection failed" after 60 seconds**
- Check BACKEND_URL in index.html is correct
- Visit backend URL directly to wake it up
- Check browser console (F12) for errors

**Issue: CORS error**
- Already fixed! Your app.py allows all origins (`'*'`)
- If you added restrictions, add your Netlify URL

**Issue: Loader never finishes**
- Check if /health endpoint exists in your backend
- It should already exist (line 123 in app.py)

---

## 📊 Cost

- **Frontend (Netlify):** FREE forever
- **Backend (Render):** FREE (with 30-60s cold start)
- **Total:** $0/month 🎉

---

## Next Steps After Deployment

1. ✅ Custom domain (optional): Connect yourdomain.com to Netlify
2. ✅ Update README with new URL
3. ✅ Add to portfolio/resume
4. ✅ Start building auth features!

---

**Ready?** Just drag `frontend/` folder to Netlify and update the BACKEND_URL. That's it!
