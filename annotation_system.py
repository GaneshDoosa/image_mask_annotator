import os
import json
import shutil
from datetime import datetime
import hashlib

class CollaborativeAnnotationManager:
    def __init__(self, images_dir, output_dir, team_members):
        self.images_dir = images_dir
        self.output_dir = output_dir
        self.team_members = team_members
        self.setup_directories()
        
    def setup_directories(self):
        """Create directory structure for team collaboration"""
        for member in self.team_members:
            os.makedirs(f"{self.output_dir}/{member}/assigned", exist_ok=True)
            os.makedirs(f"{self.output_dir}/{member}/completed", exist_ok=True)
            os.makedirs(f"{self.output_dir}/{member}/masks", exist_ok=True)
        
        os.makedirs(f"{self.output_dir}/final_masks", exist_ok=True)
        os.makedirs(f"{self.output_dir}/quality_check", exist_ok=True)
    
    def distribute_images(self):
        """Distribute images equally among team members"""
        images = [f for f in os.listdir(self.images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        images_per_member = len(images) // len(self.team_members)
        
        assignment = {}
        for i, member in enumerate(self.team_members):
            start_idx = i * images_per_member
            end_idx = start_idx + images_per_member if i < len(self.team_members) - 1 else len(images)
            
            member_images = images[start_idx:end_idx]
            assignment[member] = member_images
            
            # Copy images to member's folder
            for img in member_images:
                src = os.path.join(self.images_dir, img)
                dst = os.path.join(self.output_dir, member, "assigned", img)
                shutil.copy2(src, dst)
        
        # Save assignment info
        with open(f"{self.output_dir}/assignment.json", 'w') as f:
            json.dump(assignment, f, indent=2)
        
        print(f"Images distributed:")
        for member, imgs in assignment.items():
            print(f"  {member}: {len(imgs)} images")
        
        return assignment
    
    def create_annotation_instructions(self):
        """Create detailed instructions for annotators"""
        instructions = """
# FOOT SEGMENTATION ANNOTATION INSTRUCTIONS

## Tools Needed:
- CVAT (Computer Vision Annotation Tool) - Recommended
- LabelMe - Alternative
- Photoshop/GIMP - Manual option

## Quick Setup with LabelMe:
1. Install: `pip install labelme`
2. Run: `labelme assigned/`
3. Create polygon around foot+footwear
4. Label as "foot_with_footwear"
5. Save as PNG mask

## What to Annotate:
✅ Entire foot surface (bare feet)
✅ Socks covering feet  
✅ Any footwear (shoes, sandals, boots, flip-flops)
✅ Partially visible feet
✅ Multiple feet in same image

## What to EXCLUDE:
❌ Leg area above ankle
❌ Shadows on ground
❌ Reflections in mirrors
❌ Background objects

## Quality Standards:
- Mask edges must be precise
- No gaps in foot outline
- Include toe details
- Handle occlusions carefully

## File Naming:
- Keep original image name
- Save mask as: image_name.png
- Mask values: 0=background, 255=foot

## Submission:
1. Move completed images to 'completed/' folder
2. Save masks in 'masks/' folder
3. Update progress in progress.json
"""
        
        for member in self.team_members:
            with open(f"{self.output_dir}/{member}/INSTRUCTIONS.md", 'w') as f:
                f.write(instructions)
    
    def track_progress(self):
        """Track annotation progress for each member"""
        progress = {}
        for member in self.team_members:
            completed_dir = f"{self.output_dir}/{member}/completed"
            masks_dir = f"{self.output_dir}/{member}/masks"
            
            completed_images = len([f for f in os.listdir(completed_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
            completed_masks = len([f for f in os.listdir(masks_dir) if f.endswith('.png')])
            
            progress[member] = {
                'completed_images': completed_images,
                'completed_masks': completed_masks,
                'last_updated': datetime.now().isoformat()
            }
        
        with open(f"{self.output_dir}/progress.json", 'w') as f:
            json.dump(progress, f, indent=2)
        
        return progress

def setup_labelme_batch():
    """Create batch annotation script for LabelMe"""
    script = """#!/bin/bash
# Batch annotation with LabelMe
# Usage: ./annotate.sh

echo "Starting annotation session..."
echo "Instructions:"
echo "1. Draw polygon around foot+footwear"
echo "2. Label as 'foot_with_footwear'"
echo "3. Save and move to next image"
echo "4. Press Ctrl+C to exit"

labelme assigned/ --output masks/ --labels foot_with_footwear
"""
    
    with open('annotate.sh', 'w') as f:
        f.write(script)
    
    os.chmod('annotate.sh', 0o755)
    print("Created annotate.sh - Run this for batch annotation")

if __name__ == '__main__':
    # Setup collaborative annotation
    manager = CollaborativeAnnotationManager(
        images_dir='raw_images',
        output_dir='annotation_workspace',
        team_members=['member1', 'member2', 'member3']
    )
    
    manager.distribute_images()
    manager.create_annotation_instructions()
    setup_labelme_batch()
    
    print("\n✅ Annotation workspace created!")
    print("Next steps:")
    print("1. Each member goes to their folder")
    print("2. Run: pip install labelme")
    print("3. Run: ./annotate.sh")
    print("4. Check progress: python annotation_system.py --progress")