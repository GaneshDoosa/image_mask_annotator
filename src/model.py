import torch
import torch.nn as nn
import segmentation_models_pytorch as smp
from transformers import SamModel, SamProcessor

class FootSegmentationModel(nn.Module):
    def __init__(self, model_type='unet', encoder='resnet50', num_classes=2):
        super().__init__()
        self.model_type = model_type
        
        if model_type == 'unet':
            self.model = smp.Unet(
                encoder_name=encoder,
                encoder_weights='imagenet',
                classes=num_classes,
                activation=None
            )
        elif model_type == 'deeplabv3plus':
            self.model = smp.DeepLabV3Plus(
                encoder_name=encoder,
                encoder_weights='imagenet',
                classes=num_classes,
                activation=None
            )
        elif model_type == 'fpn':
            self.model = smp.FPN(
                encoder_name=encoder,
                encoder_weights='imagenet',
                classes=num_classes,
                activation=None
            )
    
    def forward(self, x):
        return self.model(x)

class SAMFootSegmentation:
    def __init__(self, model_name="facebook/sam-vit-base"):
        self.processor = SamProcessor.from_pretrained(model_name)
        self.model = SamModel.from_pretrained(model_name)
        
    def predict(self, image, input_points=None):
        inputs = self.processor(image, input_points=input_points, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        masks = self.processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu()
        )
        return masks[0]

def get_model(model_type='unet', encoder='resnet50', num_classes=2):
    return FootSegmentationModel(model_type, encoder, num_classes)