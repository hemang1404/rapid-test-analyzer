import cv2
import numpy as np
import os
import logging
from typing import Dict, List, Tuple, Optional, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def _show(win: str, img, max_dim: int = 900, debug: bool = False):
    """Show window only if debug is True, scaled to fit."""
    if not debug or img is None:
        return
    h, w = img.shape[:2]
    scale = min(max_dim / max(h, 1), max_dim / max(w, 1), 1.0)
    if scale < 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    cv2.imshow(win, img)
    cv2.waitKey(0)  # Wait indefinitely until a key is pressed

def load_templates(template_dir: str = "templates") -> Dict[str, np.ndarray]:
    templates = {}
    if not os.path.isdir(template_dir):
        logging.warning(f"Template directory not found: {template_dir}. Using fallback method.")
        return templates  # Return empty dict instead of raising error
    
    for fname in os.listdir(template_dir):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(template_dir, fname)
            img = cv2.imread(path)
            if img is not None:
                key = os.path.splitext(fname)[0]
                templates[key] = img
    
    if not templates:
        logging.warning(f"No templates found in: {template_dir}. Using fallback method.")
    
    return templates

def sobel_crop(image: np.ndarray, debug: bool = False) -> Tuple[Optional[np.ndarray], Optional[Tuple[int,int,int,int]]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
    sobel_edges = cv2.addWeighted(cv2.convertScaleAbs(grad_x), 0.5,
                                  cv2.convertScaleAbs(grad_y), 0.5, 0)
    _show("Sobel Edges", sobel_edges, debug=debug)
    _, edges = cv2.threshold(sobel_edges, 18, 255, cv2.THRESH_BINARY)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=6)
    _show("Binary Edges", edges, debug=debug)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best_bbox, max_area = None, 0
    img_area = image.shape[0] * image.shape[1]
    for c in contours:
        area = cv2.contourArea(c)
        if not (img_area * 0.05 < area < img_area * 0.9):
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        if 3 <= len(approx) <= 6:
            x, y, w, h = cv2.boundingRect(approx)
            if h == 0 or w == 0:
                continue
            ar = w / float(h)
            if 0.10 < ar < 0.80 and w * h > max_area:
                max_area = w * h
                best_bbox = (x, y, w, h)
    if best_bbox:
        x, y, w, h = best_bbox
        cropped = image[y:y + h, x:x + w]
        _show("Cropped Strip", cropped, debug=debug)
        return cropped, best_bbox
    return None, None

def edge_preprocess(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    edges = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 5
    )
    edges = cv2.GaussianBlur(edges, (3, 3), 0)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    return edges

