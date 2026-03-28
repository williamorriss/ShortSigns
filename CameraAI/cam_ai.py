import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import os
import numpy as np

import numpy as np
import cv2

import numpy as np
import cv2

class GestureRecognizer:
    def __init__(self):
        # Store gesture templates
        self.gesture_templates = {}
        
    def calculate_hand_size(self, hand_landmarks):
        """
        Calculate hand size as the distance from wrist to middle fingertip
        This is used for normalization
        """
        wrist = hand_landmarks[0]
        middle_tip = hand_landmarks[12]
        
        # Calculate distance
        dx = wrist.x - middle_tip.x
        dy = wrist.y - middle_tip.y
        dz = wrist.z - middle_tip.z
        
        hand_size = np.sqrt(dx*dx + dy*dy + dz*dz)
        return hand_size
    
    def extract_features(self, hand_landmarks):
        """
        Extract position-invariant features from hand landmarks
        All distances are normalized by hand size to make them scale-invariant
        All angles are already scale-invariant
        """
        features = []
        
        # Calculate hand size for normalization
        hand_size = self.calculate_hand_size(hand_landmarks[0])
        if hand_size < 0.001:  # Prevent division by zero
            hand_size = 0.001
        
        # Key landmark indices
        palm_center = 0  # Wrist
        fingertips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        knuckles = [1, 5, 9, 13, 17]  # Knuckles of each finger
        
        # 1. Distances from palm to each fingertip (NORMALIZED by hand size)
        palm = hand_landmarks[0][palm_center]
        
        for tip in fingertips:
            dist = self.calculate_distance_3d(palm, hand_landmarks[0][tip])
            normalized_dist = dist / hand_size  # This makes it scale-invariant
            features.append(normalized_dist)
        
        # 2. Distances between adjacent fingertips (NORMALIZED)
        for i in range(len(fingertips) - 1):
            dist = self.calculate_distance_3d(
                hand_landmarks[0][fingertips[i]], 
                hand_landmarks[0][fingertips[i+1]]
            )
            normalized_dist = dist / hand_size
            features.append(normalized_dist)
        
        # 3. Distances from each fingertip to palm (NORMALIZED) - adding more robust features
        for tip in fingertips:
            dist = self.calculate_distance_3d(palm, hand_landmarks[0][tip])
            normalized_dist = dist / hand_size
            features.append(normalized_dist)
        
        # 4. Angles between fingers (these are already scale-invariant)
        for i in range(len(fingertips)):
            for j in range(i+1, len(fingertips)):
                angle = self.calculate_angle_between_points(
                    hand_landmarks[0][fingertips[i]],
                    hand_landmarks[0][palm_center],
                    hand_landmarks[0][fingertips[j]]
                )
                features.append(angle)
        
        # 5. Finger bend angles (how curled each finger is)
        for tip, knuckle in zip(fingertips, knuckles):
            # Angle between fingertip, knuckle, and palm
            angle = self.calculate_angle_between_points(
                hand_landmarks[0][tip],
                hand_landmarks[0][knuckle],
                hand_landmarks[0][palm_center]
            )
            features.append(angle)
        
        # 6. Add hand size ratio features (relative proportions)
        # Distance from thumb to pinky normalized
        thumb_pinky_dist = self.calculate_distance_3d(
            hand_landmarks[0][4], hand_landmarks[0][20]
        )
        features.append(thumb_pinky_dist / hand_size)
        
        # Distance from index to ring normalized
        index_ring_dist = self.calculate_distance_3d(
            hand_landmarks[0][8], hand_landmarks[0][16]
        )
        features.append(index_ring_dist / hand_size)
        
        return np.array(features)
    
    def calculate_distance_3d(self, lm1, lm2):
        """Calculate Euclidean distance between two landmarks"""
        dx = lm1.x - lm2.x
        dy = lm1.y - lm2.y
        dz = lm1.z - lm2.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def calculate_angle_between_points(self, p1, p2, p3):
        """
        Calculate angle between vectors (p1->p2) and (p2->p3)
        """
        # Convert to vectors
        v1 = np.array([p1.x - p2.x, p1.y - p2.y, p1.z - p2.z])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y, p3.z - p2.z])
        
        # Calculate angle
        dot = np.dot(v1, v2)
        mag1 = np.linalg.norm(v1)
        mag2 = np.linalg.norm(v2)
        
        if mag1 * mag2 == 0:
            return 0
        
        angle = np.arccos(np.clip(dot / (mag1 * mag2), -1.0, 1.0))
        return angle
    
    def record_gesture(self, gesture_name, hand_landmarks):
        """Record a gesture template"""
        features = self.extract_features(hand_landmarks)
        self.gesture_templates[gesture_name] = features
        print(f"Recorded gesture: {gesture_name}")
        print(f"Feature vector length: {len(features)}")
        print(f"Sample features: {features[:5]}")  # Show first 5 features
    
    def recognize_gesture(self, hand_landmarks, threshold=0.5):
        """
        Recognize current gesture by comparing with templates
        Lower threshold = stricter matching
        """
        if not self.gesture_templates:
            return None, 1.0
        
        current_features = self.extract_features(hand_landmarks)
        
        best_match = None
        best_score = float('inf')
        best_distance = float('inf')
        
        for name, template_features in self.gesture_templates.items():
            # Calculate Euclidean distance between feature vectors
            distance = np.linalg.norm(current_features - template_features)
            
            # Also try cosine similarity for comparison
            cosine_sim = np.dot(current_features, template_features) / (
                np.linalg.norm(current_features) * np.linalg.norm(template_features) + 1e-8
            )
            
            # Combine both metrics (optional)
            combined_score = distance * (1 - cosine_sim)
            
            if distance < best_distance:
                best_distance = distance
                best_match = name
                best_score = combined_score
        
        # Normalize score (0 = perfect match, 1 = completely different)
        normalized_score = min(best_distance / threshold, 1.0)
        
        #print(f"Best match: {best_match}, distance: {best_distance:.3f}, confidence: {1-normalized_score:.2f}")
        
        if best_distance < threshold:
            return best_match, normalized_score
        else:
            return None, normalized_score
        
