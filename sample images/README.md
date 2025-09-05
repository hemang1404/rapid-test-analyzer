# Sample Images for Medical Test Analyzer

## ⚠️ IMPORTANT: For Web Deployment

**The file dialog approach only works locally.** For deployed applications (Railway, GitHub Pages, etc.), the sample images are now served as **static files** and accessed via a **modal interface**.

## Current Setup

### For Local Development:
- Use this folder structure for manual file browsing
- The "Sample Images" button opens your local file dialog

### For Web Deployment:
- Sample images are stored in `/static/sample-images/`
- Configuration is in `/frontend/sample-images-config.js`
- Images are displayed in a modal with preview

## Web Deployment Structure

```
static/sample-images/
├── ph/
│   ├── ph_acidic_sample.jpg
│   ├── ph_neutral_sample.jpg
│   └── ph_basic_sample.jpg
└── fob/
    ├── fob_positive_sample.jpg
    └── fob_negative_sample.jpg
```

## How to Add Real Sample Images

1. **Place images** in `/static/sample-images/ph/` or `/static/sample-images/fob/`
2. **Update configuration** in `/frontend/sample-images-config.js`:
   ```javascript
   {
       name: "Your Image Name",
       description: "Description of the test result",
       url: "/static/sample-images/ph/your_image.jpg",
       placeholder: false  // Set to false for real images
   }
   ```
3. **Deploy** - Images will be served statically and shown in the modal

## Fallback Behavior

- If real images aren't found, **demo images are generated** automatically
- Users can still test the application functionality
- No broken image links or empty modals

## Example File Names
- `ph_acidic_sample.jpg` (pH 4-5)
- `ph_neutral_sample.jpg` (pH 7)  
- `ph_basic_sample.jpg` (pH 9-10)
- `fob_positive_sample.jpg` (Two lines visible)
- `fob_negative_sample.jpg` (Control line only)

## Benefits of This Approach
✅ Works on deployed applications  
✅ Fast loading (static files)  
✅ No cloud storage costs  
✅ Automatic fallback to demo images  
✅ Easy to manage and update
