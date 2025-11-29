# Custom Loading Screen Setup

## Overview
The custom loading screen (`/loading`) provides a professional branded experience while your app initializes on Render.com's free tier.

## How to Use the Custom Loading Screen

### Option 1: Set as Default Landing Page (Recommended)
If you want users to always see the custom loader first:

1. **Update Render.com Settings:**
   - Go to your Render dashboard
   - Navigate to your service settings
   - Under "Environment Variables", you can't directly set a landing page
   
2. **Alternative: Modify app.py route (recommended):**
   Change the main route to show loading screen first:
   ```python
   @app.route("/")
   def home():
       return send_from_directory('static', 'loading.html')
   
   @app.route("/app")
   def main_app():
       return render_template("index.html")
   ```

### Option 2: Use as Manual Entry Point
Direct users to visit: `https://rapid-test-analyzer.onrender.com/loading`

The loading screen will automatically redirect to the main app after initialization.

### Option 3: Add to Documentation
Simply mention in your README that users should visit `/loading` for the best first-time experience.

## Features of the Custom Loading Screen

✅ **Professional branding** with your app logo and name
✅ **Animated progress indicators** (spinner + pulsing logo)
✅ **Status messages** showing initialization progress
✅ **Floating particles** background animation
✅ **Auto-redirect** to main app after loading
✅ **Fallback protection** (redirects after 10 seconds max)
✅ **Mobile responsive** design

## Customization

Edit `static/loading.html` to customize:
- **Colors**: Change gradient colors in the `background` style
- **Messages**: Modify the `messages` array in the JavaScript
- **Timing**: Adjust `setTimeout` delays
- **Logo**: Replace the emoji 🧪 with an image or icon

## Rate Limiting Fix

The "too many requests" error has been fixed by:
1. ✅ Disabling rate limiting by default (flask-limiter not installed)
2. ✅ Increasing limit from 10 to 50 requests/minute
3. ✅ Disabling in production (Render.com)

You should no longer see this error!

## Testing Locally

1. Run your Flask app: `python app.py`
2. Visit: `http://localhost:5000/loading`
3. Watch the loading animation and auto-redirect

## Deployment

The loading screen is already committed. Just push to GitHub and Render will auto-deploy:
```bash
git add .
git commit -m "Add custom loading screen and fix rate limiting"
git push origin main
```

## Troubleshooting

**Q: Loading screen doesn't redirect**
A: Clear your browser cache or check browser console for errors

**Q: Still seeing Render's default loader**
A: The Render loader appears during container startup (30-60 seconds on free tier). Your custom loader appears after the container is ready.

**Q: Want to skip the loading screen**
A: Just visit the main URL - the loading screen is optional at `/loading`
