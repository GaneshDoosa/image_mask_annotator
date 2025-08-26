import torch
import cv2
import numpy as np
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
from model import get_model
from utils import postprocess_mask
import torch.nn.functional as F

class FootSegmentationInference:
    def __init__(self, model_path, model_type='unet', encoder='resnet50', img_size=512):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.img_size = img_size
        
        # Load model
        self.model = get_model(model_type, encoder, num_classes=2)
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        # Preprocessing transform
        self.transform = A.Compose([
            A.Resize(img_size, img_size),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    
    def preprocess_image(self, image):
        if isinstance(image, str):
            image = cv2.imread(image)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif isinstance(image, Image.Image):
            image = np.array(image)
        
        original_size = image.shape[:2]
        transformed = self.transform(image=image)
        image_tensor = transformed['image'].unsqueeze(0).to(self.device)
        
        return image_tensor, original_size
    
    def predict(self, image, return_confidence=False):
        image_tensor, original_size = self.preprocess_image(image)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            
            # Get foot mask (class 1)
            foot_mask = probabilities[0, 1].cpu().numpy()
            
            # Resize back to original size
            foot_mask = cv2.resize(foot_mask, (original_size[1], original_size[0]))
            
            # Post-process
            binary_mask = postprocess_mask(foot_mask)
            
            if return_confidence:
                return binary_mask, foot_mask
            return binary_mask
    
    def predict_batch(self, images):
        results = []
        for image in images:
            mask = self.predict(image)
            results.append(mask)
        return results

def main():
    # Example usage
    inference = FootSegmentationInference(
        model_path='../models/best_model.pth',
        model_type='unet',
        encoder='resnet50'
    )
    
    # Single image prediction
    image_path = 'path/to/your/image.jpg'
    mask = inference.predict(image_path)
    
    # Save result
    cv2.imwrite('foot_mask.png', mask * 255)
    print("Prediction saved as foot_mask.png")

if __name__ == '__main__':
    main()