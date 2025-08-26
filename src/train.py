import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
from tqdm import tqdm
import wandb
import os
from dataset import FootSegmentationDataset, get_transforms
from model import get_model
from utils import dice_loss, iou_score, save_checkpoint

class FootSegmentationTrainer:
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model
        self.model = get_model(
            model_type=config['model_type'],
            encoder=config['encoder'],
            num_classes=config['num_classes']
        ).to(self.device)
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        self.dice_loss = dice_loss
        
        # Optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=config['learning_rate'],
            weight_decay=config['weight_decay']
        )
        
        # Scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=config['epochs']
        )
        
        # Data loaders
        self.train_loader = self._get_dataloader('train')
        self.val_loader = self._get_dataloader('val')
        
        # Initialize wandb
        if config['use_wandb']:
            wandb.init(project="foot-segmentation", config=config)
    
    def _get_dataloader(self, split):
        dataset = FootSegmentationDataset(
            image_dir=os.path.join(self.config['data_dir'], split, 'images'),
            mask_dir=os.path.join(self.config['data_dir'], split, 'masks'),
            transform=get_transforms(
                img_size=self.config['img_size'],
                is_train=(split == 'train')
            )
        )
        
        return DataLoader(
            dataset,
            batch_size=self.config['batch_size'],
            shuffle=(split == 'train'),
            num_workers=self.config['num_workers'],
            pin_memory=True
        )
    
    def train_epoch(self):
        self.model.train()
        total_loss = 0
        total_iou = 0
        
        pbar = tqdm(self.train_loader, desc='Training')
        for batch_idx, (images, masks) in enumerate(pbar):
            images, masks = images.to(self.device), masks.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(images)
            
            # Combined loss
            ce_loss = self.criterion(outputs, masks)
            d_loss = self.dice_loss(outputs, masks)
            loss = ce_loss + d_loss
            
            loss.backward()
            self.optimizer.step()
            
            # Metrics
            iou = iou_score(outputs, masks)
            total_loss += loss.item()
            total_iou += iou
            
            pbar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'IoU': f'{iou:.4f}'
            })
        
        return total_loss / len(self.train_loader), total_iou / len(self.train_loader)
    
    def validate(self):
        self.model.eval()
        total_loss = 0
        total_iou = 0
        
        with torch.no_grad():
            for images, masks in tqdm(self.val_loader, desc='Validation'):
                images, masks = images.to(self.device), masks.to(self.device)
                outputs = self.model(images)
                
                ce_loss = self.criterion(outputs, masks)
                d_loss = self.dice_loss(outputs, masks)
                loss = ce_loss + d_loss
                
                iou = iou_score(outputs, masks)
                total_loss += loss.item()
                total_iou += iou
        
        return total_loss / len(self.val_loader), total_iou / len(self.val_loader)
    
    def train(self):
        best_iou = 0
        
        for epoch in range(self.config['epochs']):
            print(f'Epoch {epoch+1}/{self.config["epochs"]}')
            
            train_loss, train_iou = self.train_epoch()
            val_loss, val_iou = self.validate()
            
            self.scheduler.step()
            
            print(f'Train Loss: {train_loss:.4f}, Train IoU: {train_iou:.4f}')
            print(f'Val Loss: {val_loss:.4f}, Val IoU: {val_iou:.4f}')
            
            if self.config['use_wandb']:
                wandb.log({
                    'epoch': epoch,
                    'train_loss': train_loss,
                    'train_iou': train_iou,
                    'val_loss': val_loss,
                    'val_iou': val_iou,
                    'lr': self.optimizer.param_groups[0]['lr']
                })
            
            # Save best model
            if val_iou > best_iou:
                best_iou = val_iou
                save_checkpoint(
                    self.model, self.optimizer, epoch, val_iou,
                    os.path.join(self.config['save_dir'], 'best_model.pth')
                )
        
        print(f'Training completed. Best IoU: {best_iou:.4f}')

if __name__ == '__main__':
    config = {
        'model_type': 'unet',
        'encoder': 'resnet50',
        'num_classes': 2,
        'img_size': 512,
        'batch_size': 8,
        'learning_rate': 1e-4,
        'weight_decay': 1e-4,
        'epochs': 100,
        'num_workers': 4,
        'data_dir': '../data',
        'save_dir': '../models',
        'use_wandb': True
    }
    
    trainer = FootSegmentationTrainer(config)
    trainer.train()