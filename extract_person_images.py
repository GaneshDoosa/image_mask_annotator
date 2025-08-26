import os
import shutil

def extract_person_images(source_dir, team_members=['member1', 'member2', 'member3']):
    """Extract images starting with 'person_' and distribute to team members"""
    
    # Find all person_ images recursively
    person_images = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.startswith('person_') and file.endswith(('.jpg', '.png', '.jpeg')):
                person_images.append(os.path.join(root, file))
    
    if not person_images:
        print("❌ No images starting with 'person_' found")
        return
    
    print(f"Found {len(person_images)} person images")
    
    # Create workspace structure
    for member in team_members:
        os.makedirs(f"annotation_workspace/{member}/assigned", exist_ok=True)
        os.makedirs(f"annotation_workspace/{member}/completed", exist_ok=True)
        os.makedirs(f"annotation_workspace/{member}/masks", exist_ok=True)
    
    # Distribute images equally
    images_per_member = len(person_images) // len(team_members)
    
    for i, member in enumerate(team_members):
        start_idx = i * images_per_member
        end_idx = start_idx + images_per_member if i < len(team_members) - 1 else len(person_images)
        
        member_images = person_images[start_idx:end_idx]
        
        # Copy images to member's assigned folder
        for img_path in member_images:
            img_name = os.path.basename(img_path)
            dst = f"annotation_workspace/{member}/assigned/{img_name}"
            shutil.copy2(img_path, dst)
        
        print(f"✅ {member}: {len(member_images)} images assigned")

if __name__ == '__main__':
    source_directory = input("Enter source directory path (or press Enter for 'raw_images'): ").strip()
    if not source_directory:
        source_directory = 'raw_images'
    
    if os.path.exists(source_directory):
        extract_person_images(source_directory)
        print("\n🎯 Person images distributed to team members!")
        print("Next: Each member runs 'labelme assigned/' in their folder")
    else:
        print(f"❌ Directory '{source_directory}' not found")