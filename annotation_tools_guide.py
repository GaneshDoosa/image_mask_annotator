import os

def create_annotation_guide():
    """Create comprehensive annotation tool guide"""
    
    guide = """
# 🎨 FOOT ANNOTATION TOOLS GUIDE

## 1. LABELME (Polygon + Brush)
```bash
pip install labelme
labelme assigned/
```
**Tools available:**
- ✅ **Polygon**: Click points around foot outline (precise edges)
- ✅ **Brush**: Paint over foot area (faster for complex shapes)
- ✅ **Rectangle**: Quick bounding box
- ✅ **Circle**: For round foot areas

**Best for:** Mixed approach - polygon for edges, brush for filling

## 2. CVAT (Professional Brush Tool)
```bash
# Web-based, supports brush painting
# Visit: cvat.org
```
**Features:**
- ✅ **Smart brush**: AI-assisted painting
- ✅ **Polygon**: Precise boundaries
- ✅ **Interpolation**: Auto-fill between frames

**Best for:** Large datasets, team collaboration

## 3. PHOTOSHOP/GIMP (Full Brush Control)
**Photoshop:**
- Use **Quick Selection Tool** or **Brush Tool**
- Save as PNG mask (0=background, 255=foot)

**GIMP (Free):**
- **Fuzzy Select** + **Paintbrush Tool**
- Export as PNG

**Best for:** High precision, complex foot shapes

## 4. ROBOFLOW (Online Brush)
```bash
# Upload images to roboflow.com
# Use brush tool for segmentation
```
**Features:**
- ✅ **Smart brush**: AI-assisted
- ✅ **Team collaboration**
- ✅ **Auto-export** to training format

**Best for:** No software installation needed
"""
    
    with open('ANNOTATION_TOOLS_GUIDE.md', 'w') as f:
        f.write(guide)
    
    # Create LabelMe brush config
    labelme_config = """
# LabelMe with Brush Tool Instructions

## Enable Brush Mode:
1. Open LabelMe: `labelme assigned/`
2. Click "Create Polygons" dropdown
3. Select "Create Brush" 
4. Paint over foot area
5. Label as "foot_with_footwear"
6. Save

## Brush Settings:
- Brush size: Adjust with mouse wheel
- Undo: Ctrl+Z
- Zoom: Mouse wheel while holding Ctrl

## Mixed Approach (Recommended):
1. Use Polygon for clean edges
2. Use Brush for complex internal areas
3. Combine both for best results
"""
    
    with open('LABELME_BRUSH_GUIDE.md', 'w') as f:
        f.write(labelme_config)

def create_brush_annotation_script():
    """Create script for brush-based annotation"""
    
    script = """
import cv2
import numpy as np

class BrushAnnotator:
    def __init__(self):
        self.drawing = False
        self.brush_size = 10
        self.mask = None
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            cv2.circle(self.mask, (x, y), self.brush_size, 255, -1)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
    
    def annotate_image(self, image_path):
        image = cv2.imread(image_path)
        self.mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        cv2.namedWindow('Brush Annotator')
        cv2.setMouseCallback('Brush Annotator', self.mouse_callback)
        
        while True:
            display = cv2.addWeighted(image, 0.7, cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR), 0.3, 0)
            cv2.imshow('Brush Annotator', display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):  # Save
                mask_path = image_path.replace('.jpg', '_mask.png')
                cv2.imwrite(mask_path, self.mask)
                print(f"Saved: {mask_path}")
                break
            elif key == ord('c'):  # Clear
                self.mask = np.zeros(image.shape[:2], dtype=np.uint8)
            elif key == ord('q'):  # Quit
                break
        
        cv2.destroyAllWindows()

# Usage
annotator = BrushAnnotator()
annotator.annotate_image('path/to/image.jpg')
"""
    
    with open('brush_annotator.py', 'w') as f:
        f.write(script)

if __name__ == '__main__':
    create_annotation_guide()
    create_brush_annotation_script()
    
    print("✅ Created annotation guides:")
    print("📖 ANNOTATION_TOOLS_GUIDE.md - Complete tool comparison")
    print("🖌️ LABELME_BRUSH_GUIDE.md - LabelMe brush instructions") 
    print("🎨 brush_annotator.py - Custom brush tool")
    
    print("\n🎯 RECOMMENDATION:")
    print("Use LabelMe with BRUSH mode - it's the fastest!")
    print("Command: labelme assigned/ (then select brush tool)")