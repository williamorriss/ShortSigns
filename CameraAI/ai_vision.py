import mediapipe as mp
from PyQt6.QtGui import QPixmap, QImage
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2
import os

type Gesture = np.ndarray

#from gesture import Gesture

class VisionManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),        # Index
        (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
        (0, 13), (13, 14), (14, 15), (15, 16), # Ring
        (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
        (5, 9), (9, 13), (13, 17)              # Palm connections
    ]

    def __init__(self, model_path=None, cap_no: int = 0):
        self.last_timestamp = 0

        # Fix: Use provided model_path or default to script directory
        if model_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(script_dir, "hand_landmarker.task")
        self.model_path = model_path
        print(self.model_path)
        
        # Check if model exists
        if not os.path.exists(self.model_path):
            print(f"Error: Model file not found at {self.model_path}")
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        # Create the landmarker once (not per frame)
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        self.options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=vision.RunningMode.VIDEO
        )
        
        # Create the landmarker as an instance variable (reused)
        try:
            self.landmarker = vision.HandLandmarker.create_from_options(self.options)
        except Exception as e:
            print(f"Error creating landmarker: {e}")
            self.landmarker = None

        # Initialize webcam
        self.cap = cv2.VideoCapture(cap_no)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            self.cap = None

    def set_source(self, cap_no: int):
        self.cap.release()
        self.cap = cv2.VideoCapture(cap_no)

    @staticmethod
    def instance() -> "VisionManager":
        if VisionManager._instance is None:
            VisionManager._instance = VisionManager()
        return VisionManager._instance



    def release(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        if self.landmarker:
            self.landmarker.close()
        cv2.destroyAllWindows()

    ######################################################################

    def get_frame(self) -> Gesture | None:
        """Get a single frame from webcam"""
        if self.cap is None:
            print("Webcam not initialized")
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Could not read frame")
            return None
        
        # Flip horizontally for mirror view
        frame = cv2.flip(frame, 1)
        return frame
    
    def get_annotated_frame(self, landmarkers, frame) -> Gesture | None:
        # Draw hand landmarks if detected
        if landmarkers.hand_landmarks:
            # Draw the landmarks
            annotated_frame = self._draw_hand_landmarks(frame, landmarkers.hand_landmarks)

            # Add finger count information
            for i, hand_landmarks in enumerate(landmarkers.hand_landmarks):
                finger_count = self._count_fingers(hand_landmarks)

                # Get wrist position for text placement
                h, w, _ = frame.shape
                wrist_x, wrist_y = self._to_pixel(hand_landmarks[0].x, hand_landmarks[0].y, w, h)

                # Display finger count
                cv2.putText(annotated_frame, f"Fingers: {finger_count}",
                           (wrist_x, wrist_y - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                # Get hand type if available
                if landmarkers.handedness and len(landmarkers.handedness) > i:
                    hand_type = landmarkers.handedness[i][0].category_name
                    cv2.putText(annotated_frame, hand_type,
                               (wrist_x, wrist_y - 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        else:
            annotated_frame = frame

        # Add info panel
        cv2.rectangle(annotated_frame, (10, 10), (250, 70), (0, 0, 0), -1)
        cv2.putText(annotated_frame, "Hand Tracking Active", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Show hand count
        hand_count = len(landmarkers.hand_landmarks) if landmarkers.hand_landmarks else 0
        cv2.putText(annotated_frame, f"Hands detected: {hand_count}", (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return annotated_frame

    ######################################################################

    def record_gesture(self, hand_landmarks) -> Gesture | None:
        features = self._get_landmark_features(hand_landmarks)
        return features

        
    def recognise_gesture(self, saved_gestures, hand_landmarks, threshold = 0.5):
        if not saved_gestures:
            return None, 1.0
        
        current_features = self._get_landmark_features(hand_landmarks)
        
        best_match = None
        best_distance = float('inf')
        
        for name, binding in saved_gestures.items():
            hands = binding.gesture

            if len(hands) != len(current_features) or not len(hands):
                continue
            total_distance = 0

            for i, template_features in enumerate(hands):
                # Calculate Euclidean distance between feature vectors
                distance = best_distance
                distance = np.linalg.norm(current_features[i] - template_features)              
                total_distance += distance

            if distance < best_distance:
                best_distance = total_distance
                best_match = name
        
        # Normalize score (0 = perfect match, 1 = completely different)
        normalized_score = min(best_distance / threshold, 1.0)
        
        #print(f"Best match: {best_match}, distance: {best_distance:.3f}, confidence: {1-normalized_score:.2f}")
        
        if best_distance < threshold:
            return best_match, normalized_score
        else:
            return None, normalized_score

    ######################################################################

    def get_landmarkers(self, frame):
        """Get hand landmarks from a frame"""
        if self.landmarker is None:
            print("Landmarker not initialized")
            return None

        if frame is None:
            print("Frame is None")
            return None

        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            current_time = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
            
            # Ensure timestamp is strictly increasing
            if current_time <= self.last_timestamp:
                current_time = self.last_timestamp + 1
            
            self.last_timestamp = current_time

            # Detect hands in the frame (reuse existing landmarker)
            result = self.landmarker.detect_for_video(mp_image, current_time)
            return result

        except Exception as e:
            print(f"Detection error: {e}")
            return None

    def update_frame(self) -> QPixmap | None:
        frame = self.get_frame()
        if frame is None:
            return None
        landmarks = self.get_landmarkers(frame)
        if landmarks is None:
            return None
        bgra = self.get_annotated_frame(landmarks, frame)
        if bgra is None:
            return None

        rgb = cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGB)
        h, w, ch = rgb.shape
        q_image = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy() # type: ignore
        return QPixmap.fromImage(q_image)

    def _get_landmark_features(self, hand_landmarks):
        full_features = []

        for hand in hand_landmarks:
            features = []
        
            # Calculate hand size for normalization
            hand_size = self._calculate_hand_size(hand)
            if hand_size < 0.001:  # Prevent division by zero
                hand_size = 0.001

            # Key landmark indices
            palm_center = 0  # Wrist
            fingertips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
            knuckles = [1, 5, 9, 13, 17]  # Knuckles of each finger

            # 1. Distances from palm to each fingertip (NORMALIZED by hand size)
            palm = hand[palm_center]

            for tip in fingertips:
                dist = self._calculate_distance_3d(palm, hand[tip])
                normalized_dist = dist / hand_size  # This makes it scale-invariant
                features.append(normalized_dist)

            # 2. Distances between adjacent fingertips (NORMALIZED)
            for i in range(len(fingertips) - 1):
                dist = self._calculate_distance_3d(
                    hand[fingertips[i]], 
                    hand[fingertips[i+1]]
                )
                normalized_dist = dist / hand_size
                features.append(normalized_dist)

            # 3. Distances from each fingertip to palm (NORMALIZED) - adding more robust features
            for tip in fingertips:
                dist = self._calculate_distance_3d(palm, hand[tip])
                normalized_dist = dist / hand_size
                features.append(normalized_dist)

            # 4. Angles between fingers (these are already scale-invariant)
            for i in range(len(fingertips)):
                for j in range(i+1, len(fingertips)):
                    angle = self._calculate_angle_between_points(
                        hand[fingertips[i]],
                        hand[palm_center],
                        hand[fingertips[j]]
                    )
                    features.append(angle)

            # 5. Finger bend angles (how curled each finger is)
            for tip, knuckle in zip(fingertips, knuckles):
                # Angle between fingertip, knuckle, and palm
                angle = self._calculate_angle_between_points(
                    hand[tip],
                    hand[knuckle],
                    hand[palm_center]
                )
                features.append(angle)

            # 6. Add hand size ratio features (relative proportions)
            # Distance from thumb to pinky normalized
            thumb_pinky_dist = self._calculate_distance_3d(
                hand[4], hand[20]
            )
            features.append(thumb_pinky_dist / hand_size)

            # Distance from index to ring normalized
            index_ring_dist = self._calculate_distance_3d(
                hand[8], hand[16]
            )
            features.append(index_ring_dist / hand_size)

            features = np.array(features)
            full_features.append(features)
        
        return np.array(full_features)
    
    def _calculate_hand_size(self, hand_landmarks):
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
    
    def _calculate_distance_3d(self, lm1, lm2):
        """Calculate Euclidean distance between two landmarks"""
        dx = lm1.x - lm2.x
        dy = lm1.y - lm2.y
        dz = lm1.z - lm2.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _calculate_angle_between_points(self, p1, p2, p3):
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

    ######################################################################

    def _to_pixel(self, x_norm: float, y_norm: float, w: int, h: int) -> tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates"""
        x = min(max(x_norm, 0.0), 1.0)
        y = min(max(y_norm, 0.0), 1.0)
        return int(x * w), int(y * h)

    def _draw_hand_landmarks(
        self,
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
            pts = [self._to_pixel(lm.x, lm.y, w, h) for lm in hand_landmarks]

            if draw_connections:
                for a, b in connections:
                    cv2.line(annotated, pts[a], pts[b], (0, 255, 0), line_thickness)

            if draw_points:
                for (x, y) in pts:
                    cv2.circle(annotated, (x, y), point_radius, (0, 0, 255), point_thickness)

        return annotated

    def _count_fingers(self, hand_landmarks):
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
    
if __name__ == "__main__":
    manager = VisionManager()
    while True:
        frame = manager.get_frame()
        landmarkers = manager.get_landmarkers(frame)
        annotated_frame = manager.get_annotated_frame(landmarkers, frame)
        cv2.imshow("Annotated Frame", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.waitKey(1) & 0xFF == ord('r'):
            state = manager.record_gesture("test", landmarkers.hand_landmarks)
            if state:
                print("Gesture recorded successfully")
                print(manager.saved_gestures)
            else:
                print("Error recording gesture")
        if cv2.waitKey(1) & 0xFF == ord('t'):
            gesture, confidence = manager.recognise_gesture(landmarkers.hand_landmarks)
            print(f"Gesture: {gesture}, Confidence: {confidence}")
        if cv2.waitKey(1) & 0xFF == ord('p'):
            state = manager.save_gestures_to_json()
            if state:
                print("Gestures saved to file")
            else:
                print("Error saving gestures to file")
        if cv2.waitKey(1) & 0xFF == ord('l'):
            state = manager.load_gestures_from_json()
            if state:
                print("Gestures loaded from file")
            else:
                print("Error loading gestures from file")