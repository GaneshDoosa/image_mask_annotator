import os
import subprocess
import sys

def install_annotation_tools():
    """Install required annotation tools"""
    tools = [
        'labelme',
        'opencv-python',
        'mediapipe',
        'pillow'
    ]
    
    for tool in tools:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', tool])
            print(f"✅ Installed {tool}")
        except:
            print(f"❌ Failed to install {tool}")

def create_team_workflow():
    """Create complete workflow for 3-member team"""
    
    # Create folder structure
    folders = [
        'raw_images',
        'auto_masks', 
        'annotation_workspace',
        'final_dataset/train/images',
        'final_dataset/train/masks',
        'final_dataset/val/images', 
        'final_dataset/val/masks'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Create workflow script
    workflow = """#!/bin/bash
# Complete Annotation Workflow

echo "🚀 FOOT SEGMENTATION ANNOTATION WORKFLOW"
echo "========================================"

echo "Step 1: Auto-generate initial masks..."
python auto_masking.py

echo "Step 2: Setup team annotation..."
python annotation_system.py

echo "Step 3: Team members annotate assigned images"
echo "  - Each member runs: labelme annotation_workspace/[member_name]/assigned/"
echo "  - Save masks to: annotation_workspace/[member_name]/masks/"

echo "Step 4: Collect and merge results..."
python merge_annotations.py

echo "Step 5: Prepare final dataset..."
python data_preparation.py

echo "✅ Workflow complete! Ready for training."
"""
    
    with open('run_workflow.sh', 'w') as f:
        f.write(workflow)
    
    os.chmod('run_workflow.sh', 0o755)

def create_merge_script():
    """Create script to merge team annotations"""
    merge_code = '''
import os
import shutil
import json
from datetime import datetime

def merge_team_annotations():
    """Collect all completed annotations from team members"""
    
    team_members = ['member1', 'member2', 'member3']
    workspace = 'annotation_workspace'
    output_dir = 'merged_annotations'
    
    os.makedirs(f"{output_dir}/images", exist_ok=True)
    os.makedirs(f"{output_dir}/masks", exist_ok=True)
    
    stats = {'total_images': 0, 'total_masks': 0, 'members': {}}
    
    for member in team_members:
        member_images = f"{workspace}/{member}/completed"
        member_masks = f"{workspace}/{member}/masks"
        
        if not os.path.exists(member_images) or not os.path.exists(member_masks):
            continue
            
        images = [f for f in os.listdir(member_images) if f.endswith(('.jpg', '.png', '.jpeg'))]
        masks = [f for f in os.listdir(member_masks) if f.endswith('.png')]
        
        # Copy completed work
        for img in images:
            src = os.path.join(member_images, img)
            dst = os.path.join(output_dir, 'images', img)
            shutil.copy2(src, dst)
        
        for mask in masks:
            src = os.path.join(member_masks, mask)
            dst = os.path.join(output_dir, 'masks', mask)
            shutil.copy2(src, dst)
        
        stats['members'][member] = {'images': len(images), 'masks': len(masks)}
        stats['total_images'] += len(images)
        stats['total_masks'] += len(masks)
    
    stats['merge_date'] = datetime.now().isoformat()
    
    with open(f"{output_dir}/merge_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"✅ Merged annotations:")
    print(f"  Total images: {stats['total_images']}")
    print(f"  Total masks: {stats['total_masks']}")
    
    return stats

if __name__ == '__main__':
    merge_team_annotations()
'''
    
    with open('merge_annotations.py', 'w') as f:
        f.write(merge_code)

def main():
    print("🔧 Setting up annotation environment...")
    
    # Install tools
    install_annotation_tools()
    
    # Create workflow
    create_team_workflow()
    create_merge_script()
    
    print("\n✅ Setup complete!")
    print("\n📋 ANNOTATION WORKFLOW:")
    print("1. Put raw images in 'raw_images/' folder")
    print("2. Run: python auto_masking.py (generates initial masks)")
    print("3. Run: python annotation_system.py (distributes work)")
    print("4. Team members annotate using LabelMe")
    print("5. Run: python merge_annotations.py (collect results)")
    print("6. Run: python data_preparation.py (prepare training data)")
    
    print("\n👥 TEAM MEMBER INSTRUCTIONS:")
    print("1. Go to annotation_workspace/[your_name]/")
    print("2. Run: labelme assigned/")
    print("3. Draw polygons around feet+footwear")
    print("4. Label as 'foot_with_footwear'")
    print("5. Save masks to masks/ folder")

if __name__ == '__main__':
    main()