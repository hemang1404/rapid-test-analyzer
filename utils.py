"""
Utility functions for Rapid Test Analyzer
Includes validation, error handling, and helper functions
"""
import cv2
import numpy as np
import os
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageValidationError(Exception):
    """Custom exception for image validation errors"""
    pass

def validate_image_quality(image_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate image quality for medical test analysis.
    
    Checks for:
    - Valid image file
    - Appropriate brightness levels
    - Minimum resolution
    - Valid color channels
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if image passes all checks
        - error_message: None if valid, error description if invalid
        
    Example:
        >>> is_valid, error = validate_image_quality("test.jpg")
        >>> if not is_valid:
        ...     print(f"Validation failed: {error}")
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return False, "Image file not found"
        
        # Try to read the image
        img = cv2.imread(image_path)
        if img is None:
            return False, "Invalid image file format. Please upload a valid image (PNG, JPG, JPEG)"
        
        # Check image dimensions
        height, width = img.shape[:2]
        if height < 100 or width < 100:
            return False, f"Image too small ({width}x{height}). Minimum size is 100x100 pixels"
        
        # Check if image is too large (memory concerns)
        if height > 5000 or width > 5000:
            return False, f"Image too large ({width}x{height}). Maximum size is 5000x5000 pixels"
        
        # Check brightness levels
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
            
        avg_brightness = np.mean(gray)
        
        if avg_brightness < 20:
            return False, "Image is too dark. Please use better lighting or adjust camera settings"
        
        if avg_brightness > 235:
            return False, "Image is too bright (overexposed). Please reduce lighting or adjust camera settings"
        
        # Check for completely uniform images (likely corrupted)
        std_dev = np.std(gray)
        if std_dev < 5:
            return False, "Image appears to be blank or corrupted. Please upload a clear photo of the test strip"
        
        logger.info(f"Image validation passed: {width}x{height}, brightness={avg_brightness:.1f}, std={std_dev:.1f}")
        return True, None
        
    except Exception as e:
        logger.error(f"Error during image validation: {str(e)}")
        return False, f"Error validating image: {str(e)}"

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file has an allowed extension.
    
    Args:
        filename: Name of the file to check
        allowed_extensions: Set of allowed extensions (e.g., {'png', 'jpg'})
        
    Returns:
        True if extension is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def safe_file_cleanup(file_path: str) -> bool:
    """
    Safely remove a file if it exists.
    
    Args:
        file_path: Path to the file to remove
        
    Returns:
        True if file was removed or didn't exist, False if error occurred
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {str(e)}")
        return False

def get_image_orientation(image_path: str) -> Optional[str]:
    """
    Detect image orientation (portrait/landscape).
    
    Args:
        image_path: Path to the image
        
    Returns:
        'portrait', 'landscape', or None if error
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        height, width = img.shape[:2]
        return 'portrait' if height > width else 'landscape'
    except Exception as e:
        logger.error(f"Error detecting orientation: {str(e)}")
        return None

class AnalysisValidator:
    """Validator for test analysis results"""
    
    # Define normal ranges for different tests
    NORMAL_RANGES = {
        "BLO": {"normal": ["Neg"], "severity": "high"},
        "GLU": {"normal": ["NEG"], "severity": "medium"},
        "PRO": {"normal": ["NEG"], "severity": "medium"},
        "KET": {"normal": ["NEG"], "severity": "low"},
        "NIT": {"normal": ["NEG"], "severity": "high"},
        "LEU": {"normal": ["NEG"], "severity": "medium"},
        "BIL": {"normal": ["Neg"], "severity": "medium"},
        "URO": {"normal": ["Neg", "Trace"], "severity": "low"},
    }
    
    @classmethod
    def assess_abnormality(cls, test_results: dict) -> dict:
        """
        Assess abnormality of test results and categorize by severity.
        
        Args:
            test_results: Dictionary of test results
            
        Returns:
            Dictionary with categorized findings:
            - critical: List of critical abnormal results
            - warning: List of concerning results
            - normal: List of normal results
        """
        findings = {
            "critical": [],
            "warning": [],
            "normal": []
        }
        
        for test_code, test_data in test_results.items():
            result_value = test_data.get("result", "N/A")
            test_name = test_data.get("test_name") or test_data.get("name", test_code)
            
            # Check if test is in our normal ranges
            if test_code in cls.NORMAL_RANGES:
                normal_values = cls.NORMAL_RANGES[test_code]["normal"]
                severity = cls.NORMAL_RANGES[test_code]["severity"]
                
                if result_value not in normal_values:
                    finding = {
                        "test": test_name,
                        "result": result_value,
                        "severity": severity
                    }
                    
                    if severity == "high":
                        findings["critical"].append(finding)
                    else:
                        findings["warning"].append(finding)
                else:
                    findings["normal"].append({
                        "test": test_name,
                        "result": result_value
                    })
            else:
                # Unknown test, add to normal by default
                findings["normal"].append({
                    "test": test_name,
                    "result": result_value
                })
        
        return findings
