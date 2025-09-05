# Rapid Test Analyzer 🧪

## Overview
Advanced AI-powered medical test analysis system with professional-grade reporting capabilities. Supports pH strip analysis and Fecal Occult Blood (FOB) testing with computer vision and machine learning.

## Features
- **AI-Powered Analysis**: Computer vision algorithms for accurate test interpretation
- **Medical-Grade Reports**: Professional diagnostic reports with clinical styling
- **Multiple Test Types**: pH Analysis, FOB Detection (Urinalysis coming soon)
- **User-Friendly Interface**: Modern, responsive design with accessibility features
- **Real-time Processing**: Fast analysis with progress tracking
- **Professional Styling**: Medical-themed interface with glass morphism effects

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
├── app.py                 # Flask backend server
├── fob_analyzer.py        # FOB test analysis logic
├── ph_strip_analyzer.py   # pH strip analysis logic
├── frontend/
│   ├── index.html         # Main application interface
│   ├── result.html        # Results display page
│   ├── analyze.js         # Frontend JavaScript logic
│   └── result.js          # Results page logic
├── uploads/               # Temporary image storage
└── requirements.txt       # Python dependencies
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
- [x] Professional Medical Reports
- [x] Responsive Design
- [ ] Urinalysis Pipeline
- [ ] User Authentication
- [ ] Test History
- [ ] Multi-language Support

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Medical Disclaimer
This system is for informational purposes only. Results should be verified by qualified healthcare professionals. Not intended to replace professional medical diagnosis.

## Contact
For questions or support, please open an issue on GitHub.
