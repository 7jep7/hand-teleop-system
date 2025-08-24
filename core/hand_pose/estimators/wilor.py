from typing import Optional
import numpy as np

try:
    from wilor_mini.pipelines.wilor_hand_pose3d_estimation_pipeline import (
        WiLorHandPose3dEstimationPipeline,
    )
except ImportError:
    WiLorHandPose3dEstimationPipeline = None

from core.hand_pose.estimators.base import HandPoseEstimator
from core.hand_pose.types import HandKeypointsPred, TrackedHandKeypoints
from core.resource_manager import ResourceManager, ProgressTracker, configure_torch_for_safety


class WiLorEstimator(HandPoseEstimator):
    """Resource-controlled WiLoR hand pose estimator"""
    
    def __init__(self, device: Optional[str] = None):
        if WiLorHandPose3dEstimationPipeline is None:
            raise ImportError("WiLoR not installed. Run: pip install 'https://github.com/Joeclinton1/WiLoR-mini'")
            
        self.resource_manager = ResourceManager(
            max_cpu_percent=60.0,      # Reduced from 85% to prevent overload  
            max_memory_percent=70.0,   # Reduced from 90% to prevent Chrome freeze
            max_gpu_memory_percent=50.0, # Reduced from 75% to share with browser
            model_loading_mode=True    # Special mode for model loading
        )        # Configure torch for safety before creating pipeline
        configure_torch_for_safety()
        
        print("🔧 Initializing WiLoR with resource management...")
        
        with self.resource_manager.controlled_execution() as rm:
            try:
                import torch
                
                # Determine device safely
                if device is None:
                    if torch.cuda.is_available():
                        device = "cuda"
                        print("🎮 Using GPU with safety limits")
                    else:
                        device = "cpu"
                        print("💻 Using CPU")
                else:
                    print(f"🎯 Using specified device: {device}")
                
                # Create pipeline with resource management
                self.pipe = WiLorHandPose3dEstimationPipeline(
                    device=device,
                    dtype=torch.float16 if device == "cuda" else torch.float32,  # Use half precision on GPU
                    verbose=False,
                )
                
                print("✅ WiLoR initialized safely")
                
            except Exception as e:
                print(f"❌ Failed to initialize WiLoR: {e}")
                raise

    def __call__(self, image: np.ndarray, focal_len: float) -> list[HandKeypointsPred]:
        """Process image with resource management and progress tracking"""
        
        with self.resource_manager.controlled_execution() as rm:
            progress = ProgressTracker(3, "WiLoR Processing")
            
            try:
                progress.update(1, "Running WiLoR inference...")
                raw_preds = self.pipe.predict(image)
                
                progress.update(2, "Processing results...")
                preds = []
                for p in raw_preds:
                    kp = p["wilor_preds"]["pred_keypoints_3d"][0] + p["wilor_preds"]["pred_cam_t_full"][0]
                    kp *= (1, -1, 1)  # Wilor coordinates need to be flipped in the y axis
                    kp_mm = kp * 1000  # Convert to mm
                    
                    keypoints = []
                    for idx in range(21):
                        keypoints.append(TrackedHandKeypoints(np.array([kp_mm[idx]])))

                    preds.append(HandKeypointsPred(keypoints, focal_len))
                
                progress.update(3, "Complete")
                progress.complete()
                return preds
                
            except Exception as e:
                print(f"❌ WiLoR processing failed: {e}")
                raise
