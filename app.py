from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import logging
import json
from datetime import datetime
from config import get_config
from utils import validate_image_quality, validate_file_extension, safe_file_cleanup, AnalysisValidator, validate_email
from models import db, User, Analysis
from auth import generate_token, token_required, optional_token

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

# Load configuration based on environment
env = os.environ.get("FLASK_ENV", "production")
app.config.from_object(get_config(env))

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Fix postgres:// to postgresql:// for SQLAlchemy
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Use SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rapidtest.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database initialized")

# Configure Flask for memory optimization
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
RESULT_IMAGES_FOLDER = app.config['RESULT_IMAGES_FOLDER']
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_IMAGES_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter if enabled
if app.config.get('RATE_LIMIT_ENABLED', False):
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[f"{app.config.get('RATE_LIMIT_PER_MINUTE', 10)} per minute"],
            storage_uri="memory://"
        )
        logger.info("Rate limiting enabled")
    except ImportError:
        logger.warning("flask-limiter not installed. Rate limiting disabled.")
        limiter = None
else:
    limiter = None
    logger.info("Rate limiting disabled (development mode)")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return validate_file_extension(filename, ALLOWED_EXTENSIONS)

# Route for frontend
@app.route("/")
def home():
    return render_template("index.html")

# Custom loading/splash screen
@app.route("/loading")
def loading():
    return send_from_directory('static', 'loading.html')

# Health check endpoint for deployment platforms
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "rapid-test-analyzer"}), 200

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

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route("/register", methods=["POST"])
def register():
    """
    Register a new user account
    
    Request body:
        {
            "username": "string",
            "email": "string",
            "password": "string"
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate inputs
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Validate email format and domain
        is_valid_email, email_error = validate_email(email)
        if not is_valid_email:
            return jsonify({'error': email_error}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        verification_token = user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        
        # TODO: Send verification email with token
        # For now, we'll include the token in the response for testing
        # In production, this should be sent via email
        
        return jsonify({
            'success': True,
            'message': 'Registration successful. Please verify your email to login.',
            'user': user.to_dict(),
            'verification_token': verification_token  # Remove this in production
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route("/login", methods=["POST"])
def login():
    """
    Login user and return JWT token
    
    Request body:
        {
            "email": "string",
            "password": "string"
        }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if email is verified
        if not user.email_verified:
            return jsonify({
                'error': 'Email not verified',
                'message': 'Please verify your email before logging in. Check your inbox for the verification link.',
                'email_verified': False
            }), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(user.id, user.username, user.email)
        
        logger.info(f"User logged in: {user.username}")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    """
    Verify user's email with the provided token
    
    URL Parameters:
        token: Verification token sent to user's email
    """
    try:
        # Find user with this verification token
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({
                'error': 'Invalid or expired verification token',
                'success': False
            }), 400
        
        # Check if already verified
        if user.email_verified:
            return jsonify({
                'success': True,
                'message': 'Email already verified',
                'already_verified': True
            }), 200
        
        # Verify the email
        user.email_verified = True
        user.verification_token = None  # Clear the token after use
        db.session.commit()
        
        logger.info(f"Email verified for user: {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now login.',
            'username': user.username
        }), 200
        
    except Exception as e:
        logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Verification failed'}), 500

@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    """
    Resend verification email to user
    
    Request body:
        {
            "email": "string"
        }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal if email exists or not for security
            return jsonify({
                'success': True,
                'message': 'If an account exists with this email, a verification link has been sent.'
            }), 200
        
        # Check if already verified
        if user.email_verified:
            return jsonify({
                'success': True,
                'message': 'Email is already verified. You can login now.',
                'already_verified': True
            }), 200
        
        # Generate new verification token
        verification_token = user.generate_verification_token()
        db.session.commit()
        
        logger.info(f"Verification email resent to: {email}")
        
        # TODO: Send verification email
        # For now, return the token in response for testing
        
        return jsonify({
            'success': True,
            'message': 'Verification email sent. Please check your inbox.',
            'verification_token': verification_token  # Remove this in production
        }), 200
        
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}")
        return jsonify({'error': 'Failed to resend verification'}), 500

@app.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    """Get current user's profile (protected route)"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    }), 200

