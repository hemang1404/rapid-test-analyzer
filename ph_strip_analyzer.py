import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor  # Changed from NearestNeighbors
from typing import Optional, List, Dict, Any
import os

class PHStripAnalyzer:
    def __init__(self, fixed_ph_labels: Optional[List[float]] = None, debug: bool = False):
        self.knn_model = None
        self.knn_labels = []
        self.reference_segments_data = []
        self.debug_mode = debug
        self.fixed_ph_labels = fixed_ph_labels or [3.8, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0]

    # ---------------------- Debug Utility ----------------------
    def _show_debug(self, title, img, wait_ms=None):
        # Disabled debug image display
        pass

    # ---------------------- Test Patch Detection ----------------------
    def detect_test_patch_contour(self, image):
        debug_img = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.medianBlur(gray, 5)
        # Removed debug display
        # self._show_debug("Blurred Gray Image", blurred, wait_ms=None)

        circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
            param1=50, param2=30, minRadius=15, maxRadius=80
        )

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            x, y, r = circles[0]
            cv2.circle(debug_img, (x, y), r, (0,255,0), 2)
            # Removed debug display
            # self._show_debug("Test Patch - HoughCircles", debug_img, wait_ms=None)
            return {
                'contour': None,
                'center': (x, y),
                'radius': r,
                'bbox': (x - r, y - r, 2*r, 2*r),
                'area': np.pi * r * r,
                'circularity': 1.0
            }

        # Fallback contour method
        thresh_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY_INV, 11, 2)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_color_bound = np.array([0, 25, 25])
        upper_color_bound = np.array([150, 255, 255])
        mask_hsv = cv2.inRange(hsv, lower_color_bound, upper_color_bound)
        combined_thresh = cv2.bitwise_and(thresh_adaptive, mask_hsv)

        kernel_large = np.ones((10,10), np.uint8)
        kernel_small = np.ones((3,3), np.uint8)
        cleaned_thresh = cv2.morphologyEx(combined_thresh, cv2.MORPH_CLOSE, kernel_large)
        cleaned_thresh = cv2.morphologyEx(cleaned_thresh, cv2.MORPH_OPEN, kernel_small)
        cleaned_thresh = cv2.dilate(cleaned_thresh, kernel_small, iterations=1)
        # Removed debug display
        # self._show_debug("Test Patch - Thresholded Mask", cleaned_thresh, wait_ms=None)

        contours, _ = cv2.findContours(cleaned_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        test_patch_contour_info = None
        max_radius = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            (x_center, y_center), radius = cv2.minEnclosingCircle(contour)
            if 1500 < area < 50000 and circularity > 0.5:
                if radius > max_radius:
                    max_radius = radius
                    test_patch_contour_info = {
                        'contour': contour,
                        'center': (int(x_center), int(y_center)),
                        'radius': int(radius),
                        'bbox': cv2.boundingRect(contour),
                        'area': area,
                        'circularity': circularity
                    }

        if test_patch_contour_info and test_patch_contour_info['contour'] is not None:
            cv2.drawContours(debug_img, [test_patch_contour_info['contour']], -1, (0,255,0), 2)
            # Removed debug display
            # self._show_debug("Test Patch - Contour Fallback", debug_img, wait_ms=None)

        return test_patch_contour_info

    # ---------------------- Reference Patch Detection (HSV only) ----------------------
    def detect_reference_patches(self, image, test_patch_bbox=None):
        debug_img = image.copy()
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Broad HSV range to capture patches
        lower_color_hsv = np.array([0, 40, 40])
        upper_color_hsv = np.array([179, 255, 255])
        mask_colors = cv2.inRange(hsv, lower_color_hsv, upper_color_hsv)

        # Morphological cleaning
        kernel_open = np.ones((3,3), np.uint8)
        mask_cleaned = cv2.morphologyEx(mask_colors, cv2.MORPH_OPEN, kernel_open, iterations=1)
        kernel_close = np.ones((3,3), np.uint8)
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel_close, iterations=1)
        # Removed debug display
        # self._show_debug("Reference Patches - HSV Mask", mask_cleaned, wait_ms=None)

        contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        patches = []
        h_img = image.shape[0]

        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            if 500 < area < 15000 and 0.5 < (w/h if h else 0) < 2.0 and h_img*0.20 < y < h_img*0.80:
                if not test_patch_bbox or not self._bbox_overlap((x,y,w,h), test_patch_bbox):
                    patches.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': w/h if h else 0,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    })

        if len(patches) == 0:
            return []

        # ---- Cluster filtering ----
        ys = [p['center_y'] for p in patches]
        median_y = np.median(ys)
        patches = [p for p in patches if abs(p['center_y'] - median_y) < 0.25 * image.shape[0]]

        # Sort and trim to label count
        patches = sorted(patches, key=lambda p: p['center_x'])
        patches = patches[:len(self.fixed_ph_labels)]

        # Debug draw (but not displayed)
        for i, patch in enumerate(patches):
            x,y,w,h = patch['bbox']
            cv2.rectangle(debug_img, (x,y), (x+w,y+h), (255,0,0), 2)
            if i < len(self.fixed_ph_labels):
                cv2.putText(debug_img, str(self.fixed_ph_labels[i]), (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        # Removed debug display
        # self._show_debug("Reference Patches - Filtered Cluster", debug_img, wait_ms=None)
        return patches

    # ---------------------- Utilities ----------------------
    def _bbox_overlap(self, bbox1, bbox2, min_overlap_ratio=0.5):
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        inter_area = x_overlap * y_overlap
        if inter_area == 0:
            return False
        union_area = (w1*h1)+(w2*h2)-inter_area
        return (inter_area / union_area) > min_overlap_ratio

    def _extract_average_color_circle(self, segment_image, center, radius_ratio=0.4):
        if segment_image is None or segment_image.size == 0:
            return (0,0,0)
        h_img, w_img = segment_image.shape[:2]
        x_c, y_c = center
        radius = int(min(w_img, h_img) * radius_ratio)
        mask = np.zeros((h_img, w_img), dtype=np.uint8)
        cv2.circle(mask, (x_c, y_c), radius, 255, -1)
        hsv = cv2.cvtColor(segment_image, cv2.COLOR_BGR2HSV)
        masked_hsv = cv2.bitwise_and(hsv, hsv, mask=mask)
        pixels = masked_hsv[mask==255]
        if len(pixels) == 0:
            return (0,0,0)
        avg_hsv = np.mean(pixels, axis=0)
        return tuple(np.clip(avg_hsv, [0,0,0],[179,255,255]).astype(int))

    # ---------------------- NEW: Map continuous value to hardcoded list ----------------------
    def _map_to_hardcoded_ph(self, continuous_ph_value):
        """
        Map a continuous pH prediction to the closest value in the hardcoded list
        
        Args:
            continuous_ph_value: The continuous pH value from KNN regression
            
        Returns:
            The closest pH value from self.fixed_ph_labels
        """
        # Find the closest value in the hardcoded list
        distances = [abs(continuous_ph_value - ph) for ph in self.fixed_ph_labels]
        closest_index = distances.index(min(distances))
        return self.fixed_ph_labels[closest_index]

    # ---------------------- Visualization ----------------------
    def visualize_results(self, image, test_patch_info, reference_patches, estimated_ph_value):
        vis = image.copy()

        if test_patch_info.get('center') and test_patch_info.get('radius'):
            x, y, r = test_patch_info['center'][0], test_patch_info['center'][1], test_patch_info['radius']
            cv2.circle(vis, (x, y), r, (0, 255, 0), 2)
            cv2.putText(vis, f"Test", (x-20, y-r-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        else:
            x,y,w,h = test_patch_info['bbox']
            cv2.rectangle(vis, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(vis, f"Test", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        for i, patch in enumerate(reference_patches):
            x,y,w,h = patch['bbox']
            cv2.rectangle(vis, (x,y), (x+w,y+h), (255,0,0), 2)
            label = self.fixed_ph_labels[i] if i < len(self.fixed_ph_labels) else '?'
            cv2.putText(vis, str(label), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        cv2.putText(vis, f"Estimated pH: {estimated_ph_value:.1f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
        # Removed debug display - this is now only for final result
        # self._show_debug("Final Annotated Strip", vis, wait_ms=1000)
        return vis

    # ---------------------- Main Analysis ----------------------
    def analyze_ph_strip(self, image_path, debug=False, result_folder=None, analysis_id=None):
        """
        Analyze pH strip with Flask app compatibility
        
        Args:
            image_path: Path to the image file
            debug: Enable debug mode (now only affects console output)
            result_folder: Folder to save result images (for web app)
            analysis_id: Unique ID for this analysis (for web app)
            
        Returns:
            Dictionary with analysis results compatible with Flask app
        """
        # Debug mode now only affects console output, not image display
        self.debug_mode = False  # Force disable debug image display
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": f"Could not load image from {image_path}"
                }
            
            output_image = image.copy()

            # Step 1: Detect test patch
            test_patch_info = self.detect_test_patch_contour(image)
            if not test_patch_info:
                return {
                    "success": False,
                    "error": "Could not detect test patch in the image"
                }

            x, y, w_patch, h_patch = test_patch_info['bbox']
            test_roi = image[y:y+h_patch, x:x+w_patch]
            cx, cy = w_patch//2, h_patch//2

            # Step 2: Extract test patch HSV
            test_patch_color_hsv = self._extract_average_color_circle(test_roi, (cx, cy))
            # Removed debug display
            # debug_test = test_roi.copy()
            # cv2.putText(debug_test, f"Test HSV: {test_patch_color_hsv}", (5,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
            # self._show_debug("Test Patch HSV", debug_test, wait_ms=1000)

            # Step 3: Detect reference patches
            reference_patches = self.detect_reference_patches(image, test_patch_bbox=test_patch_info['bbox'])
            if len(reference_patches) < 1:  # Changed from 3 to 1 since we're mapping to hardcoded values
                return {
                    "success": False,
                    "error": f"Need at least 1 reference patch for analysis, found {len(reference_patches)}"
                }

            # Step 4: Extract HSV for reference patches and train KNN Regressor
            X_train, y_train = [], []
            self.reference_segments_data = []
            for i, patch in enumerate(reference_patches):
                x, y, w, h = patch['bbox']
                roi = image[y:y+h, x:x+w]
                cx, cy = w//2, h//2
                avg_hsv = self._extract_average_color_circle(roi, (cx, cy))
                label = self.fixed_ph_labels[i] if i < len(self.fixed_ph_labels) else 0
                X_train.append(avg_hsv)
                y_train.append(label)
                self.reference_segments_data.append({'label': label,'color': avg_hsv,'bbox':(x,y,w,h)})

            # Train KNN Regressor
            n_neighbors = min(3, len(X_train))  # Use 3 neighbors or less if we don't have enough data
            self.knn_model = KNeighborsRegressor(n_neighbors=n_neighbors, weights='distance')
            self.knn_model.fit(np.array(X_train), np.array(y_train))

            # Predict pH using regression (get continuous value first)
            continuous_ph_value = self.knn_model.predict(np.array(test_patch_color_hsv).reshape(1, -1))[0]
            
            # Map continuous value to hardcoded pH list
            estimated_ph_value = self._map_to_hardcoded_ph(continuous_ph_value)
            
            # Calculate distance to nearest neighbors for debugging
            from sklearn.neighbors import NearestNeighbors
            nn_for_distance = NearestNeighbors(n_neighbors=1)
            nn_for_distance.fit(np.array(X_train))
            distances, indices = nn_for_distance.kneighbors(np.array(test_patch_color_hsv).reshape(1, -1))
            min_distance = distances[0][0]

            if debug:  # Only console debug output
                print(f"Debug: Using {n_neighbors} neighbors for regression")
                print(f"Debug: Continuous pH prediction={continuous_ph_value:.2f}")
                print(f"Debug: Mapped to hardcoded pH={estimated_ph_value}")
                print(f"Debug: Min distance to reference={min_distance:.2f}")
                print(f"Debug: Available hardcoded pH values: {self.fixed_ph_labels}")
                print(f"Debug: Reference pH values used: {y_train}")

            # Create visualization
            vis_image = self.visualize_results(output_image, test_patch_info, reference_patches, estimated_ph_value)

            # Save only the final annotated result image
            result_images = []
            if result_folder and analysis_id:
                os.makedirs(result_folder, exist_ok=True)
                
                # Save only the final annotated result image
                result_image_path = os.path.join(result_folder, f"{analysis_id}_ph_result.jpg")
                cv2.imwrite(result_image_path, vis_image)
                result_images.append(result_image_path)

            # Return results in format expected by Flask app - ONLY hardcoded values
            return {
                "success": True,
                "estimated_ph": float(estimated_ph_value),  # Only hardcoded value
                "test_patch_color_hsv": test_patch_color_hsv,
                "annotated_image": vis_image,
                "min_distance_to_reference": float(min_distance),
                "detected_reference_patches_count": len(reference_patches),
                "result_images": result_images,
                
                # Legacy format for backward compatibility
                "estimated_ph_value": float(estimated_ph_value)  # Only hardcoded value
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }

if __name__ == "__main__":
    analyzer = PHStripAnalyzer(debug=False)  # Changed to False to disable debug displays

    image_path = r"C:\Users\dell\Downloads\test10.jpeg"

    try:
        results = analyzer.analyze_ph_strip(image_path, debug=True)  # debug=True only for console output
        
        if results["success"]:
            print("\n--- pH Test Strip Analysis Results ---")
            print(f"Estimated pH Value: {results['estimated_ph']}")
            print(f"Test Patch HSV Color: {results['test_patch_color_hsv']}")
            print(f"Reference Patches Detected: {results['detected_reference_patches_count']}")
            print(f"Min Distance to Reference: {results['min_distance_to_reference']:.2f}")

            # Only show final result in standalone mode
            cv2.imshow("Annotated pH Strip", results["annotated_image"])
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(f"Analysis failed: {results['error']}")
            
    except Exception as e:
        print(f"Error: {e}")
