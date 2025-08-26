# Foot + Footwear Segmentation Model

A robust semantic segmentation model for detecting and segmenting human feet with any worn footwear in various image conditions.

## Features

- **Multi-architecture support**: U-Net, DeepLabV3+, FPN
- **Robust augmentations**: Handles partial crops, lighting variations, occlusions
- **Single class segmentation**: `foot_with_footwear` (includes bare feet, socks, shoes, sandals, etc.)
- **Real-world optimized**: Works with mobile photos, mirror selfies, cropped images
- **Easy inference**: Simple API for deployment

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Data Preparation
Organize your data:
```
raw_data/
├── images/
│   ├── image1.jpg
│   └── ...
└── masks/
    ├── image1.png  # Binary masks: 0=background, 255=foot_with_footwear
    └── ...
```

Run data preparation:
```bash
python data_preparation.py
```

### 3. Training
```bash
cd src
python train.py
```

### 4. Inference
```python
from src.inference import FootSegmentationInference

# Load model
inference = FootSegmentationInference('models/best_model.pth')

# Predict on image
mask = inference.predict('path/to/image.jpg')
```

## Model Architectures

### U-Net (Recommended)
- **Best for**: General foot segmentation
- **Encoder**: ResNet50, EfficientNet-B4
- **Memory**: Moderate
- **Speed**: Fast

### DeepLabV3+
- **Best for**: High-precision boundaries
- **Encoder**: ResNet50, ResNet101
- **Memory**: High
- **Speed**: Moderate

### FPN
- **Best for**: Multi-scale feet detection
- **Encoder**: ResNet50, EfficientNet
- **Memory**: Low
- **Speed**: Very fast

## Training Configuration

Key parameters in `configs/config.yaml`:

```yaml
model:
  type: 'unet'
  encoder: 'resnet50'
  
training:
  img_size: 512
  batch_size: 8
  learning_rate: 1e-4
  epochs: 100
```

## Data Augmentation Strategy

The model uses aggressive augmentations to handle real-world scenarios:

- **Cropping**: Simulates partial body images
- **Lighting**: Brightness/contrast variations
- **Color**: Footwear color/texture changes
- **Noise**: Handles low-quality mobile photos
- **Geometric**: Rotation, scaling for different poses

## Labeling Guidelines

### Include in Masks:
✅ Bare feet (complete surface)  
✅ Feet with socks  
✅ Any footwear (shoes, sandals, flip-flops, boots)  
✅ Partially visible feet  

### Exclude from Masks:
❌ Leg area above ankle  
❌ Shadows on ground  
❌ Reflections  
❌ Background objects  

## Performance Metrics

- **IoU (Intersection over Union)**: Primary metric
- **Dice Score**: Segmentation quality
- **Pixel Accuracy**: Overall correctness

## Model Deployment

### Batch Processing
```python
inference = FootSegmentationInference('models/best_model.pth')
masks = inference.predict_batch(image_list)
```

### Real-time Processing
```python
# Optimized for speed
inference = FootSegmentationInference(
    'models/best_model.pth',
    model_type='fpn',  # Fastest architecture
    img_size=256       # Smaller input size
)
```

## Common Use Cases

1. **Mobile foot scanning apps**
2. **Virtual shoe try-on**
3. **Foot measurement applications**
4. **Medical foot analysis**
5. **Fashion e-commerce**

## Troubleshooting

### Low IoU scores:
- Increase training epochs
- Use stronger augmentations
- Check mask quality
- Try different encoder

### Slow inference:
- Use FPN architecture
- Reduce input image size
- Use lighter encoder (EfficientNet-B0)

### Memory issues:
- Reduce batch size
- Use gradient checkpointing
- Smaller input resolution

## File Structure

```
foot_segmentation/
├── src/
│   ├── dataset.py      # Data loading and augmentation
│   ├── model.py        # Model architectures
│   ├── train.py        # Training script
│   ├── inference.py    # Inference API
│   └── utils.py        # Helper functions
├── configs/
│   └── config.yaml     # Training configuration
├── data/               # Organized dataset
├── models/             # Saved checkpoints
├── data_preparation.py # Data organization script
└── requirements.txt    # Dependencies
```

## License

MIT License - Feel free to use for commercial and research purposes.