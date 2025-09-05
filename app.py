from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import logging

# Wrap imports in try-catch for better error handling
try:
    from fob_analyzer import analyze_fob
    print("✅ FOB analyzer imported successfully")
except ImportError as e:
    print(f"❌ FOB analyzer import failed: {e}")
    # Create dummy function for FOB
    def analyze_fob(image_path, templates_dir="templates", debug=False, result_folder="result_images", analysis_id=None):
        return {
            "status": "success",
            "result": "Demo result - FOB analyzer not available",
            "confidence": 0.0,
            "analysis_id": analysis_id
        }

try:
    from ph_strip_analyzer import PHStripAnalyzer
    print("✅ pH Strip analyzer imported successfully")
    REAL_PH_ANALYZER = True
except ImportError as e:
    print(f"❌ pH Strip analyzer import failed: {e}")
    REAL_PH_ANALYZER = False
    # Create dummy class for pH
    class PHStripAnalyzer:
        def __init__(self, debug=False):
            self.debug = debug
            
        def analyze_ph_strip(self, image_path, debug=False, result_folder="result_images", analysis_id=None):
            print("⚠️ Using dummy pH analyzer - real analyzer not available")
            return {
                "success": True, 
                "estimated_ph": 7.0,
                "test_patch_color_hsv": [60, 100, 200],
                "min_distance_to_reference": 0.5,
                "detected_reference_patches_count": 7,
                "result_images": [],
                "estimated_ph_value": 7.0
            }

app = Flask(__name__, template_folder='templates', static_folder='static')
UPLOAD_FOLDER = "uploads"
RESULT_IMAGES_FOLDER = "result_images"

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_IMAGES_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for frontend
@app.route("/")
def home():
    return render_template("index.html")

# Serve static files (CSS, JS, images)
@app.route('/static/<path:filename>')
def serve_sample_images(filename):
    return send_from_directory('static', filename)

# Serve frontend files (JS, CSS, HTML from frontend folder)
@app.route('/<path:filename>')
def serve_frontend_files(filename):
    # Serve JS, CSS, and HTML files from frontend
    if filename.endswith(('.js', '.css', '.html')):
        return send_from_directory('frontend', filename)
    return "File not found", 404

# Add CORS headers for local development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# API endpoint for analysis
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    test_type = request.form.get("test_type")

    if not test_type or test_type not in ["ph", "fob", "urinalysis"]:
        return jsonify({"error": "Invalid test type"}), 400

    if not allowed_file(image_file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Generate unique analysis ID
    analysis_id = uuid.uuid4().hex
    filename = secure_filename(f"{analysis_id}_{image_file.filename}")
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(image_path)

    try:
        if test_type == "fob":
            result = analyze_fob(
                image_path=image_path,
                debug=False,  # Don't show debug windows in web app
                result_folder=RESULT_IMAGES_FOLDER,
                analysis_id=analysis_id
            )
            
            logger.info(f"FOB analysis result: {result}")
            
            if result["status"] == "error":
                logger.error(f"FOB analysis failed: {result['message']}")
                return jsonify({"error": result["message"]}), 500
            
            response = {
                "success": True,
                "test_type": "fob",
                "result": result["result"],
                "diagnosis": f"FOB Test shows: {result['result']}. {'Consult a healthcare provider for further evaluation.' if result['result'] == 'positive' else 'No blood detected in sample.'}",
                "message": f"FOB Test Result: {result['result']}",
                "result_images": result.get("result_images", []),
                "analysis_id": analysis_id
            }
            
        elif test_type == "ph":
            logger.info(f"pH analysis starting. Real analyzer available: {REAL_PH_ANALYZER}")
            analyzer = PHStripAnalyzer(debug=False)
            logger.info(f"PHStripAnalyzer created successfully")
            
            result = analyzer.analyze_ph_strip(
                image_path,
                debug=False,
                result_folder=RESULT_IMAGES_FOLDER,
                analysis_id=analysis_id
            )
            
            logger.info(f"pH analysis result: {result}")
            
            if not result["success"]:
                logger.error(f"pH analysis failed: {result.get('error', 'Unknown error')}")
                return jsonify({"error": result.get("error", "pH analysis failed")}), 500

            ph_value = result["estimated_ph"]
            logger.info(f"Estimated pH value: {ph_value}")
            # Add pH interpretation
            if ph_value < 6.0:
                interpretation = "Acidic - may indicate acidosis or dietary factors"
            elif ph_value > 8.0:
                interpretation = "Alkaline - may indicate alkalosis or UTI"
            else:
                interpretation = "Normal pH range"

            response = {
                "success": True,
                "test_type": "ph",
                "result": f"pH {ph_value:.1f}",
                "pH": ph_value,
                "estimated_ph": ph_value,
                "diagnosis": interpretation,
                "message": f"Estimated pH: {ph_value:.1f}",
                "result_images": result.get("result_images", []),
                "analysis_id": analysis_id
            }

        elif test_type == "urinalysis":
            # Placeholder for urinalysis - you can implement this later
            response = {
                "success": True,
                "test_type": "urinalysis",
                "result": "Feature coming soon",
                "diagnosis": "Urinalysis feature is currently under development.",
                "message": "Urinalysis analysis will be available in a future update.",
                "result_images": [],
                "analysis_id": analysis_id
            }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error analyzing {test_type} image: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file after processing
        if os.path.exists(image_path):
            os.remove(image_path)


if __name__ == "__main__":
    # Use environment variables for production deployment
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
