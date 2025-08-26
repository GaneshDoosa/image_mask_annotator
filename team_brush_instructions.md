# 🖌️ TEAM BRUSH ANNOTATION INSTRUCTIONS

## Setup (One-time)
```bash
pip install opencv-python
```

## How to Annotate with Brush Tool

### 1. Go to your assigned folder:
```bash
cd annotation_workspace/member1/assigned/
```

### 2. Run the brush annotator:
```bash
python ../../../simple_brush_annotator.py
```

### 3. Annotation Controls:
- **Left click + drag**: Paint foot area (white)
- **Right click + drag**: Erase (black)
- **+/-**: Change brush size
- **'s'**: Save mask and continue
- **'n'**: Skip to next image
- **'c'**: Clear current mask
- **'q'**: Quit

### 4. What to Paint:
✅ **Paint over entire foot area including:**
- Bare feet
- Socks
- Shoes, sandals, flip-flops
- Any footwear

❌ **Don't paint:**
- Legs above ankle
- Shadows
- Background

### 5. Tips:
- Start with larger brush for main area
- Use smaller brush for details (toes, edges)
- Right-click to fix mistakes
- Zoom in browser if image is small

### 6. File Output:
- Masks automatically saved to `../masks/` folder
- Same filename as image but `.png` extension
- White pixels = foot, Black pixels = background

## Alternative: Use LabelMe with Polygons
If brush tool has issues:
```bash
labelme assigned/
# Draw polygon around foot outline
# Label as "foot_with_footwear"
```