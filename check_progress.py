import os
import glob

def check_team_progress():
    """Check annotation progress for all team members"""
    
    team_members = ['member1', 'member2', 'member3']
    total_assigned = 0
    total_completed = 0
    
    print("🏃‍♂️ TEAM ANNOTATION PROGRESS")
    print("=" * 40)
    
    for member in team_members:
        assigned_dir = f"annotation_workspace/{member}/assigned"
        masks_dir = f"annotation_workspace/{member}/masks"
        
        if not os.path.exists(assigned_dir):
            print(f"❌ {member}: No assigned folder found")
            continue
        
        # Count assigned images
        assigned_images = len(glob.glob(f"{assigned_dir}/*.jpg") + 
                            glob.glob(f"{assigned_dir}/*.png") + 
                            glob.glob(f"{assigned_dir}/*.jpeg"))
        
        # Count completed masks
        completed_masks = len(glob.glob(f"{masks_dir}/*.png")) if os.path.exists(masks_dir) else 0
        
        progress_pct = (completed_masks / assigned_images * 100) if assigned_images > 0 else 0
        
        print(f"👤 {member}:")
        print(f"   Assigned: {assigned_images} images")
        print(f"   Completed: {completed_masks} masks")
        print(f"   Progress: {progress_pct:.1f}%")
        print(f"   Output: {masks_dir}/")
        print()
        
        total_assigned += assigned_images
        total_completed += completed_masks
    
    overall_progress = (total_completed / total_assigned * 100) if total_assigned > 0 else 0
    
    print("📊 OVERALL PROGRESS:")
    print(f"   Total assigned: {total_assigned}")
    print(f"   Total completed: {total_completed}")
    print(f"   Overall progress: {overall_progress:.1f}%")
    
    if overall_progress == 100:
        print("🎉 ALL ANNOTATION COMPLETED!")
        print("Next step: Run 'python merge_annotations.py'")

if __name__ == '__main__':
    check_team_progress()