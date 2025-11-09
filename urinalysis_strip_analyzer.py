import cv2
import numpy as np
import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Reference HSV data for urinalysis tests
urinalysis_refs = {
    "BLO": {
        "non_hemo": {
            "values": ["Neg", "10", "50", "250"],
            "hsv": [
                [29.98, 221.79, 198.65],
                [32.32, 116.72, 194.28],
                [97.24, 69.3, 174.8],
                [94.28, 123.72, 122.77],
            ]
        },
        "hemo": {
            "values": ["Neg", "10", "50", "250"],
            "hsv": [
                [29.98, 221.79, 198.65],
                [39.4, 172.5, 176.32],
                [61.71, 123.13, 150.5],
                [93.62, 133.39, 116.4],
            ]
        }
    },
    "BIL": {
        "values": ["Neg", "0.5", "1.0", "3.0"],
        "hsv": [
            [71.99, 32.67, 209.32],
            [96.4, 16.28, 193.5],
            [151.0, 32.51, 178.4],
            [171.12, 39.22, 168.77],
        ]
    },
    "URO": {
        "values": ["Neg", "Trace", "1", "4", "8", "12"],
        "hsv": [
            [90.56, 32.66, 210.56],
            [67.49, 29.15, 201.78],
            [120.18, 13.6, 185.85],
            [154.69, 35.66, 175.17],
            [166.11, 78.55, 163.42],
            [173.23, 91.97, 158.96],
        ]
    },
    "KET": {
        "values": ["NEG", "5", "10", "50", "100"],
        "hsv": [
            [68.99, 35.78, 207.37],
            [119.5, 13.77, 186.56],
            [159.36, 43.03, 171.8],
            [168.76, 102.51, 169.7],
            [153.0, 105.29, 137.21],
        ]
    },
    "PRO": {
        "values": ["NEG", "10", "30", "100", "300", "1000"],
        "hsv": [
            [33.84, 174.88, 194.46],
            [35.99, 138.02, 179.72],
            [40.34, 170.3, 169.72],
            [43.38, 143.9, 154.91],
            [89.98, 171.68, 135.3],
            [89.59, 199.47, 114.14],
        ]
    },
    "NIT": {
        "values": ["NEG", ">0.5", ">0.5"],
        "hsv": [
            [70.49, 36.69, 201.32],
            [157.0, 43.45, 169.05],
            [147.86, 99.51, 153.27],
        ]
    },
    "GLU": {
        "values": ["NEG", "100", "250", "500", "1000", "2000"],
        "hsv": [
            [96.74, 164.84, 194.89],
            [69.74, 119.55, 150.15],
            [43.05, 224.23, 126.04],
            [22.86, 179.28, 80.42],
            [5.92, 116.26, 73.92],
            [7.44, 84.42, 56.68],
        ]
    },
    "pH": {
        "values": ["5.0", "6.0", "6.5", "7.0", "7.5", "8.0", "9.0"],
        "hsv": [
            [14.92, 196.22, 163.75],
            [20.4, 217.47, 168.39],
            [25.96, 225.64, 136.65],
            [35.21, 232.62, 135.89],
            [42.07, 201.65, 122.86],
            [100.29, 200.16, 85.44],
            [104.61, 216.98, 113.93],
        ]
    },
    "S.G": {
        "values": ["1.000", "1.005", "1.010", "1.015", "1.020", "1.025", "1.030"],
        "hsv": [
            [103.71, 201.2, 52.66],
            [59.95, 126.82, 92.52],
            [46.52, 208.06, 112.98],
            [31.43, 220.13, 101.06],
            [31.48, 201.48, 124.75],
            [30.83, 213.42, 135.62],
            [28.3, 209.7, 135.78],
        ]
    },
    "LEU": {
        "values": ["NEG", "25", "75", "500"],
        "hsv": [
            [75.24, 38.12, 187.64],
            [103.82, 34.42, 182.48],
            [121.88, 29.92, 154.68],
            [126.17, 64.75, 133.02],
        ]
    },
}


