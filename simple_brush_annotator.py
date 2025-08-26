import cv2
import numpy as np
import os
import glob

class FootBrushAnnotator:
    def __init__(self, image_folder):
        self.image_folder = os.path.abspath(image_folder)
        
        # Create masks folder in same parent directory as assigned folder
        if 'assigned' in self.image_folder:
            self.masks_folder = self.image_folder.replace('assigned', 'masks')
        else:
            # If not in assigned folder, create masks folder alongside
            self.masks_folder = os.path.join(os.path.dirname(self.image_folder), 'masks')
        
        os.makedirs(self.masks_folder, exist_ok=True)
        print(f"📁 Images from: {self.image_folder}")
        print(f"💾 Masks will be saved to: {self.masks_folder}")
        self.brush_size = 15
        self.drawing = False
        self.erase_mode = False  # Toggle between paint and erase
        self.mask = None
        self.image = None
        self.current_image_path = None
        self.mouse_x, self.mouse_y = 0, 0  # Track mouse position
        
    def mouse_callback(self, event, x, y, flags, param):
        # Always update mouse position for cursor
        self.mouse_x, self.mouse_y = x, y
        
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            color = 0 if self.erase_mode else 255  # 0 = erase, 255 = paint
            cv2.circle(self.mask, (x, y), self.brush_size, color, -1)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            color = 0 if self.erase_mode else 255
            cv2.circle(self.mask, (x, y), self.brush_size, color, -1)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
        elif event == cv2.EVENT_RBUTTONDOWN:  # Right click to erase (always)
            cv2.circle(self.mask, (x, y), self.brush_size, 0, -1)
    
    def get_completed_masks(self):
        """Get list of already completed mask files"""
        mask_files = glob.glob(os.path.join(self.masks_folder, "*.png"))
        print(f"\n🔍 All .png files in masks folder ({len(mask_files)}):")
        for mask_file in mask_files:
            size = os.path.getsize(mask_file)
            print(f"   - {os.path.basename(mask_file)} ({size} bytes)")
        
        # Also check assigned folder contents
        assigned_files = glob.glob(os.path.join(self.image_folder, "*"))
        jpg_count = len([f for f in assigned_files if f.endswith('.jpg')])
        png_count = len([f for f in assigned_files if f.endswith('.png')])
        jpeg_count = len([f for f in assigned_files if f.endswith('.jpeg')])
        print(f"\n📁 Assigned folder contents: {jpg_count} .jpg, {png_count} .png, {jpeg_count} .jpeg")
        
        return mask_files
    
    def annotate_images(self):
        # Only get actual image files, not mask files
        images = glob.glob(os.path.join(self.image_folder, "*.jpg")) + \
                glob.glob(os.path.join(self.image_folder, "*.jpeg"))
        
        # Only add .png files if they don't have corresponding masks (to avoid confusion)
        png_files = glob.glob(os.path.join(self.image_folder, "*.png"))
        for png_file in png_files:
            img_name = os.path.splitext(os.path.basename(png_file))[0]
            mask_path = os.path.join(self.masks_folder, f"{img_name}.png")
            if not os.path.exists(mask_path):  # Only include if no mask exists
                images.append(png_file)
        
        if not images:
            print("No images found!")
            return
        
        # Check progress - only count masks that match assigned images
        remaining_images = []
        completed_images = []
        
        print(f"\n🔍 Checking which images have masks...")
        processed_names = set()  # Track processed image names to avoid duplicates
        
        for img_path in images:
            img_name = os.path.splitext(os.path.basename(img_path))[0]
            
            # Skip if we already processed this image name
            if img_name in processed_names:
                continue
            processed_names.add(img_name)
            
            mask_path = os.path.join(self.masks_folder, f"{img_name}.png")
            
            if os.path.exists(mask_path):
                completed_images.append(img_path)
                print(f"✅ {img_name} -> has mask")
            else:
                remaining_images.append(img_path)
        
        total_images = len(images)
        completed_count = len(completed_images)
        
        print(f"\n📋 Found {completed_count} completed masks:")
        for img_path in completed_images:
            print(f"   - {os.path.basename(img_path)}")
        
        print(f"\n📁 Total unique image names: {len(processed_names)}")
        
        print(f"\n📊 PROGRESS SUMMARY:")
        print(f"Total images: {total_images}")
        print(f"Completed: {completed_count}")
        print(f"Remaining: {len(remaining_images)}")
        print(f"Output folder: {self.masks_folder}")
        
        # Ask user what to do
        if completed_count > 0 and len(remaining_images) > 0:
            choice = input("\n🔄 Options: (1) Edit completed masks (2) Continue with remaining (3) All images: ").strip()
            if choice == '1':
                images = completed_images
                print("📝 Editing completed masks...")
            elif choice == '2':
                images = remaining_images
                print("▶️ Continuing with remaining images...")
            elif choice == '3':
                images = images  # All images
                print("🔄 Processing all images...")
            else:
                images = remaining_images
        elif completed_count > 0:
            choice = input("\n🎉 All completed! Edit existing masks? (y/n): ").strip().lower()
            if choice == 'y':
                images = completed_images
            else:
                return
        else:
            images = remaining_images
        
        cv2.namedWindow('Foot Brush Annotator', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Foot Brush Annotator', self.mouse_callback)
        
        # Hide default cursor and use custom one
        # cv2.setWindowProperty('Foot Brush Annotator', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        i = 0
        while i < len(images):
            img_path = images[i]
            self.current_image_path = img_path
            self.image = cv2.imread(img_path)
            
            # Load existing mask if it exists
            img_name = os.path.splitext(os.path.basename(img_path))[0]
            existing_mask_path = os.path.join(self.masks_folder, f"{img_name}.png")
            
            if os.path.exists(existing_mask_path):
                self.mask = cv2.imread(existing_mask_path, cv2.IMREAD_GRAYSCALE)
                print(f"📝 Loaded existing mask: {existing_mask_path}")
            else:
                self.mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
            
            print(f"\nImage {i+1}/{len(images)}: {os.path.basename(img_path)}")
            print("Controls:")
            print("- Left click + drag: Paint/Erase (depends on mode)")
            print("- Right click + drag: Always erase")
            print("- 'e': Toggle erase mode")
            print("- '+'/'-': Change brush size")
            print("- 's': Save mask")
            print("- 'n': Next image (skip)")
            print("- 'p': Previous image")
            print("- 'c': Clear mask")
            print("- 'r': Reset to original (if exists)")
            print("- 'q': Quit")
            
            while True:
                # Create overlay
                overlay = cv2.addWeighted(self.image, 0.7, 
                                        cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR), 0.3, 0)
                
                # Draw custom round cursor
                cursor_color = (0, 0, 255) if self.erase_mode else (0, 255, 0)  # Red for erase, Green for paint
                cv2.circle(overlay, (self.mouse_x, self.mouse_y), self.brush_size, cursor_color, 2)
                cv2.circle(overlay, (self.mouse_x, self.mouse_y), 2, cursor_color, -1)  # Center dot
                
                # Show brush size and mode
                mode_text = "ERASE" if self.erase_mode else "PAINT"
                mode_color = (0, 0, 255) if self.erase_mode else (0, 255, 0)
                cv2.putText(overlay, f"Brush: {self.brush_size} ({mode_text})", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, mode_color, 2)
                
                # Show if editing existing mask
                if os.path.exists(existing_mask_path):
                    cv2.putText(overlay, "EDITING", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                
                cv2.imshow('Foot Brush Annotator', overlay)
                
                key = cv2.waitKey(30) & 0xFF  # Faster refresh for smooth cursor
                if key == ord('s'):  # Save
                    img_name = os.path.splitext(os.path.basename(img_path))[0]
                    mask_path = os.path.join(self.masks_folder, f"{img_name}.png")
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(mask_path), exist_ok=True)
                    
                    success = cv2.imwrite(mask_path, self.mask)
                    if success:
                        print(f"✅ Saved: {mask_path}")
                        # Verify file exists
                        if os.path.exists(mask_path):
                            print(f"✅ Verified: File exists ({os.path.getsize(mask_path)} bytes)")
                        else:
                            print(f"❌ Error: File not found after save!")
                    else:
                        print(f"❌ Error: Failed to save {mask_path}")
                    
                    # Update progress
                    remaining = len(images) - (i + 1)
                    print(f"📈 Progress: {i+1}/{len(images)} completed, {remaining} remaining")
                    i += 1  # Move to next image
                    break
                elif key == ord('n'):  # Next
                    i += 1  # Move to next image
                    break
                elif key == ord('p'):  # Previous
                    if i > 0:
                        i -= 1  # Go back to previous image
                        break
                    else:
                        print("⚠️ Already at first image")
                elif key == ord('c'):  # Clear
                    self.mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
                    print("🗑️ Mask cleared")
                elif key == ord('r'):  # Reset to original
                    if os.path.exists(existing_mask_path):
                        self.mask = cv2.imread(existing_mask_path, cv2.IMREAD_GRAYSCALE)
                        print("↩️ Reset to original mask")
                    else:
                        print("❌ No original mask to reset to")
                elif key == ord('+') or key == ord('='):  # Increase brush
                    self.brush_size = min(50, self.brush_size + 2)
                elif key == ord('-'):  # Decrease brush
                    self.brush_size = max(5, self.brush_size - 2)
                elif key == ord('e'):  # Toggle erase mode
                    self.erase_mode = not self.erase_mode
                    mode_text = "ERASE" if self.erase_mode else "PAINT"
                    print(f"🖌️ Switched to {mode_text} mode")
                elif key == ord('q'):  # Quit
                    cv2.destroyAllWindows()
                    return
            
            # Continue to next iteration of while loop
        
        cv2.destroyAllWindows()
        print("✅ All images processed!")

if __name__ == '__main__':
    folder = input("Enter folder path with images (or press Enter for current directory): ").strip()
    if not folder:
        folder = "."
    
    annotator = FootBrushAnnotator(folder)
    annotator.annotate_images()