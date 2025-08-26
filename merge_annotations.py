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