class UrinalysisAnalyzer:
    """Production-ready urinalysis strip analyzer using KNN"""
    
    def __init__(self, k: int = 3):
        self.reference_data = self._prepare_reference_data()
        self.test_order = ["BLO", "BIL", "URO", "KET", "PRO", "NIT", "GLU", "pH", "S.G", "LEU"]
        self.test_names = {
            'BLO': 'Blood', 'BIL': 'Bilirubin', 'URO': 'Urobilinogen',
            'KET': 'Ketones', 'PRO': 'Protein', 'NIT': 'Nitrites',
            'GLU': 'Glucose', 'pH': 'pH', 'S.G': 'Specific Gravity', 'LEU': 'Leukocytes'
        }
        self.k = k
    
    def _prepare_reference_data(self) -> Dict:
        """Prepare reference data structure"""
        prepared_data = {}
        
        for test_code, data in urinalysis_refs.items():
            if test_code == 'BLO':
                prepared_data[test_code] = {
                    'non_hemo': data['non_hemo'],
                    'hemo': data['hemo']
                }
            else:
                prepared_data[test_code] = {
                    'values': data['values'],
                    'hsv': data['hsv']
                }
        
        return prepared_data
    
    def calculate_hsv_distance(self, hsv1: List[float], hsv2: List[float]) -> float:
        """Calculate weighted Euclidean distance between two HSV colors"""
        h1, s1, v1 = hsv1
        h2, s2, v2 = hsv2
        
        # Handle hue wraparound (circular distance)
        hue_diff = min(abs(h1 - h2), 180 - abs(h1 - h2))
        
        # Weighted distance calculation
        distance = np.sqrt(
            (hue_diff * 2.0) ** 2 +
            (abs(s1 - s2) * 1.0) ** 2 +
            (abs(v1 - v2) * 0.5) ** 2
        )
        
        return distance
    
    def find_best_match_knn(self, test_hsv: List[int], test_code: str) -> Tuple[str, float, str]:
        """KNN-based matching with voting"""
        if test_code not in self.reference_data:
            return "Unknown", 0.0, "Test code not found in reference data."
        
        ref_data = self.reference_data[test_code]
        blood_type = None
        
        # Special handling for Blood test
        if test_code == 'BLO':
            hue = test_hsv[0]
            
            if hue < 60:
                ref_group = ref_data['hemo']
                blood_type = "Hemo"
            else:
                ref_group = ref_data['non_hemo']
                blood_type = "Non-Hemo"
            
            distances_and_results = []
            for i, ref_hsv in enumerate(ref_group['hsv']):
                distance = self.calculate_hsv_distance(test_hsv, ref_hsv)
                result_value = ref_group['values'][i] if i < len(ref_group['values']) else "Unknown"
                distances_and_results.append((distance, result_value))
        else:
            # Regular test processing
            distances_and_results = []
            for i, ref_hsv in enumerate(ref_data['hsv']):
                distance = self.calculate_hsv_distance(test_hsv, ref_hsv)
                result_value = ref_data['values'][i] if i < len(ref_data['values']) else "Unknown"
                distances_and_results.append((distance, result_value))
        
        # Sort by distance and get K nearest neighbors
        distances_and_results.sort(key=lambda x: x[0])
        k_actual = min(self.k, len(distances_and_results))
        nearest_neighbors = distances_and_results[:k_actual]
        
        # Voting
        neighbor_votes = [result for _, result in nearest_neighbors]
        vote_counts = Counter(neighbor_votes)
        
        if vote_counts:
            best_result = vote_counts.most_common(1)[0][0]
            vote_strength = vote_counts.most_common(1)[0][1] / k_actual
            
            # Calculate confidence
            avg_distance = np.mean([dist for dist, _ in nearest_neighbors])
            consensus_bonus = vote_strength * 20
            distance_confidence = max(0, 100 - (avg_distance / 150.0 * 100))
            final_confidence = min(100, distance_confidence + consensus_bonus)
            
            # Build explanation
            explanation_parts = []
            
            if test_code == 'BLO':
                explanation_parts.append(f"Classified as {blood_type} (Hue={test_hsv[0]:.1f})")
            
            # List the K nearest neighbors
            neighbor_list = ", ".join([f"{val}({dist:.1f})" for dist, val in nearest_neighbors])
            explanation_parts.append(f"K={k_actual} nearest: {neighbor_list}")
            
            # Voting result
            winner_votes = vote_counts.most_common(1)[0][1]
            if winner_votes == k_actual:
                explanation_parts.append(f"Unanimous vote for '{best_result}'")
            else:
                explanation_parts.append(f"Won by {winner_votes}/{k_actual} votes")
            
            explanation = " | ".join(explanation_parts)
            
            # Add blood type indicator to result if BLO test
            if test_code == 'BLO':
                best_result = f"{best_result} ({blood_type})"
            
            return best_result, round(final_confidence, 1), explanation
        else:
            return "Unknown", 0.0, "No valid neighbors found."
    
    def analyze_pads(self, pad_hsv_dict: Dict[str, List[int]]) -> Dict[str, Dict]:
        """Analyze pads with KNN"""
        results = {}
        pad_keys = sorted(pad_hsv_dict.keys(), key=lambda x: int(x.split('_')[1]))
        
        for i, pad_key in enumerate(pad_keys):
            if i >= len(self.test_order):
                break
            
            test_code = self.test_order[i]
            test_hsv = pad_hsv_dict[pad_key]
            
            result, confidence, explanation = self.find_best_match_knn(test_hsv, test_code)
            
            results[test_code] = {
                'test_name': self.test_names.get(test_code, test_code),
                'result': result,
                'confidence': confidence,
                'hsv': test_hsv,
                'explanation': explanation
            }
        
        return results