def multi_scale_match(
    image: np.ndarray,
    template_edges: np.ndarray,
    scales: np.ndarray = np.linspace(0.5, 1.5, 15),
    method: int = cv2.TM_CCORR_NORMED
) -> Tuple[float, Optional[np.ndarray], Optional[Tuple[int,int,int,int]], Optional[Tuple[int,int]]]:
    img_edges = edge_preprocess(image)
    best_score = -1.0
    best_loc = None
    best_size = None
    t_h_orig, t_w_orig = template_edges.shape[:2]
    for scale in scales:
        new_w, new_h = int(t_w_orig * scale), int(t_h_orig * scale)
        if new_w < 10 or new_h < 10:
            continue
        resized_template = cv2.resize(template_edges, (new_w, new_h))
        kernel = np.ones((3, 3), np.uint8)
        resized_template = cv2.morphologyEx(resized_template, cv2.MORPH_CLOSE, kernel)
        if img_edges.shape[0] < new_h or img_edges.shape[1] < new_w:
            continue
        result = cv2.matchTemplate(img_edges, resized_template, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > best_score:
            best_score = max_val
            best_loc = max_loc
            best_size = (new_w, new_h)
    roi, roi_box = None, None
    if best_score >= 0 and best_loc is not None and best_size is not None:
        x, y = best_loc
        roi = image[y:y + best_size[1], x:x + best_size[0]]
        roi_box = (x, y, best_size[0], best_size[1])
    return best_score, roi, roi_box, best_loc

def match_with_templates_dict(
    image: np.ndarray,
    templates: Dict[str, np.ndarray],
    threshold: float = 0.6
) -> Tuple[Optional[np.ndarray], Optional[Tuple[int,int,int,int]], float, Optional[str], Optional[Tuple[int,int,int,int]]]:
    best_score = -1.0
    best_roi, best_box = None, None
    best_name = None
    for name, template_img in templates.items():
        template_edges = edge_preprocess(template_img)
        score, roi, roi_box, _ = multi_scale_match(image, template_edges)
        if score > best_score:
            best_score, best_roi, best_box, best_name = score, roi, roi_box, name
    if best_roi is not None and best_score >= threshold:
        return best_roi, best_box, best_score, best_name, best_box
    return None, None, best_score, None, None

def circle_based_roi(cropped_strip: np.ndarray, debug: bool = False) -> Tuple[Optional[np.ndarray], Optional[Tuple[int,int,int,int]]]:
    gray = cv2.cvtColor(cropped_strip, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    gray_eq = cv2.equalizeHist(blurred)
    h, w = gray.shape
    expected_r = int(0.10 * h)
    circles = cv2.HoughCircles(gray_eq, cv2.HOUGH_GRADIENT, dp=1,
                               minDist=int(expected_r * 1.5),
                               param1=80, param2=50,
                               minRadius=int(expected_r * 0.8),
                               maxRadius=int(expected_r * 1.2))
    debug_img = cropped_strip.copy()
    if circles is None:
        return None, None
    circles = np.round(circles[0, :]).astype("int")
    cx, cy, r = sorted(circles, key=lambda c: c[1], reverse=True)[0]
    cv2.circle(debug_img, (cx, cy), r, (0, 255, 0), 2)
    y_start = max(0, cy - int(r * 4.5))
    y_end = min(h, y_start + int(r * 2.7))
    x_start = max(0, cx - int(r * 0.65))
    x_end = min(w, cx + int(r * 0.65))
    roi = cropped_strip[y_start:y_end, x_start:x_end]
    cv2.rectangle(debug_img, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
    _show("Circle ROI Debug", debug_img, debug=debug)
    return roi, (x_start, y_start, x_end - x_start, y_end - y_start)

def detect_lines(roi: np.ndarray, min_vertical_gap: int = 20, debug: bool = False) -> List[Tuple[int,int,int,int]]:
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, np.array([0, 15, 80]), np.array([15, 255, 255]))
    mask2 = cv2.inRange(hsv, np.array([165, 15, 80]), np.array([179, 255, 255]))
    color_mask = cv2.bitwise_or(mask1, mask2)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 51, 21)
    combined = cv2.bitwise_and(color_mask, adapt)
    _show("Combined Mask", combined, debug=debug)
    dilated = cv2.dilate(combined, np.ones((3, 20), np.uint8), iterations=2)
    _show("Dilated Mask", dilated, debug=debug)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lines, roi_h = [], roi.shape[0]
    debug_img = roi.copy()
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if cv2.contourArea(c) > 100 and w > 20 and 5 <= h < 35 and w / h > 1:
            cy = y + h / 2
            if roi_h * 0.15 < cy < roi_h * 0.95:
                lines.append((x, y, w, h))
                cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    _show("Detected Lines", debug_img, debug=debug)
    lines.sort(key=lambda b: b[1])
    filtered = []
    for l in lines:
        if not filtered or abs(l[1] - filtered[-1][1]) > min_vertical_gap:
            filtered.append(l)
    return filtered

def classify_result(lines: List[Tuple[int,int,int,int]], roi_h: int) -> str:
    ctrl, test = False, False
    for x, y, w, h in lines:
        cy = y + h / 2
        if roi_h * 0.15 < cy < roi_h * 0.5:
            ctrl = True
        elif roi_h * 0.5 < cy < roi_h * 0.95:
            test = True
    if ctrl and test:
        return "positive"
    if ctrl and not test:
        return "negative"
    return "invalid"

def draw_roi_bbox_on_strip(strip: np.ndarray, roi_box: Tuple[int,int,int,int], template_name: Optional[str] = None) -> np.ndarray:
    x, y, w, h = roi_box
    vis = strip.copy()
    cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 2)
    label = "ROI"
    if template_name:
        label += f" ({template_name})"
    cv2.putText(vis, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    return vis

def analyze_fob(image_path: str, templates_dir: str = "templates", debug: bool = False, result_folder: str = "result_images", analysis_id: str = None) -> Dict[str, Any]:
    image = cv2.imread(image_path)
    if image is None:
        return {"status": "error", "message": f"Failed to load image: {image_path}"}
    
    # Try to load templates, but don't fail if they're missing
    templates = load_templates(templates_dir)
    
    cropped_strip, strip_box = sobel_crop(image, debug=debug)
    if cropped_strip is None:
        return {"status": "error", "message": "Could not crop strip"}
    
    roi, roi_box, score, best_template_name = None, None, 0.0, None
    method_used = "circle"  # Default to circle method
    
    # Try template matching if templates are available
    if templates:
        roi, roi_box, score, best_template_name, _ = match_with_templates_dict(
            cropped_strip, templates, threshold=0.6
        )
        if roi is not None:
            method_used = "template"
    
    # Fallback to circle detection if template matching failed or no templates
    if roi is None:
        roi_cd, roi_cd_box = circle_based_roi(cropped_strip, debug=debug)
        if roi_cd is None:
            return {
                "status": "error",
                "message": "Both template matching and circle detection failed",
                "template_best_score": float(score)
            }
        roi, roi_box = roi_cd, roi_cd_box
        method_used = "circle"
    # Draw and show/save the ROI bounding box on the cropped strip
    vis_strip = cropped_strip.copy()
    roi_box_img = draw_roi_bbox_on_strip(
        vis_strip,
        roi_box if roi_box is not None else (0, 0, vis_strip.shape[1], vis_strip.shape[0]),
        best_template_name if method_used=="template" else None
    )
    _show("ROI Bounding Box (before cropping)", roi_box_img, debug=debug)

    # --- Add missing ROI crop, line detection, and result classification ---
    h_roi = roi.shape[0]
    y1 = int(h_roi * 0.20)
    y2 = int(h_roi * 0.85)
    roi_cropped = roi[y1:y2, :]
    lines = detect_lines(roi_cropped, debug=debug)
    result_text = classify_result(lines, roi_cropped.shape[0])

    # Draw bounding box around detected ROI and detected lines on cropped strip
    final_img = cropped_strip.copy()
    if roi_box is not None:
        x_roi, y_roi, w_roi, h_roi = roi_box
        # Draw actual ROI bounding box on cropped strip
        cv2.rectangle(final_img, (x_roi, y_roi), (x_roi + w_roi, y_roi + h_roi), (255, 0, 0), 2)
        cv2.putText(final_img, "ROI", (x_roi, max(0, y_roi - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        # Overlay detected lines at correct position inside ROI
        for line in lines:
            x, y, w, h = line
            # Lines are relative to cropped ROI, so offset by ROI position and y1 crop
            cv2.rectangle(final_img, (x_roi + x, y_roi + y + y1), (x_roi + x + w, y_roi + y + h + y1), (0, 255, 0), 2)

    _show("Cropped Strip with ROI and Detected Lines", final_img, debug=debug)

    # Save the final annotated image
    os.makedirs(result_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    if analysis_id:
        filename = f"{analysis_id}_fob_result.jpg"
    else:
        filename = f"{base_name}_fob_result.jpg"
    output_path = os.path.join(result_folder, filename)
    cv2.imwrite(output_path, final_img)

    # Now return the result dictionary
    return {
        "status": "ok",
        "result": result_text,
        "lines": [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in lines],
        "method": method_used,
        "template_best_score": float(score),
        "best_template": best_template_name,
        "result_images": [output_path]
    }

if __name__ == "__main__":
    # Example usage
    image_path = r"C:/coding/images/real test.jpeg"  # <-- Change this to your image path
    templates_dir = "templates"  # <-- Change if your templates are in a different folder
    debug = True  # Set to True to see debug images, False for silent run

    result = analyze_fob(image_path, templates_dir=templates_dir, debug=debug)
    print(result)


