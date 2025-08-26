import cv2
import numpy as np
from segment_anything import SamPredictor, sam_model_registry
import torch
from transformers import pipeline
import mediapipe as mp

class AutoFootMasking:
    def __init__(self):
        self.setup_models()
    
    def setup_models(self):
        """Initialize automatic masking models"""
        # MediaPipe for pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
        
        # SAM for segmentation (if available)
        try:
            sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")
            self.sam_predictor = SamPredictor(sam)
            self.sam_available = True
        except:
            self.sam_available = False
            print("SAM not available, using traditional methods")
    
    def detect_foot_region(self, image):
        """Detect foot region using MediaPipe pose estimation"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_image)
        
        foot_points = []
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w = image.shape[:2]
            
            # Get foot landmarks
            foot_indices = [27, 28, 29, 30, 31, 32]  # Ankle, heel, foot_index landmarks
            for idx in foot_indices:
                if idx < len(landmarks):
                    x = int(landmarks[idx].x * w)
                    y = int(landmarks[idx].y * h)
                    foot_points.append([x, y])
        
        return foot_points
    
    def create_rough_mask_traditional(self, image):
        """Create rough foot mask using traditional CV methods"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Skin color detection in HSV
        lower_skin = np.array([0, 20, 70])
        upper_skin = np.array([20, 255, 255])
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Focus on lower part of image (likely foot region)
        h, w = image.shape[:2]
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        roi_mask[h//2:, :] = 255  # Lower half
        
        # Combine masks
        combined_mask = cv2.bitwise_and(skin_mask, roi_mask)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        return combined_mask
    
    def create_sam_mask(self, image, foot_points):
        """Create mask using SAM with foot points as prompts"""
        if not self.sam_available or not foot_points:
            return None
        
        self.sam_predictor.set_image(image)
        
        # Use foot points as positive prompts
        input_points = np.array(foot_points)
        input_labels = np.ones(len(foot_points))
        
        masks, scores, _ = self.sam_predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True,
        )
        
        # Return best mask
        best_mask = masks[np.argmax(scores)]
        return (best_mask * 255).astype(np.uint8)
    
    def process_image(self, image_path, output_path):
        """Process single image and create foot mask"""
        image = cv2.imread(image_path)
        
        # Method 1: Detect foot points
        foot_points = self.detect_foot_region(image)
        
        # Method 2: Try SAM if available
        if self.sam_available and foot_points:
            mask = self.create_sam_mask(image, foot_points)
            if mask is not None:
                cv2.imwrite(output_path, mask)
                return True
        
        # Method 3: Traditional CV fallback
        mask = self.create_rough_mask_traditional(image)
        cv2.imwrite(output_path, mask)
        return True
    
    def batch_process(self, input_dir, output_dir):
        """Process all images in directory"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        images = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        for img_name in images:
            input_path = os.path.join(input_dir, img_name)
            output_path = os.path.join(output_dir, img_name.replace('.jpg', '.png'))
            
            try:
                self.process_image(input_path, output_path)
                print(f"✅ Processed: {img_name}")
            except Exception as e:
                print(f"❌ Failed: {img_name} - {e}")

def create_annotation_gui():
    """Simple GUI for quick manual corrections"""
    gui_code = '''
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

class QuickAnnotator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quick Foot Mask Corrector")
        
        # Load image and mask
        tk.Button(self.root, text="Load Image", command=self.load_image).pack()
        tk.Button(self.root, text="Load Auto Mask", command=self.load_mask).pack()
        tk.Button(self.root, text="Save Corrected Mask", command=self.save_mask).pack()
        
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg='white')
        self.canvas.pack()
        
        self.image = None
        self.mask = None
        
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path)
            self.display_image()
    
    def load_mask(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.mask = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            self.display_overlay()
    
    def display_image(self):
        if self.image is not None:
            img_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_pil = img_pil.resize((800, 600))
            self.photo = ImageTk.PhotoImage(img_pil)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = QuickAnnotator()
    app.run()
'''
    
    with open('quick_annotator.py', 'w') as f:
        f.write(gui_code)
    
    print("Created quick_annotator.py for manual corrections")

if __name__ == '__main__':
    # Auto masking setup
    auto_masker = AutoFootMasking()
    
    # Process images
    input_directory = 'raw_images'
    output_directory = 'auto_masks'
    
    if os.path.exists(input_directory):
        auto_masker.batch_process(input_directory, output_directory)
        print(f"\n✅ Auto-masking completed! Check {output_directory}/")
        print("💡 Tip: Review and correct masks manually using quick_annotator.py")
    else:
        print(f"Create {input_directory}/ folder and add your images")
    
    create_annotation_gui()