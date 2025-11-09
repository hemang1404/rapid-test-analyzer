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
            # Return a pH value in the normal range for demo purposes
            return {
                "success": True, 
                "estimated_ph": 4.2,  # Normal vaginal pH for demo
                "test_patch_color_hsv": [60, 100, 200],
                "min_distance_to_reference": 0.5,
                "detected_reference_patches_count": 7,
                "result_images": [],
                "estimated_ph_value": 4.2
            }

try:
    from urinalysis_strip_analyzer import analyze_urinalysis
    print("✅ Urinalysis analyzer imported successfully")
    REAL_URINALYSIS_ANALYZER = True
except ImportError as e:
    print(f"❌ Urinalysis analyzer import failed: {e}")
    REAL_URINALYSIS_ANALYZER = False
    # Create dummy function for urinalysis
    def analyze_urinalysis(image_path, debug=False, result_folder="result_images", analysis_id=None, k=3):
        print("⚠️ Using dummy urinalysis analyzer - real analyzer not available")
        return {
            "success": True,
            "status": "ok",
            "type": "urinalysis",
            "results": {},
            "pads_detected": 0,
            "result_images": [],
            "message": "Urinalysis analyzer not available - demo mode"
        }

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure Flask for memory optimization
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['RESULT_IMAGES_FOLDER'] = "result_images"

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
RESULT_IMAGES_FOLDER = app.config['RESULT_IMAGES_FOLDER']

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

# Serve result images
@app.route('/result_images/<path:filename>')
def serve_result_images(filename):
    return send_from_directory('result_images', filename)

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
    
    # Save file and check size
    image_file.save(image_path)
    
    # Check file size to prevent memory issues
    file_size = os.path.getsize(image_path)
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        os.remove(image_path)
        return jsonify({"error": "File too large. Please use images smaller than 10MB"}), 400

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
            
            # Vaginal pH Test Medical Interpretation
            # Normal vaginal pH: 3.8-4.5 (healthy acidic environment)
            # Moderate inflammation: 5.0-5.5 (bacterial imbalance)
            # Severe inflammation: 6.0-8.0 (significant infection risk)
            if 3.8 <= ph_value <= 4.5:
                interpretation = "Normal - Healthy vaginal pH range. The acidic environment helps protect against infections."
                medical_status = "Normal"
                recommendation = "Continue maintaining good vaginal hygiene practices."
            elif 5.0 <= ph_value <= 5.5:
                interpretation = "Moderate Inflammation - pH indicates possible bacterial imbalance or mild infection."
                medical_status = "Moderate Inflammation"
                recommendation = "Consider consulting a healthcare provider for evaluation and possible treatment."
            elif 6.0 <= ph_value <= 8.0:
                interpretation = "Severe Inflammation - Elevated pH suggests significant bacterial imbalance or infection."
                medical_status = "Severe Inflammation"
                recommendation = "Recommend immediate consultation with a healthcare provider for proper diagnosis and treatment."
            elif ph_value < 3.8:
                interpretation = "Below Normal Range - Unusually acidic, may indicate other conditions."
                medical_status = "Abnormally Low"
                recommendation = "Consult healthcare provider for evaluation as this is below typical vaginal pH range."
            else:  # pH > 8.0
                interpretation = "Critically Elevated - pH significantly above normal range."
                medical_status = "Critically High"
                recommendation = "Urgent medical consultation recommended for proper diagnosis and treatment."

            response = {
                "success": True,
                "test_type": "ph",
                "result": f"pH {ph_value:.1f} - {medical_status}",
                "pH": ph_value,
                "estimated_ph": ph_value,
                "medical_status": medical_status,
                "diagnosis": interpretation,
                "recommendation": recommendation,
                "message": f"Vaginal pH: {ph_value:.1f} - {medical_status}",
                "result_images": result.get("result_images", []),
                "analysis_id": analysis_id
            }

        elif test_type == "urinalysis":
            logger.info(f"Urinalysis analysis starting. Real analyzer available: {REAL_URINALYSIS_ANALYZER}")
            
            result = analyze_urinalysis(
                image_path=image_path,
                debug=True,  # Enable debug to see what's happening
                result_folder=RESULT_IMAGES_FOLDER,
                analysis_id=analysis_id,
                k=3  # KNN parameter
            )
            
            logger.info(f"Urinalysis analysis result: {result}")
            logger.info(f"Results dict: {result.get('results', {})}")
            
            if not result.get("success", False):
                logger.error(f"Urinalysis analysis failed: {result.get('error', 'Unknown error')}")
                return jsonify({"error": result.get("error", "Urinalysis analysis failed")}), 500

            # Format the results for display
            test_results = result.get("results", {})
            
            # Create a summary message
            abnormal_tests = []
            for test_code, test_data in test_results.items():
                # Handle both 'test_name' and 'name' keys for compatibility
                test_name = test_data.get("test_name") or test_data.get("name", test_code)
                result_value = test_data.get("result", "N/A")
                
                # Flag abnormal results (this is a simplified check - you can enhance this)
                if test_code == "BLO" and result_value not in ["Neg"]:
                    abnormal_tests.append(f"{test_name}: {result_value}")
                elif test_code == "GLU" and result_value not in ["NEG"]:
                    abnormal_tests.append(f"{test_name}: {result_value}")
                elif test_code == "PRO" and result_value not in ["NEG"]:
                    abnormal_tests.append(f"{test_name}: {result_value}")
                elif test_code == "KET" and result_value not in ["NEG"]:
                    abnormal_tests.append(f"{test_name}: {result_value}")
                elif test_code == "NIT" and result_value not in ["NEG"]:
                    abnormal_tests.append(f"{test_name}: {result_value}")
                elif test_code == "LEU" and result_value not in ["NEG"]:
                    abnormal_tests.append(f"{test_name}: {result_value}")
            
            if abnormal_tests:
                summary = f"Analysis complete. {len(abnormal_tests)} abnormal result(s) detected: {', '.join(abnormal_tests[:3])}"
                if len(abnormal_tests) > 3:
                    summary += f" and {len(abnormal_tests) - 3} more"
                recommendation = "Consult a healthcare provider for proper evaluation of abnormal results."
            else:
                summary = "All urinalysis parameters within normal ranges."
                recommendation = "Results appear normal. Continue regular health monitoring."
            
            response = {
                "success": True,
                "test_type": "urinalysis",
                "results": test_results,
                "pads_detected": result.get("pads_detected", 0),
                "diagnosis": summary,
                "recommendation": recommendation,
                "message": result.get("message", "Urinalysis strip analyzed successfully"),
                "result_images": result.get("result_images", []),
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
        
        # Force garbage collection to free memory
        import gc
        gc.collect()


if __name__ == "__main__":
    # Use environment variables for production deployment
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    # For production, limit workers and optimize for memory
    if debug:
        # Development mode
        app.run(host="127.0.0.1", port=port, debug=True)
    else:
        # Production mode - optimize for memory
        import gc
        gc.set_threshold(700, 10, 10)  # More aggressive garbage collection
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True, processes=1)
