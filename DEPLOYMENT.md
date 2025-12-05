# Deployment Guide: Split Frontend & Backend

This guide explains how to deploy your frontend and backend separately to avoid Render's default loading screen.

## Architecture

```
User visits site
    ↓
Frontend (Static Site - Netlify/Vercel) - loads instantly
    ↓
Shows YOUR custom loading screen (loader.html)
    ↓
Pings backend /health endpoint
    ↓
Backend (Render.com) - wakes up (30-60s on free tier)
    ↓
Once backend is ready → Redirects to index.html
```

## Option 1: Deploy Frontend on Netlify (Recommended)

### Step 1: Prepare Frontend for Deployment

All your frontend files are in the `frontend/` folder:
- `loader.html` - Entry point (landing page)
- `index.html` - Main app
- `result.html` - Results page
- `analyze.js` - Main logic
- `config.js` - Backend URL configuration
- Other JS/CSS files

### Step 2: Update Backend URL in loader.html

Open `frontend/loader.html` and update line 145:

```javascript
const BACKEND_URL = 'https://your-backend-name.onrender.com'; // ← Change this
```

Replace with your actual Render backend URL.

### Step 3: Deploy to Netlify

1. **Sign up/Login to Netlify**: https://netlify.com
2. **Drag & Drop Deploy**:
   - Go to: https://app.netlify.com/drop
   - Drag the entire `frontend/` folder into the upload box
   - Netlify will deploy it instantly

3. **Or Connect to GitHub**:
   ```bash
   # Create netlify.toml in project root
   ```

   **netlify.toml:**
   ```toml
   [build]
     publish = "frontend/"
     command = "echo 'Static site - no build needed'"

   [[redirects]]
     from = "/*"
     to = "/loader.html"
     status = 200
   ```

   - Push to GitHub
   - Connect repository in Netlify dashboard
   - Deploy!

4. **Set loader.html as homepage**:
   - In Netlify dashboard → Site settings → Build & deploy → Post processing
   - Add redirect rule: `/* /loader.html 200`

### Step 4: Update Backend CORS

Your backend needs to allow requests from Netlify domain.

In `app.py`, update CORS:

```python
@app.after_request
def after_request(response):
    # Add your Netlify URL here
    allowed_origins = [
        'https://your-site-name.netlify.app',
        'http://localhost:5000',  # For development
    ]
    
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
```

---

## Option 2: Deploy Frontend on Vercel

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Deploy

```bash
cd "c:\coding\Project - Copy"
vercel --prod

# Follow prompts:
# - Project name: rapid-test-analyzer-frontend
# - Directory: frontend/
```

### Step 3: Create vercel.json

In `frontend/vercel.json`:

```json
{
  "rewrites": [
    { "source": "/", "destination": "/loader.html" },
    { "source": "/(.*)", "destination": "/$1" }
  ]
}
```

---

## Option 3: Deploy Frontend on GitHub Pages (Free)

### Step 1: Create gh-pages branch

```bash
git checkout -b gh-pages
git rm -rf .  # Clear everything
git checkout main -- frontend/
mv frontend/* .
rm -rf frontend/
git add .
git commit -m "Deploy frontend to GitHub Pages"
git push origin gh-pages
```

### Step 2: Enable GitHub Pages

- Go to repository Settings → Pages
- Source: gh-pages branch
- Save

Your site will be at: `https://username.github.io/rapid-test-analyzer/`

---

## Option 4: Keep Everything Together (Current Setup)

If you don't want to split, modify your Render deployment:

### Create a custom loading endpoint

In `app.py`:

```python
@app.route("/")
def home():
    # Serve your custom loading screen instead of index
    return send_from_directory('static', 'loading.html')

@app.route("/app")
def main_app():
    # The actual app
    return send_from_directory('frontend', 'index.html')
```

**Issue:** Users still wait 30-60s on first visit before seeing anything.

---

## Testing Your Setup

### Local Testing

1. Update `frontend/loader.html` line 145:
   ```javascript
   const BACKEND_URL = 'http://localhost:5000';
   ```

2. Run backend:
   ```bash
   python app.py
   ```

3. Serve frontend with Python:
   ```bash
   cd frontend
   python -m http.server 8000
   ```

4. Visit: http://localhost:8000/loader.html

### Production Testing

1. Deploy frontend to Netlify
2. Update BACKEND_URL to your Render URL
3. Visit your Netlify URL
4. Should see your loading screen, then app loads

---

## Recommended Flow for You

**Best approach for your project:**

1. ✅ Deploy backend to Render (already done)
2. ✅ Deploy frontend to Netlify (takes 2 minutes)
3. ✅ Update BACKEND_URL in loader.html
4. ✅ Update CORS in app.py

**Benefits:**
- Frontend loads instantly (static files)
- Shows YOUR loading screen immediately
- Backend spins up in background (30-60s)
- User sees progress, not blank Render screen
- Free hosting for both!

---

## Need Help?

If you get stuck:
1. Check browser console for errors (F12)
2. Verify BACKEND_URL is correct
3. Check Network tab to see if /health endpoint is reachable
4. Ensure CORS is configured correctly

---

## Quick Deploy Commands

```bash
# 1. Deploy frontend to Netlify
cd "c:\coding\Project - Copy\frontend"
# Drag folder to https://app.netlify.com/drop

# 2. Update loader.html with your Render backend URL
# Edit line 145 in frontend/loader.html

# 3. Push backend changes to Render
git add .
git commit -m "Update CORS for Netlify"
git push origin main

# Done! 🎉
```