def detect_pads(image_path, center_window=10, swatch_margin=100, expected_pads=10):
    """
    Detect individual urinalysis test pads, extract HSV values from centers,
    correct slight tilt automatically, fill in missing pads if some are missed,
    and visualize with colored swatches.
    """
    # --- Step 1: Load image ---
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # --- Step 2: Auto-rotate using bounding rectangle angle ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours_edge, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_rotated = img
    rotation_angle = 0
    if contours_edge:
        c = max(contours_edge, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        angle = rect[-1]
        if angle < -45:
            angle = 90 + angle
        rotation_angle = angle

        (h, w) = img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        img_rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    print(f"🌀 Auto-rotation correction: {rotation_angle:.2f}°")

    # --- Step 3: Resize for consistency ---
    target_width = 800
    img_resized = cv2.resize(img_rotated, (target_width, int(img_rotated.shape[0] * target_width / img_rotated.shape[1])))

    hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)

    # --- Step 4: Mask for non-white (remove background) ---
    lower = np.array([0, 20, 15])
    upper = np.array([188, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)

    # Reduced morphology → prevent connecting patches
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # --- Step 5: Find contours (candidate pads) ---
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pads = []
    img_center_x = img_resized.shape[1] // 2

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 and h > 20:
            pad_center_x = x + w // 2
            if 100 < pad_center_x < img_resized.shape[1] - 100:
                pads.append((x, y, w, h))

    # --- Step 6: Sort top to bottom ---
    pads = sorted(pads, key=lambda b: b[1])

    # --- Step 7: IMPROVED missing pad correction ---
    num_detected = len(pads)
    if len(pads) >= 2 and len(pads) < expected_pads:
        centers_y = [y + h // 2 for (x, y, w, h) in pads]
        y_top, y_bottom = centers_y[0], centers_y[-1]
        interval = (y_bottom - y_top) / (expected_pads - 1)
        
        # ✅ Calculate average dimensions for synthesized pads
        avg_x = int(np.mean([x for x, _, _, _ in pads]))
        avg_w = int(np.mean([w for _, _, w, _ in pads]))
        avg_h = int(np.mean([h for _, _, _, h in pads]))
        
        # ✅ Track which detected pads have been used
        used_pad_indices = set()
        filled_pads = []
        
        for i in range(expected_pads):
            expected_y = int(y_top + i * interval)
            
            # Find nearest detected pad that hasn't been used yet
            distances = []
            for idx, cy in enumerate(centers_y):
                if idx not in used_pad_indices:
                    distances.append((abs(cy - expected_y), idx))
            
            if distances:
                min_distance, nearest_idx = min(distances, key=lambda x: x[0])
                nearest_y = centers_y[nearest_idx]
                
                # If close enough, use the detected pad
                if min_distance < interval * 0.4:
                    filled_pads.append(pads[nearest_idx])
                    used_pad_indices.add(nearest_idx)  # ✅ Mark as used
                else:
                    # Synthesize missing pad using average dimensions
                    filled_pads.append((avg_x, expected_y - avg_h//2, avg_w, avg_h))
            else:
                # All detected pads used, synthesize remaining
                filled_pads.append((avg_x, expected_y - avg_h//2, avg_w, avg_h))

        missing_count = expected_pads - num_detected
        print(f"⚙️ Reconstructed {missing_count} missing pad{'s' if missing_count > 1 else ''} (total now = {expected_pads})")
        pads = filled_pads

    # --- Step 8: Visualization canvas ---
    height, width = img_resized.shape[:2]
    debug_img = np.zeros((height, width + swatch_margin, 3), dtype=np.uint8)
    debug_img[:height, :width] = img_resized

    # --- Step 9: Extract HSV values ---
    pad_hsv_dict = {}

    for i, (x, y, w, h) in enumerate(pads):
        x_center = x + w // 2
        y_center = y + h // 2

        half_win = center_window // 2
        y0 = max(0, y_center - half_win)
        y1 = min(hsv.shape[0], y_center + half_win + 1)
        x0 = max(0, x_center - half_win)
        x1 = min(hsv.shape[1], x_center + half_win + 1)

        hsv_patch = hsv[y0:y1, x0:x1]
        hsv_avg = hsv_patch.mean(axis=(0, 1)).astype(int).tolist()
        pad_hsv_dict[f"Pad_{i+1}"] = hsv_avg

        # --- Draw visuals ---
        # ✅ Better color coding: green = detected, blue = synthesized
        is_detected = i < num_detected or (i in range(len(pads)) and pads[i] in pads[:num_detected])
        color = (0, 255, 0) if is_detected else (255, 0, 0)
        
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), color, 2)
        cv2.circle(debug_img, (x_center, y_center), 8, (0, 0, 255), -1)
        cv2.putText(debug_img, str(i+1), (x-20, y+h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        swatch_size = 30
        hsv_bgr = cv2.cvtColor(np.uint8([[hsv_avg]]), cv2.COLOR_HSV2BGR)[0][0].tolist()
        cv2.rectangle(debug_img,
                      (width + 10, y_center - swatch_size//2),
                      (width + 10 + swatch_size, y_center + swatch_size//2),
                      hsv_bgr, -1)
        hsv_text = f"H:{hsv_avg[0]} S:{hsv_avg[1]} V:{hsv_avg[2]}"
        cv2.putText(debug_img, hsv_text, (width + 45, y_center + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    # --- Step 10: Scale debug image for display ---
    display_height = 800
    if debug_img.shape[0] > display_height:
        scale = display_height / debug_img.shape[0]
        display_img = cv2.resize(debug_img, (int(debug_img.shape[1]*scale), display_height))
        mask_display = cv2.resize(mask, (int(mask.shape[1]*scale), display_height))
    else:
        display_img = debug_img
        mask_display = mask

    if len(pads) < 2:
        raise ValueError(f"Only {len(pads)} pads detected. Need at least 2. Check image quality.")

    # Validate HSV values
    for pad_name, hsv_vals in pad_hsv_dict.items():
        if hsv_vals[2] < 30:  # Very dark
            print(f"⚠️ WARNING: {pad_name} is very dark (V={hsv_vals[2]}). Poor lighting?")
        if hsv_vals[1] < 10 and hsv_vals[2] > 200:  # Nearly white
            print(f"⚠️ WARNING: {pad_name} appears to be background (S={hsv_vals[1]}, V={hsv_vals[2]})")

    return pads, pad_hsv_dict, display_img, mask_display


def create_results_visualization(debug_img: np.ndarray, results: Dict) -> np.ndarray:
    """Create visualization with results overlay"""
    height, width = debug_img.shape[:2]
    results_width = 300
    final_img = np.zeros((height, width + results_width, 3), dtype=np.uint8)
    final_img[:height, :width] = debug_img
    
    # Add results background
    final_img[:, width:] = (50, 50, 50)
    
    # Add title
    cv2.putText(final_img, "TEST RESULTS", (width + 50, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Add results
    y_pos = 90
    line_height = 45
    
    test_order = ["BLO", "BIL", "URO", "KET", "PRO", "NIT", "GLU", "pH", "S.G", "LEU"]
    
    for test_code in test_order:
        if test_code in results:
            data = results[test_code]
            
            # Test name
            cv2.putText(final_img, f"{data['test_name']}:", (width + 20, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
            
            # Result
            cv2.putText(final_img, f"{data['result']}", (width + 20, y_pos + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Confidence
            cv2.putText(final_img, f"{data['confidence']:.0f}%", (width + 200, y_pos + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
            
            y_pos += line_height
    
    return final_img


def analyze_urinalysis(image_path: str, debug: bool = False, result_folder: str = "result_images", 
                       analysis_id: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
    """
    Analyze urinalysis strip image - Flask app compatible
    
    Args:
        image_path: Path to the strip image
        debug: Enable debug mode (console output only)
        result_folder: Folder to save result images
        analysis_id: Unique ID for this analysis
        k: K value for KNN
        
    Returns:
        Dictionary with analysis results compatible with Flask app
    """
    try:
        logger.info(f"Starting urinalysis analysis: {image_path}")
        
        # Detect pads and extract HSV
        pads, hsv_dict, debug_img, mask_img = detect_pads(
            image_path,
            center_window=10,
            swatch_margin=150,
            expected_pads=10
        )
        
        logger.info(f"Detected {len(pads)} pads")
        
        # Analyze with KNN
        analyzer = UrinalysisAnalyzer(k=k)
        results = analyzer.analyze_pads(hsv_dict)
        
        # Log results
        if debug:
            logger.info("="*60)
            logger.info("ANALYSIS RESULTS")
            logger.info("="*60)
            for test_code in analyzer.test_order:
                if test_code in results:
                    data = results[test_code]
                    conf_icon = "✅" if data['confidence'] >= 70 else "⚠️" if data['confidence'] >= 50 else "❌"
                    logger.info(f"{data['test_name']}: {data['result']} | {data['confidence']:.1f}% {conf_icon}")
        
        # Create visualization
        final_visualization = create_results_visualization(debug_img, results)
        
        # Save result images
        result_images = []
        if result_folder:
            os.makedirs(result_folder, exist_ok=True)
            
            if analysis_id:
                filename = f"{analysis_id}_urinalysis_result.jpg"
            else:
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                filename = f"{base_name}_urinalysis_result.jpg"
            
            output_path = os.path.join(result_folder, filename)
            cv2.imwrite(output_path, final_visualization)
            result_images.append(output_path)
            logger.info(f"Result saved to: {output_path}")
        
        # Format results for Flask response
        test_results = {}
        for test_code, data in results.items():
            test_results[test_code] = {
                'test_name': data['test_name'],  # Changed from 'name' to 'test_name' for consistency
                'result': data['result'],
                'confidence': data['confidence'] / 100.0,  # Convert to 0-1 range for frontend
                'explanation': data['explanation']
            }
        
        return {
            "success": True,
            "status": "ok",
            "type": "urinalysis",
            "results": test_results,
            "pads_detected": len(pads),
            "result_images": result_images,
            "message": "Urinalysis strip analyzed successfully"
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "message": "Image file not found"
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "message": "Pad detection failed"
        }
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "message": "Analysis failed"
        }


if __name__ == "__main__":
    # Example usage for testing
    image_path = r"C:\coding\images\uri test 5.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
    else:
        result = analyze_urinalysis(image_path, debug=True, result_folder="result_images")
        
        if result["success"]:
            print("\n" + "="*80)
            print("📊 URINALYSIS RESULTS")
            print("="*80)
            for test_code, data in result["results"].items():
                conf_icon = "✅" if data['confidence'] >= 70 else "⚠️" if data['confidence'] >= 50 else "❌"
                print(f"\n{data['name']} ({test_code}):")
                print(f"  Result: {data['result']} | Confidence: {data['confidence']:.1f}% {conf_icon}")
                print(f"  How: {data['explanation']}")
            print(f"\n✅ Analysis complete! Result saved to: {result['result_images'][0]}")
        else:
            print(f"❌ Analysis failed: {result['error']}")