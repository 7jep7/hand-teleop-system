import os
from typing import List, Optional

import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import vision

from core.hand_pose.estimators.base import HandPoseEstimator
from core.hand_pose.types import HandKeypointsPred, TrackedHandKeypoints


class MediaPipeEstimator(HandPoseEstimator):
    """
    Wraps MediaPipe GestureRecognizer in VIDEO mode and converts its world-
    landmarks to camera-space key-points (metres), matching HandKeypointsPred.
    """

    _DT_MS = 33  # advance timestamp by ~1 / 30 s per call

    def __init__(
        self,
        device: Optional[str] = None,
        model_path: str = os.path.join(os.path.dirname(__file__), "gesture_recognizer.task"),
        num_hands: int = 1,
    ):
        BaseOptions = mp.tasks.BaseOptions
        GestureRecognizerOptions = vision.GestureRecognizerOptions
        VisionRunningMode = vision.RunningMode

        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.1,
            min_hand_presence_confidence=0.4,
            min_tracking_confidence=0.4
        )
        self._rec = vision.GestureRecognizer.create_from_options(options)
        self._ts_ms = 0  # rolling video timestamp

    # ------------------------------------------------------------------ #
    def __call__(self, frame_rgb: np.ndarray, f_px: float) -> List[HandKeypointsPred]:
        h, w = frame_rgb.shape[:2]
        cx, cy = w * 0.5, h * 0.5

        mp_img = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb,
        )
        res = self._rec.recognize_for_video(mp_img, self._ts_ms)
        self._ts_ms += self._DT_MS

        if not res.hand_landmarks:
            return []

        preds: list[HandKeypointsPred] = []
        for ilm, hand in zip(res.hand_landmarks, res.handedness):
            # Use 2D normalized coordinates directly - much simpler!
            landmarks_2d = []
            for lm in ilm:
                landmarks_2d.append({
                    "x": lm.x,  # Already normalized [0,1]
                    "y": lm.y,  # Already normalized [0,1] 
                    "z": lm.z,  # Relative depth
                    "visibility": getattr(lm, 'visibility', 1.0)
                })
            
            # Create a simple result that includes the 2D landmarks
            result = {
                "is_right": hand[0].category_name.lower() == "right",
                "landmarks_2d": landmarks_2d,
                "keypoints": None  # We'll extract keypoints in the backend
            }
            
            preds.append(result)

        return preds
        return preds