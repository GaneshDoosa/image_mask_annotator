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

## Tool:
- Simple Brush Annotator (included in this project)

## Quick Setup:
1. Navigate to your assigned folder
2. Run: `python simple_brush_annotator.py`
3. Paint over foot+footwear areas
4. Save masks using 's' key

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
            assigned_dir = f"{self.output_dir}/{member}/assigned"
            masks_dir = f"{self.output_dir}/{member}/masks"
            
            # Count assigned images
            assigned_images = [f for f in os.listdir(assigned_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
            total_assigned = len(assigned_images)
            
            # Count completed masks (masks that match assigned images)
            completed_masks = 0
            for img in assigned_images:
                img_name = os.path.splitext(img)[0]
                mask_path = os.path.join(masks_dir, f"{img_name}.png")
                if os.path.exists(mask_path):
                    completed_masks += 1
            
            progress[member] = {
                'assigned': total_assigned,
                'completed': completed_masks,
                'remaining': total_assigned - completed_masks,
                'last_updated': datetime.now().isoformat()
            }
        
        with open(f"{self.output_dir}/progress.json", 'w') as f:
            json.dump(progress, f, indent=2)
        
        return progress



if __name__ == '__main__':
    import sys
    
    manager = CollaborativeAnnotationManager(
        images_dir='raw_images',
        output_dir='annotation_workspace',
        team_members=['member1', 'member2', 'member3']
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == '--progress':
        # Show progress
        progress = manager.track_progress()
        print("\n📊 Progress Report:")
        for member, stats in progress.items():
            print(f"  {member}: {stats['completed']}/{stats['assigned']} completed ({stats['remaining']} remaining)")
    else:
        # Setup workspace
        manager.distribute_images()
        manager.create_annotation_instructions()
        manager.track_progress()  # Create initial progress file
        
        print("\n✅ Annotation workspace created!")
        print("Next steps:")
        print("1. Each member goes to their assigned folder")
        print("2. Run: python simple_brush_annotator.py")
        print("3. Check progress: python annotation_system.py --progress")