####################################################################

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "hand_landmarker.task")

# Verify the model file exists
if not os.path.exists(model_path):
    print(f"Error: Model file not found at {model_path}")
    print("Please make sure hand_landmarker.task is in the same folder as this script")
    exit()

print(f"Using model: {model_path}")

# Hand connections for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm connections
]

def to_pixel(x_norm: float, y_norm: float, w: int, h: int) -> tuple[int, int]:
    """Convert normalized coordinates to pixel coordinates"""
    x = min(max(x_norm, 0.0), 1.0)
    y = min(max(y_norm, 0.0), 1.0)
    return int(x * w), int(y * h)

def draw_hand_landmarks(
    image_bgr: np.ndarray,
    hand_landmarks_list,
    connections=HAND_CONNECTIONS,
    draw_points=True,
    draw_connections=True,
    point_radius=3,
    point_thickness=-1,
    line_thickness=2,
):
    """Draw hand landmarks on the image"""
    annotated = image_bgr.copy()
    h, w = annotated.shape[:2]

    for hand_landmarks in hand_landmarks_list:
        # Convert normalized landmarks to pixel coords
        pts = [to_pixel(lm.x, lm.y, w, h) for lm in hand_landmarks]

        if draw_connections:
            for a, b in connections:
                cv2.line(annotated, pts[a], pts[b], (0, 255, 0), line_thickness)

        if draw_points:
            for (x, y) in pts:
                cv2.circle(annotated, (x, y), point_radius, (0, 0, 255), point_thickness)

    return annotated

def count_fingers(hand_landmarks):
    """Count number of raised fingers"""
    # Fingertip landmarks
    tips = [4, 8, 12, 16, 20]
    finger_count = 0
    
    # Thumb (special case - compare x coordinates)
    if hand_landmarks[4].x < hand_landmarks[3].x:
        finger_count += 1
    
    # Other fingers (compare y coordinates)
    for tip in tips[1:]:
        if hand_landmarks[tip].y < hand_landmarks[tip - 2].y:
            finger_count += 1
    
    return finger_count
    

def run_webcam_hand_tracker():
    """Run hand tracking on webcam feed"""
    
    # Initialize the hand landmarker with VIDEO mode
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        running_mode=vision.RunningMode.VIDEO
    )
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Hand tracking started! Press 'q' to quit")

    # Gesture recorder
    gesture_recorder = GestureRecognizer()
    is_recording = False
    
    try:
        # Create the landmarker
        with vision.HandLandmarker.create_from_options(options) as landmarker:
            
            while True:
                # Read frame from webcam
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip horizontally for mirror view
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create MediaPipe Image object
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Get timestamp in milliseconds
                timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
                
                try:
                    # Detect hands in the frame
                    result = landmarker.detect_for_video(mp_image, timestamp_ms)
                except Exception as e:
                    print(f"Detection error: {e}")
                    continue
                
                # Draw hand landmarks if detected
                if result.hand_landmarks:
                    # Draw the landmarks
                    annotated_frame = draw_hand_landmarks(frame, result.hand_landmarks)
                    
                    # Add finger count information
                    for i, hand_landmarks in enumerate(result.hand_landmarks):
                        finger_count = count_fingers(hand_landmarks)
                        
                        # Get wrist position for text placement
                        h, w, _ = frame.shape
                        wrist_x, wrist_y = to_pixel(hand_landmarks[0].x, hand_landmarks[0].y, w, h)
                        
                        # Display finger count
                        cv2.putText(annotated_frame, f"Fingers: {finger_count}", 
                                   (wrist_x, wrist_y - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # Get hand type if available
                        if result.handedness and len(result.handedness) > i:
                            hand_type = result.handedness[i][0].category_name
                            cv2.putText(annotated_frame, hand_type, 
                                       (wrist_x, wrist_y - 40),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                else:
                    annotated_frame = frame
                
                # Add info panel
                cv2.rectangle(annotated_frame, (10, 10), (300, 100), (0, 0, 0), -1)
                cv2.putText(annotated_frame, "Hand Tracking Active", (20, 35),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(annotated_frame, "Press 'q' to quit", (20, 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show hand count
                hand_count = len(result.hand_landmarks) if result.hand_landmarks else 0
                cv2.putText(annotated_frame, f"Hands detected: {hand_count}", (20, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Show the frame
                cv2.imshow('Hand Tracking', annotated_frame)
                
                # Break loop on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Break loop on 'r' key to start/stop recording
                if cv2.waitKey(1) & 0xFF == ord('r'):
                    print("Recording gestures...")
                    gesture_recorder.record_gesture("gest", result.hand_landmarks)

                best_match, score = gesture_recorder.recognize_gesture(result.hand_landmarks)
                if best_match is not None:
                    print(f"Detected gesture: {best_match}, Score: {score}")


                    
    except Exception as e:
        print(f"Error in tracker: {e}")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam closed")

###############################################################


# Run the webcam tracker
if __name__ == "__main__":
    run_webcam_hand_tracker()