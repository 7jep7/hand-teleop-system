#!/usr/bin/env python3
"""
WiLoR Hand Tracking GUI App
Live camera view with click-to-capture and overlay display
"""
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import os
import subprocess
import time

class WiLoRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiLoR Hand Tracking App")
        self.root.geometry("1200x600")
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.processing = False
        
        # Setup GUI
        self.setup_gui()
        
        # Start camera feed
        self.update_camera()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Live camera feed
        left_frame = ttk.LabelFrame(main_frame, text="Live Camera Feed", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.camera_label = ttk.Label(left_frame)
        self.camera_label.pack()
        
        # Capture button
        self.capture_btn = ttk.Button(left_frame, text="📸 Capture & Process Hand", 
                                     command=self.capture_and_process, style="Accent.TButton")
        self.capture_btn.pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(left_frame, text="Position your RIGHT hand in view", 
                                     foreground="blue")
        self.status_label.pack()
        
        # Right side - Results
        right_frame = ttk.LabelFrame(main_frame, text="WiLoR Results", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.result_label = ttk.Label(right_frame, text="Click 'Capture' to see WiLoR overlay")
        self.result_label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(right_frame, mode='indeterminate')
        self.progress.pack(pady=10, fill=tk.X)
        
        # Instructions
        instructions = ttk.Label(right_frame, text="""
Instructions:
1. Position your RIGHT hand in the camera view
2. Click 'Capture & Process Hand'
3. Wait for WiLoR to process (20-30 seconds first time)
4. See the overlay result with hand tracking!

Controls in overlay:
• Green box = Hand bounding box
• Yellow dots = Fingertips
• Blue dots = Joint positions
        """, justify=tk.LEFT, foreground="gray")
        instructions.pack(pady=20)
        
    def update_camera(self):
        """Update live camera feed"""
        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Resize for display
                frame = cv2.resize(frame, (480, 360))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                # Update label
                self.camera_label.configure(image=photo)
                self.camera_label.image = photo  # Keep a reference
                
        # Schedule next update
        self.root.after(50, self.update_camera)  # ~20 FPS
        
    def capture_and_process(self):
        """Capture current frame and process with WiLoR"""
        if self.processing:
            return
            
        self.processing = True
        self.capture_btn.configure(state='disabled', text="🔄 Processing...")
        self.status_label.configure(text="Processing with WiLoR...", foreground="orange")
        self.progress.start()
        
        # Run processing in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self.process_wilor)
        thread.daemon = True
        thread.start()
        
    def process_wilor(self):
        """Process captured frame with WiLoR (runs in separate thread)"""
        try:
            # Capture current frame
            ret, frame = self.cap.read()
            if not ret:
                self.update_status("❌ Failed to capture frame", "red")
                return
                
            # Save captured frame
            cv2.imwrite("gui_capture.jpg", frame)
            
            # Create a temporary script for WiLoR processing
            script_content = '''
import cv2
import sys
import os

def process_frame():
    try:
        # Load image
        frame = cv2.imread("gui_capture.jpg")
        
        # Load WiLoR
        from hand_teleop.hand_pose.factory import create_estimator
        estimator = create_estimator("wilor")
        
        # Process
        result = estimator.pipe.predict(frame, hand="right")
        
        if not result or len(result) == 0:
            print("NO_HAND_DETECTED")
            return
            
        hand = result[0]
        print("HAND_DETECTED")
        
        # Create overlay
        overlay = frame.copy()
        
        # Draw bounding box
        if 'hand_bbox' in hand:
            x1, y1, x2, y2 = [int(x) for x in hand['hand_bbox']]
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(overlay, "RIGHT HAND", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw keypoints
        if 'wilor_preds' in hand and 'pred_keypoints_2d' in hand['wilor_preds']:
            points = hand['wilor_preds']['pred_keypoints_2d'][0]
            for i, (x, y) in enumerate(points):
                if i in [4, 8, 12, 16, 20]:  # Fingertips
                    color = (0, 255, 255)
                    radius = 8
                else:  # Other joints
                    color = (255, 255, 0)
                    radius = 5
                cv2.circle(overlay, (int(x), int(y)), radius, color, -1)
        
        # Save result
        cv2.imwrite("gui_overlay.jpg", overlay)
        print("OVERLAY_SAVED")
        
        # Clean up
        del estimator
        import gc
        gc.collect()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    process_frame()
'''
            
            # Write temporary script
            with open("temp_wilor_process.py", "w") as f:
                f.write(script_content)
            
            # Run WiLoR processing in separate process
            cmd = ["/mnt/nvme0n1p8/conda-envs/hand-teleop/bin/python", "temp_wilor_process.py"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Check result
            if "HAND_DETECTED" in result.stdout and "OVERLAY_SAVED" in result.stdout:
                # Success - load and display overlay
                self.root.after(0, self.display_overlay, "gui_overlay.jpg")
            elif "NO_HAND_DETECTED" in result.stdout:
                self.root.after(0, self.update_status, "❌ No hand detected in image", "red")
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                self.root.after(0, self.update_status, f"❌ Error: {error_msg[:50]}...", "red")
                
        except subprocess.TimeoutExpired:
            self.root.after(0, self.update_status, "❌ Processing timed out", "red")
        except Exception as e:
            self.root.after(0, self.update_status, f"❌ Error: {str(e)[:50]}...", "red")
        finally:
            # Clean up temp files
            for temp_file in ["temp_wilor_process.py", "gui_capture.jpg"]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            # Reset GUI state
            self.root.after(0, self.reset_gui)
            
    def display_overlay(self, image_path):
        """Display the WiLoR overlay result"""
        try:
            # Load overlay image
            overlay_cv = cv2.imread(image_path)
            overlay_cv = cv2.resize(overlay_cv, (480, 360))
            overlay_rgb = cv2.cvtColor(overlay_cv, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            image = Image.fromarray(overlay_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # Update result label
            self.result_label.configure(image=photo)
            self.result_label.image = photo  # Keep reference
            
            self.update_status("✅ Hand tracking complete!", "green")
            
        except Exception as e:
            self.update_status(f"❌ Display error: {str(e)[:30]}...", "red")
            
    def update_status(self, message, color):
        """Update status label"""
        self.status_label.configure(text=message, foreground=color)
        
    def reset_gui(self):
        """Reset GUI to ready state"""
        self.processing = False
        self.progress.stop()
        self.capture_btn.configure(state='normal', text="📸 Capture & Process Hand")
        
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.root.quit()

def main():
    # Check if conda environment is active
    if "/mnt/nvme0n1p8/conda-envs/hand-teleop" not in os.environ.get("PATH", ""):
        print("❌ Please activate the hand-teleop conda environment first:")
        print("conda activate /mnt/nvme0n1p8/conda-envs/hand-teleop")
        return
    
    root = tk.Tk()
    app = WiLoRApp(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.cleanup)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.cleanup()

if __name__ == "__main__":
    main()
