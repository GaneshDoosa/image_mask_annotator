import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image

def dice_loss(pred, target, smooth=1e-6):
    pred = F.softmax(pred, dim=1)
    pred = pred[:, 1, :, :]  # Get foreground class
    target = target.float()
    
    intersection = (pred * target).sum(dim=(1, 2))
    union = pred.sum(dim=(1, 2)) + target.sum(dim=(1, 2))
    
    dice = (2. * intersection + smooth) / (union + smooth)
    return 1 - dice.mean()

def iou_score(pred, target, threshold=0.5):
    pred = F.softmax(pred, dim=1)
    pred = (pred[:, 1, :, :] > threshold).float()
    target = target.float()
    
    intersection = (pred * target).sum(dim=(1, 2))
    union = pred.sum(dim=(1, 2)) + target.sum(dim=(1, 2)) - intersection
    
    iou = (intersection + 1e-6) / (union + 1e-6)
    return iou.mean().item()

def save_checkpoint(model, optimizer, epoch, iou, filepath):
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'iou': iou,
    }, filepath)

def load_checkpoint(model, optimizer, filepath):
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    return checkpoint['epoch'], checkpoint['iou']

def visualize_prediction(image, mask, prediction, save_path=None):
    """Visualize original image, ground truth mask, and prediction"""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Original image
    if isinstance(image, torch.Tensor):
        image = image.permute(1, 2, 0).cpu().numpy()
        image = (image * np.array([0.229, 0.224, 0.225]) + np.array([0.485, 0.456, 0.406]))
        image = np.clip(image, 0, 1)
    
    axes[0].imshow(image)
    axes[0].set_title('Original Image')
    axes[0].axis('off')
    
    # Ground truth mask
    if isinstance(mask, torch.Tensor):
        mask = mask.cpu().numpy()
    axes[1].imshow(mask, cmap='gray')
    axes[1].set_title('Ground Truth')
    axes[1].axis('off')
    
    # Prediction
    if isinstance(prediction, torch.Tensor):
        prediction = F.softmax(prediction, dim=0)[1].cpu().numpy()
    axes[2].imshow(prediction, cmap='gray')
    axes[2].set_title('Prediction')
    axes[2].axis('off')
    
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def postprocess_mask(mask, min_area=1000):
    """Remove small connected components"""
    mask = (mask > 0.5).astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < min_area:
            cv2.fillPoly(mask, [contour], 0)
    
    return mask