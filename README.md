# Manual Image Mask Annotator

A simple tool for manually creating pixel-perfect masks for foot and footwear segmentation.

## Features

- **Simple brush interface**: Paint and erase with adjustable brush size
- **Team collaboration**: Distribute work among multiple annotators
- **Progress tracking**: Monitor annotation progress
- **Single class segmentation**: `foot_with_footwear` (includes bare feet, socks, shoes, sandals, etc.)

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Simple Annotation
For individual annotation:
```bash
python simple_brush_annotator.py
```

### 3. Team Collaboration
For team-based annotation:
```bash
python annotation_system.py
```

## When to Use Team Collaboration

**Use team collaboration when:**
- You have 100+ images to annotate
- Multiple people available to help
- Need to distribute workload evenly
- Want to track individual progress

**Use simple annotation when:**
- Small dataset (<100 images)
- Working alone
- Quick one-off annotation task

## How Team Collaboration Works

### Setup (Run once):
1. Put all images in `raw_images/` folder
2. Run `python annotation_system.py`
3. Images automatically distributed to team members

### Each team member:
1. Navigate to their assigned folder: `cd annotation_workspace/member1/assigned/`
2. Run: `python ../../../simple_brush_annotator.py`
3. When prompted, press Enter (uses current directory)
4. Annotate assigned images
5. Masks saved to: `annotation_workspace/member1/masks/`

### Progress tracking:
- Run: `python annotation_system.py --progress`
- Progress saved to: `annotation_workspace/progress.json`
- Each member's completed count tracked automatically

## Labeling Guidelines

### Include in Masks:
✅ Bare feet (complete surface)  
✅ Feet with socks  
✅ Any footwear (shoes, sandals, flip-flops, boots)  
✅ Partially visible feet  

### Exclude from Masks:
❌ Leg area above ankle  
❌ Shadows on ground  
❌ Reflections  
❌ Background objects  

## Controls (Simple Brush Annotator)

- **Left click + drag**: Paint/Erase (depends on mode)
- **Right click + drag**: Always erase
- **'e'**: Toggle erase mode
- **'+'/'-'**: Change brush size
- **'s'**: Save mask
- **'n'**: Next image
- **'p'**: Previous image
- **'c'**: Clear mask
- **'q'**: Quit

## File Structure

```
image_mask_annotator/
├── simple_brush_annotator.py    # Main annotation tool
├── annotation_system.py         # Team collaboration system
├── annotation_workspace/        # Team workspace
│   ├── member1/
│   │   ├── assigned/            # Images to annotate
│   │   ├── completed/           # Completed images
│   │   └── masks/               # Created masks
│   └── final_masks/             # Merged final masks
├── raw_images/                  # Source images
└── requirements.txt             # Dependencies
```

## Usage

1. Place your images in appropriate folders
2. Run the annotation tool
3. Create masks by painting over foot/footwear areas
4. Save masks as PNG files (0=background, 255=foot_with_footwear)