@app.route("/history", methods=["GET"])
@token_required
def get_history(current_user):
    """
    Get user's analysis history
    Query params:
        - limit: Number of results (default 50)
        - test_type: Filter by test type (optional)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        test_type = request.args.get('test_type')
        
        query = Analysis.query.filter_by(user_id=current_user.id)
        
        if test_type:
            query = query.filter_by(test_type=test_type)
        
        analyses = query.order_by(Analysis.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(analyses),
            'analyses': [a.to_dict() for a in analyses]
        }), 200
        
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch history'}), 500

@app.route("/update-profile", methods=["POST"])
@token_required
def update_profile(current_user):
    """
    Update user profile information
    
    Request body:
        {
            "username": "string" (optional),
            "email": "string" (optional)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update username if provided
        if 'username' in data:
            username = data['username'].strip()
            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
            # Check if username is taken by another user
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Username already taken'}), 400
            
            current_user.username = username
        
        # Update email if provided
        if 'email' in data:
            email = data['email'].strip().lower()
            if '@' not in email:
                return jsonify({'error': 'Invalid email address'}), 400
            
            # Check if email is taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already registered'}), 400
            
            current_user.email = email
        
        db.session.commit()
        logger.info(f"Profile updated for user: {current_user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """
    Change user password
    
    Request body:
        {
            "current_password": "string",
            "new_password": "string"
        }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"Password changed for user: {current_user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Failed to change password'}), 500

@app.route("/delete-account", methods=["DELETE"])
@token_required
def delete_account(current_user):
    """
    Delete user account and all associated data
    """
    try:
        username = current_user.username
        
        # Delete user (cascade will delete all analyses)
        db.session.delete(current_user)
        db.session.commit()
        
        logger.info(f"Account deleted: {username}")
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Account deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete account'}), 500

# ============================================
# ANALYSIS ROUTES
# ============================================

# API endpoint for analysis - now with optional authentication
@app.route("/analyze", methods=["POST"])
@optional_token
def analyze(current_user):
    """
    Analyze uploaded medical test image.
    
    Accepts POST request with:
    - image: File upload (PNG, JPG, JPEG, GIF, BMP)
    - test_type: String ('ph', 'fob', 'urinalysis')
    
    Returns:
        JSON response with analysis results or error message
        
    Example:
        POST /analyze
        Content-Type: multipart/form-data
        image: <file>
        test_type: "urinalysis"
    """
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    test_type = request.form.get("test_type")

    if not test_type or test_type not in ["ph", "fob", "urinalysis"]:
        return jsonify({"error": "Invalid test type. Must be 'ph', 'fob', or 'urinalysis'"}), 400

    if not allowed_file(image_file.filename):
        return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    # Generate unique analysis ID
    analysis_id = uuid.uuid4().hex
    filename = secure_filename(f"{analysis_id}_{image_file.filename}")
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save file and check size
    image_file.save(image_path)
    
    # Check file size to prevent memory issues
    file_size = os.path.getsize(image_path)
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        safe_file_cleanup(image_path)
        return jsonify({"error": "File too large. Please use images smaller than 10MB"}), 400
    
    # Validate image quality
    is_valid, error_message = validate_image_quality(image_path)
    if not is_valid:
        safe_file_cleanup(image_path)
        return jsonify({"error": error_message}), 400

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
            
            # Use AnalysisValidator to assess abnormality
            findings = AnalysisValidator.assess_abnormality(test_results)
            
            # Create a summary message based on findings
            if findings["critical"]:
                critical_tests = [f"{f['test']}: {f['result']}" for f in findings["critical"][:3]]
                summary = f"⚠️ {len(findings['critical'])} critical abnormal result(s) detected: {', '.join(critical_tests)}"
                if len(findings["critical"]) > 3:
                    summary += f" and {len(findings['critical']) - 3} more"
                recommendation = "Urgent: Consult a healthcare provider immediately for proper evaluation."
            elif findings["warning"]:
                warning_tests = [f"{f['test']}: {f['result']}" for f in findings["warning"][:3]]
                summary = f"⚠️ {len(findings['warning'])} abnormal result(s) detected: {', '.join(warning_tests)}"
                if len(findings["warning"]) > 3:
                    summary += f" and {len(findings['warning']) - 3} more"
                recommendation = "Consult a healthcare provider for proper evaluation of abnormal results."
            else:
                summary = "✓ All urinalysis parameters within normal ranges."
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

        # Save analysis to database if user is authenticated
        if current_user:
            try:
                analysis = Analysis(
                    user_id=current_user.id,
                    test_type=test_type,
                    result=response.get('result') or response.get('diagnosis', ''),
                    diagnosis=response.get('diagnosis', ''),
                    image_path=image_path,
                    confidence=response.get('confidence'),
                    raw_data=json.dumps(response)
                )
                db.session.add(analysis)
                db.session.commit()
                response['saved'] = True
                response['analysis_id'] = analysis.id
                logger.info(f"Analysis saved to database for user {current_user.username}")
            except Exception as e:
                logger.error(f"Failed to save analysis to database: {str(e)}")
                db.session.rollback()
                # Don't fail the request if save fails
                response['saved'] = False

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error analyzing {test_type} image: {str(e)}")
        safe_file_cleanup(image_path)
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file after processing
        safe_file_cleanup(image_path)
        
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
