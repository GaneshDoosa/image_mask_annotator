import os
import subprocess

def quick_setup():
    """One-click setup for annotation workflow"""
    
    print("🔧 Setting up annotation environment...")
    
    # Create essential folders
    folders = [
        'raw_images',
        'auto_masks', 
        'annotation_workspace',
        'merged_annotations',
        'final_dataset'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created {folder}/")
    
    print("\n📋 NEXT STEPS:")
    print("1. Put your images in 'raw_images/' folder")
    print("2. Run: python auto_masking.py")
    print("3. Run: python annotation_system.py") 
    print("4. Team annotates using LabelMe")
    print("5. Run: python merge_annotations.py")
    print("6. Run: python data_preparation.py")
    
    print("\n🛠️ INSTALL LABELME:")
    print("pip install labelme")
    
    print("\n👥 TEAM WORKFLOW:")
    print("Each member:")
    print("1. cd annotation_workspace/[member_name]/")
    print("2. labelme assigned/")
    print("3. Draw polygons around feet+footwear")
    print("4. Save as 'foot_with_footwear'")

if __name__ == '__main__':
    quick_setup()