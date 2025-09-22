"""
MONAI Model Inference Pipeline
Loads trained models and generates segmentation masks
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from pathlib import Path

# Try to import MONAI
try:
    import monai
    from monai.inferers import sliding_window_inference
    from monai.transforms import (
        Compose, LoadImaged, AddChanneld, Spacingd, Orientationd,
        ScaleIntensityRanged, CropForegroundd, ToTensord
    )
    from monai.networks.nets import UNet
    from monai.data import DataLoader, Dataset
    MONAI_AVAILABLE = True
except ImportError:
    MONAI_AVAILABLE = False
    logging.warning("MONAI not available")

# Try to import PyTorch
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available")

logger = logging.getLogger(__name__)

class MONAIInferencePipeline:
    """MONAI-based inference pipeline for medical image segmentation"""
    
    def __init__(self, models_path: str = "./models/monai"):
        self.models_path = Path(models_path)
        self.models = {}
        self.transforms = {}
        self.device = self._setup_device()
        
        # Load available models
        self._load_models()
    
    def _setup_device(self) -> str:
        """Setup inference device (GPU/CPU)"""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            device = "cuda"
            logger.info("Using CUDA device for inference")
        else:
            device = "cpu"
            logger.info("Using CPU device for inference")
        return device
    
    def _load_models(self):
        """Load available MONAI models"""
        if not MONAI_AVAILABLE:
            logger.error("MONAI not available, cannot load models")
            return
        
        try:
            # Look for model configuration files
            model_configs = list(self.models_path.glob("*/model_config.json"))
            
            for config_path in model_configs:
                with open(config_path, "r") as f:
                    config = json.load(f)
                
                model_name = config.get("model_name", config_path.parent.name)
                model_path = config_path.parent / "model.pth"
                
                if model_path.exists():
                    self._load_single_model(model_name, model_path, config)
                else:
                    logger.warning(f"Model file not found: {model_path}")
                    
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    def _load_single_model(self, model_name: str, model_path: Path, config: Dict[str, Any]):
        """Load a single MONAI model"""
        try:
            # Create model architecture
            model = self._create_model_architecture(config)
            
            # Load trained weights
            if TORCH_AVAILABLE:
                checkpoint = torch.load(model_path, map_location=self.device)
                if "model_state_dict" in checkpoint:
                    model.load_state_dict(checkpoint["model_state_dict"])
                else:
                    model.load_state_dict(checkpoint)
                
                model.to(self.device)
                model.eval()
            
            # Store model and configuration
            self.models[model_name] = {
                "model": model,
                "config": config,
                "path": str(model_path)
            }
            
            # Create transforms
            self.transforms[model_name] = self._create_transforms(config)
            
            logger.info(f"Loaded model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
    
    def _create_model_architecture(self, config: Dict[str, Any]) -> Any:
        """Create model architecture based on configuration"""
        model_type = config.get("model_type", "unet")
        
        if model_type == "unet":
            spatial_dims = config.get("spatial_dims", 3)
            in_channels = config.get("in_channels", 1)
            out_channels = config.get("out_channels", 1)
            features = config.get("features", [32, 64, 128, 256, 512])
            
            model = UNet(
                spatial_dims=spatial_dims,
                in_channels=in_channels,
                out_channels=out_channels,
                features=features,
                dropout=config.get("dropout", 0.1)
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        return model
    
    def _create_transforms(self, config: Dict[str, Any]) -> Any:
        """Create preprocessing transforms based on configuration"""
        transforms_list = [
            LoadImaged(keys=["image"]),
            AddChanneld(keys=["image"]),
            Spacingd(
                keys=["image"],
                pixdim=config.get("target_spacing", [1.0, 1.0, 1.0]),
                mode=("bilinear")
            ),
            Orientationd(keys=["image"], axcodes="RAS"),
            ScaleIntensityRanged(
                keys=["image"],
                a_min=config.get("intensity_range", [-1000, 1000])[0],
                a_max=config.get("intensity_range", [-1000, 1000])[1],
                b_min=0.0,
                b_max=1.0,
                clip=True
            ),
            CropForegroundd(keys=["image"], source_key="image"),
            ToTensord(keys=["image"])
        ]
        
        return Compose(transforms_list)
    
    def list_available_models(self) -> List[str]:
        """List available models"""
        return list(self.models.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        if model_name not in self.models:
            return None
        
        model_info = self.models[model_name].copy()
        # Remove the actual model object for serialization
        if "model" in model_info:
            del model_info["model"]
        return model_info
    
    def run_inference(
        self, 
        image_path: str, 
        model_name: str,
        output_path: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """Run inference on an image"""
        if not MONAI_AVAILABLE:
            return {"success": False, "error": "MONAI not available"}
        
        if model_name not in self.models:
            return {"success": False, "error": f"Model {model_name} not found"}
        
        try:
            # Load and preprocess image
            data_dict = {"image": image_path}
            processed_data = self.transforms[model_name](data_dict)
            
            # Prepare input tensor
            input_tensor = processed_data["image"].unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                output = self.models[model_name]["model"](input_tensor)
                
                if output.shape[1] > 1:  # Multi-class
                    output = torch.softmax(output, dim=1)
                    # Take the first class (background) and second class (foreground)
                    mask = output[:, 1:2, ...]  # Foreground class
                else:  # Binary
                    mask = torch.sigmoid(output)
                
                # Apply confidence threshold
                mask = (mask > confidence_threshold).float()
            
            # Convert to numpy
            mask_np = mask.squeeze().cpu().numpy()
            
            # Save mask
            if output_path is None:
                output_path = str(Path(image_path).parent / "segmentation_mask.nii.gz")
            
            self._save_mask(mask_np, output_path, processed_data)
            
            # Calculate metrics
            metrics = self._calculate_segmentation_metrics(mask_np)
            
            return {
                "success": True,
                "mask_path": output_path,
                "confidence": float(torch.max(output).item()),
                "mask_shape": mask_np.shape,
                "metrics": metrics,
                "model_name": model_name
            }
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_mask(self, mask: np.ndarray, output_path: str, processed_data: Dict[str, Any]):
        """Save segmentation mask as NIfTI file"""
        try:
            # Convert to SimpleITK image
            import SimpleITK as sitk
            
            # Create image from array
            sitk_image = sitk.GetImageFromArray(mask)
            
            # Set metadata from processed data
            if "image_meta_dict" in processed_data:
                meta = processed_data["image_meta_dict"]
                if "spacing" in meta:
                    sitk_image.SetSpacing(meta["spacing"])
                if "origin" in meta:
                    sitk_image.SetOrigin(meta["origin"])
                if "direction" in meta:
                    sitk_image.SetDirection(meta["direction"])
            
            # Save as NIfTI
            sitk.WriteImage(sitk_image, output_path)
            logger.info(f"Saved mask to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save mask: {e}")
            raise
    
    def _calculate_segmentation_metrics(self, mask: np.ndarray) -> Dict[str, float]:
        """Calculate basic segmentation metrics"""
        try:
            # Volume (voxel count)
            volume_voxels = np.sum(mask > 0)
            
            # Surface area (approximate)
            surface_area = self._calculate_surface_area(mask)
            
            # Bounding box
            bbox = self._calculate_bounding_box(mask)
            
            return {
                "volume_voxels": int(volume_voxels),
                "surface_area_voxels": float(surface_area),
                "bounding_box": bbox
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            return {}
    
    def _calculate_surface_area(self, mask: np.ndarray) -> float:
        """Calculate approximate surface area of segmentation"""
        try:
            from scipy import ndimage
            
            # Erode and dilate to find boundary
            eroded = ndimage.binary_erosion(mask)
            dilated = ndimage.binary_dilation(mask)
            boundary = dilated & ~eroded
            
            return float(np.sum(boundary))
            
        except ImportError:
            logger.warning("scipy not available, using simple boundary calculation")
            # Simple boundary calculation
            boundary = np.zeros_like(mask)
            for i in range(1, mask.shape[0]-1):
                for j in range(1, mask.shape[1]-1):
                    for k in range(1, mask.shape[2]-1):
                        if mask[i,j,k] > 0:
                            if (mask[i-1,j,k] == 0 or mask[i+1,j,k] == 0 or
                                mask[i,j-1,k] == 0 or mask[i,j+1,k] == 0 or
                                mask[i,j,k-1] == 0 or mask[i,j,k+1] == 0):
                                boundary[i,j,k] = 1
            
            return float(np.sum(boundary))
    
    def _calculate_bounding_box(self, mask: np.ndarray) -> Dict[str, List[int]]:
        """Calculate bounding box of segmentation"""
        try:
            # Find non-zero indices
            indices = np.where(mask > 0)
            
            if len(indices[0]) == 0:
                return {"min": [0, 0, 0], "max": [0, 0, 0]}
            
            min_coords = [int(np.min(indices[i])) for i in range(3)]
            max_coords = [int(np.max(indices[i])) for i in range(3)]
            
            return {
                "min": min_coords,
                "max": max_coords,
                "size": [max_coords[i] - min_coords[i] + 1 for i in range(3)]
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate bounding box: {e}")
            return {"min": [0, 0, 0], "max": [0, 0, 0]}

def create_monai_pipeline(models_path: str = "./models/monai") -> MONAIInferencePipeline:
    """Factory function to create MONAI inference pipeline"""
    return MONAIInferencePipeline(models_path)

def run_segmentation_pipeline(
    image_path: str,
    model_name: str,
    models_path: str = "./models/monai",
    output_dir: Optional[str] = None,
    confidence_threshold: float = 0.5
) -> Dict[str, Any]:
    """Complete segmentation pipeline"""
    pipeline_result = {
        "success": False,
        "outputs": {},
        "processing_time": 0.0,
        "errors": []
    }
    
    import time
    start_time = time.time()
    
    try:
        # Create pipeline
        pipeline = create_monai_pipeline(models_path)
        
        # Check if model is available
        if model_name not in pipeline.list_available_models():
            pipeline_result["errors"].append(f"Model {model_name} not found")
            return pipeline_result
        
        # Set output path
        if output_dir is None:
            output_dir = str(Path(image_path).parent)
        
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"segmentation_{model_name}.nii.gz")
        
        # Run inference
        result = pipeline.run_inference(
            image_path, 
            model_name, 
            output_path, 
            confidence_threshold
        )
        
        if result["success"]:
            pipeline_result["success"] = True
            pipeline_result["outputs"] = {
                "mask": result["mask_path"],
                "metrics": result["metrics"],
                "confidence": result["confidence"]
            }
        else:
            pipeline_result["errors"].append(result["error"])
        
    except Exception as e:
        pipeline_result["errors"].append(f"Pipeline failed: {e}")
    
    finally:
        pipeline_result["processing_time"] = time.time() - start_time
    
    return pipeline_result
