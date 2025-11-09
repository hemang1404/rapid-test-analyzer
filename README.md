# Rapid Test Analyzer 🧪

🌐 **Live Demo**: [https://rapid-test-analyzer.onrender.com](https://rapid-test-analyzer.onrender.com)

## Overview
Advanced AI-powered medical test analysis system with professional-grade reporting capabilities. Supports pH strip analysis, Fecal Occult Blood (FOB) testing, and Urinalysis with computer vision and machine learning.

## Features
- **AI-Powered Analysis**: Computer vision algorithms for accurate test interpretation
- **Medical-Grade Reports**: Professional diagnostic reports with clinical styling
- **Multiple Test Types**: 
  - ✅ pH Analysis (Vaginal pH Testing)
  - ✅ FOB Detection (Fecal Occult Blood)
  - ✅ Urinalysis (10-parameter comprehensive urine analysis)
- **User-Friendly Interface**: Modern, responsive design with accessibility features
- **Real-time Processing**: Fast analysis with progress tracking
- **Professional Styling**: Medical-themed interface with glass morphism effects
- **Confidence Scoring**: KNN-based confidence levels for each result
- **Abnormal Detection**: Automatic flagging of abnormal test results

## Urinalysis Features
- **10 Parameters Analyzed**:
  - Blood (Hemoglobin/Non-Hemoglobin detection)
  - Bilirubin
  - Urobilinogen
  - Ketones
  - Protein
  - Nitrites
  - Glucose
  - pH Level
  - Specific Gravity
  - Leukocytes
- **Automatic Pad Detection**: Detects and analyzes all 10 test pads
- **Missing Pad Reconstruction**: Intelligently fills in missing pads
- **KNN Classification**: K-Nearest Neighbors algorithm for accurate results
- **Detailed Results Table**: Professional medical report format

## Technologies Used
- **Backend**: Python, Flask, OpenCV, scikit-learn, NumPy
- **Frontend**: HTML5, CSS3 (TailwindCSS), Vanilla JavaScript
- **AI/ML**: Computer vision algorithms, image processing
- **Styling**: Glass morphism, responsive design, accessibility features

## Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/rapid-test-analyzer.git
cd rapid-test-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage
1. **Select Test Type**: Choose from pH Analysis or FOB Detection
2. **Upload Image**: Drag & drop or select your test image
3. **Analyze**: Click analyze to process your image
4. **View Results**: Get professional medical-style reports

## Project Structure
```
├── app.py                        # Flask backend server
├── fob_analyzer.py               # FOB test analysis logic
├── ph_strip_analyzer.py          # pH strip analysis logic
├── urinalysis_strip_analyzer.py  # Urinalysis analysis logic (KNN-based)
├── frontend/
│   ├── index.html                # Main application interface
│   ├── result.html               # Results display page
│   ├── analyze.js                # Frontend JavaScript logic
│   └── result.js                 # Results page logic
├── templates/                    # Flask templates
├── static/                       # Static assets
├── uploads/                      # Temporary image storage
├── result_images/                # Analysis result images
├── requirements.txt              # Python dependencies
├── Procfile                      # Deployment configuration
├── runtime.txt                   # Python version
└── render.yaml                   # Render.com deployment config
```

## API Endpoints
- `GET /` - Main application interface
- `POST /analyze` - Image analysis endpoint
- `GET /result` - Results display page

## Supported File Types
- PNG, JPG, JPEG, GIF, BMP
- Maximum file size: 10MB

## Development Roadmap
- [x] pH Strip Analysis
- [x] FOB Detection
- [x] Urinalysis (10-parameter analysis)
- [x] Professional Medical Reports
- [x] Responsive Design
- [x] KNN-based Classification
- [x] Confidence Scoring
- [x] Abnormal Result Detection
- [ ] User Authentication
- [ ] Test History
- [ ] Multi-language Support
- [ ] Export to PDF
- [ ] API Documentation

## Deployment

### Deploy to Render.com (Recommended - Free)

## Deployment

### Deploy to Render.com (Recommended - Free)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Sign up/Login to Render.com**:
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

3. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `rapid-test-analyzer` repository

4. **Configure the service**:
   - **Name**: `rapid-test-analyzer` (or your preferred name)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 60`
   - **Plan**: Free

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for the build to complete (5-10 minutes)
   - Your app will be live at `https://your-app-name.onrender.com`

### Deploy to Railway.app

1. **Push to GitHub** (if not already done)

2. **Deploy on Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect Flask and deploy

### Environment Variables (if needed)
No environment variables required for basic deployment. The app works out of the box!

### Post-Deployment
- The first request may take 30-60 seconds as the server spins up (free tier)
- Subsequent requests will be faster
- Upload limit: 16MB (configurable in app.py)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Medical Disclaimer
This system is for informational purposes only. Results should be verified by qualified healthcare professionals. Not intended to replace professional medical diagnosis.

## Contact
For questions or support, please open an issue on GitHub.
