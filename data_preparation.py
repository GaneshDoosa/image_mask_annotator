import os
import shutil
from sklearn.model_selection import train_test_split
import json

def prepare_data_structure(source_dir, target_dir, train_split=0.8):
    """
    Organize data into train/val splits with proper directory structure
    
    Expected source structure:
    source_dir/
    ├── images/
    │   ├── image1.jpg
    │   ├── image2.jpg
    │   └── ...
    └── masks/
        ├── image1.png
        ├── image2.png
        └── ...
    """
    
    # Create target directory structure
    os.makedirs(os.path.join(target_dir, 'train', 'images'), exist_ok=True)
    os.makedirs(os.path.join(target_dir, 'train', 'masks'), exist_ok=True)
    os.makedirs(os.path.join(target_dir, 'val', 'images'), exist_ok=True)
    os.makedirs(os.path.join(target_dir, 'val', 'masks'), exist_ok=True)
    
    # Get all image files
    image_dir = os.path.join(source_dir, 'images')
    mask_dir = os.path.join(source_dir, 'masks')
    
    images = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    # Filter images that have corresponding masks
    valid_images = []
    for img in images:
        mask_name = img.replace('.jpg', '.png').replace('.jpeg', '.png')
        if os.path.exists(os.path.join(mask_dir, mask_name)):
            valid_images.append(img)
    
    print(f"Found {len(valid_images)} valid image-mask pairs")
    
    # Split data
    train_images, val_images = train_test_split(
        valid_images, train_size=train_split, random_state=42
    )
    
    # Copy files to respective directories
    for split, image_list in [('train', train_images), ('val', val_images)]:
        for img in image_list:
            # Copy image
            src_img = os.path.join(image_dir, img)
            dst_img = os.path.join(target_dir, split, 'images', img)
            shutil.copy2(src_img, dst_img)
            
            # Copy mask
            mask_name = img.replace('.jpg', '.png').replace('.jpeg', '.png')
            src_mask = os.path.join(mask_dir, mask_name)
            dst_mask = os.path.join(target_dir, split, 'masks', mask_name)
            shutil.copy2(src_mask, dst_mask)
    
    # Save split information
    split_info = {
        'train_images': len(train_images),
        'val_images': len(val_images),
        'total_images': len(valid_images),
        'train_split': train_split
    }
    
    with open(os.path.join(target_dir, 'split_info.json'), 'w') as f:
        json.dump(split_info, f, indent=2)
    
    print(f"Data preparation completed:")
    print(f"  Train: {len(train_images)} images")
    print(f"  Val: {len(val_images)} images")
    print(f"  Split info saved to {os.path.join(target_dir, 'split_info.json')}")

def create_sample_annotation_guide():
    """Create annotation guidelines for labelers"""
    guide = """
# Foot + Footwear Segmentation Annotation Guidelines

## Objective
Create pixel-perfect masks for human feet including any worn footwear.

## What to Include in Masks:
1. **Bare feet** - Complete foot surface from toes to heel
2. **Feet with socks** - Include sock material as part of foot region
3. **Feet with footwear** - Include entire visible shoe/sandal/flip-flop surface
4. **Boots** - Include boot surface up to ankle, exclude leg portion above ankle

## What to Exclude:
1. **Leg area** - Exclude skin/clothing above ankle unless it's part of footwear
2. **Shadows** - Do not include foot shadows on ground
3. **Reflections** - Exclude mirror reflections of feet
4. **Background objects** - Exclude floor, rugs, or other objects

## Annotation Quality Standards:
1. **Precision** - Mask edges should be tight to foot/footwear outline
2. **Completeness** - Include all visible foot/footwear pixels
3. **Consistency** - Use same standards across all images
4. **Occlusion handling** - Include partially visible feet behind objects

## File Naming Convention:
- Images: `image_001.jpg`, `image_002.jpg`, etc.
- Masks: `image_001.png`, `image_002.png`, etc.
- Mask values: 0 = background, 255 = foot_with_footwear

## Common Scenarios:
1. **Side view feet** - Include full foot profile
2. **Top-down view** - Include entire foot surface visible from above
3. **Partial crops** - Include all visible foot portions in frame
4. **Multiple feet** - Create single mask including all feet in image
5. **Crossed feet** - Include both feet even when overlapping
"""
    
    with open('annotation_guidelines.md', 'w') as f:
        f.write(guide)
    
    print("Annotation guidelines saved to annotation_guidelines.md")

if __name__ == '__main__':
    # Example usage
    source_directory = 'raw_data'  # Your source data directory
    target_directory = 'data'      # Organized data directory
    
    # Prepare data structure
    if os.path.exists(source_directory):
        prepare_data_structure(source_directory, target_directory)
    else:
        print(f"Source directory {source_directory} not found.")
        print("Please organize your data as:")
        print("raw_data/")
        print("├── images/")
        print("│   ├── image1.jpg")
        print("│   └── ...")
        print("└── masks/")
        print("    ├── image1.png")
        print("    └── ...")
    
    # Create annotation guide
    create_sample_annotation_guide()