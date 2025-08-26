import os
import glob

def debug_mask_counting(assigned_folder):
    """Debug mask counting issues"""
    
    # Determine masks folder
    if 'assigned' in assigned_folder:
        masks_folder = assigned_folder.replace('assigned', 'masks')
    else:
        masks_folder = os.path.join(os.path.dirname(assigned_folder), 'masks')
    
    print(f"🔍 DEBUGGING MASK COUNT")
    print(f"Assigned folder: {assigned_folder}")
    print(f"Masks folder: {masks_folder}")
    print()
    
    # Check assigned images
    assigned_images = glob.glob(os.path.join(assigned_folder, "*.jpg")) + \
                     glob.glob(os.path.join(assigned_folder, "*.png")) + \
                     glob.glob(os.path.join(assigned_folder, "*.jpeg"))
    
    print(f"📁 Assigned images ({len(assigned_images)}):")
    for img in assigned_images:
        print(f"   - {os.path.basename(img)}")
    print()
    
    # Check mask files
    if os.path.exists(masks_folder):
        mask_files = glob.glob(os.path.join(masks_folder, "*.png"))
        print(f"🎭 Mask files ({len(mask_files)}):")
        for mask in mask_files:
            size = os.path.getsize(mask)
            print(f"   - {os.path.basename(mask)} ({size} bytes)")
    else:
        print(f"❌ Masks folder doesn't exist: {masks_folder}")
    print()
    
    # Check matching
    completed_count = 0
    for img_path in assigned_images:
        img_name = os.path.splitext(os.path.basename(img_path))[0]
        mask_path = os.path.join(masks_folder, f"{img_name}.png")
        
        if os.path.exists(mask_path):
            completed_count += 1
            print(f"✅ {img_name}: Has mask")
        else:
            print(f"❌ {img_name}: No mask")
    
    print(f"\n📊 SUMMARY:")
    print(f"Total assigned: {len(assigned_images)}")
    print(f"Actual completed: {completed_count}")

if __name__ == '__main__':
    folder = input("Enter assigned folder path: ").strip()
    if folder and os.path.exists(folder):
        debug_mask_counting(folder)
    else:
        print("Invalid folder path")