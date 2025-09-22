"""
PyRadiomics Feature Extraction Pipeline
SUVmax/MTV/TLG + texture features extraction
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from pathlib import Path

# Try to import PyRadiomics
try:
    import radiomics
    from radiomics import featureextractor, getTestCase
    RADIOMICS_AVAILABLE = True
except ImportError:
    RADIOMICS_AVAILABLE = False
    logging.warning("PyRadiomics not available")

# Try to import SimpleITK
try:
    import SimpleITK as sitk
    SIMPLEITK_AVAILABLE = True
except ImportError:
    SIMPLEITK_AVAILABLE = False
    logging.warning("SimpleITK not available")

logger = logging.getLogger(__name__)

class RadiomicsExtractor:
    """PyRadiomics-based feature extraction for PET/CT images"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.extractor = None
        self.config = self._load_config(config_path)
        self._setup_extractor()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load PyRadiomics configuration"""
        default_config = {
            "binWidth": 25,
            "resampledPixelSpacing": [2, 2, 2],
            "interpolator": "sitkBSpline",
            "label": 1,
            "enableCExtensions": True,
            "force2D": False,
            "force2Ddimension": 0,
            "normalize": True,
            "normalizeScale": 100,
            "removeOutliers": 3,
            "resegmentRange": [-1000, 1000],
            "minimumROIDimensions": 2,
            "minimumROISize": 10,
            "additionalInfo": True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    custom_config = json.load(f)
                default_config.update(custom_config)
                logger.info(f"Loaded custom config from: {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom config: {e}")
        
        return default_config
    
    def _setup_extractor(self):
        """Setup PyRadiomics feature extractor"""
        if not RADIOMICS_AVAILABLE:
            logger.error("PyRadiomics not available")
            return
        
        try:
            self.extractor = featureextractor.RadiomicsFeatureExtractor(**self.config)
            logger.info("PyRadiomics feature extractor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PyRadiomics extractor: {e}")
    
    def extract_features(
        self, 
        image_path: str, 
        mask_path: str,
        feature_classes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extract radiomics features from image and mask"""
        if not RADIOMICS_AVAILABLE or self.extractor is None:
            return {"success": False, "error": "PyRadiomics not available"}
        
        if not SIMPLEITK_AVAILABLE:
            return {"success": False, "error": "SimpleITK not available"}
        
        try:
            # Load image and mask
            image = sitk.ReadImage(image_path)
            mask = sitk.ReadImage(mask_path)
            
            # Validate inputs
            if not self._validate_inputs(image, mask):
                return {"success": False, "error": "Invalid image or mask"}
            
            # Extract features
            features = self.extractor.execute(image, mask)
            
            # Filter feature classes if specified
            if feature_classes:
                filtered_features = {}
                for feature_name, feature_value in features.items():
                    for class_name in feature_classes:
                        if class_name in feature_name:
                            filtered_features[feature_name] = feature_value
                            break
                features = filtered_features
            
            # Organize features by class
            organized_features = self._organize_features(features)
            
            # Calculate SUV metrics
            suv_metrics = self._calculate_suv_metrics(image, mask)
            
            # Combine all results
            result = {
                "success": True,
                "radiomics_features": organized_features,
                "suv_metrics": suv_metrics,
                "image_info": self._get_image_info(image),
                "mask_info": self._get_mask_info(mask)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_inputs(self, image: sitk.Image, mask: sitk.Image) -> bool:
        """Validate image and mask inputs"""
        try:
            # Check image dimensions
            image_size = image.GetSize()
            mask_size = mask.GetSize()
            
            if image_size != mask_size:
                logger.error(f"Image and mask size mismatch: {image_size} vs {mask_size}")
                return False
            
            # Check for empty mask
            mask_array = sitk.GetArrayFromImage(mask)
            if np.sum(mask_array > 0) == 0:
                logger.error("Mask is empty")
                return False
            
            # Check image spacing
            image_spacing = image.GetSpacing()
            if any(s <= 0 for s in image_spacing):
                logger.error(f"Invalid image spacing: {image_spacing}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return False
    
    def _organize_features(self, features: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Organize features by class"""
        organized = {
            "firstorder": {},
            "shape": {},
            "glcm": {},
            "glrlm": {},
            "glszm": {},
            "ngtdm": {},
            "gldm": {}
        }
        
        for feature_name, feature_value in features.items():
            # Skip diagnostic features
            if feature_name.startswith("diagnostics"):
                continue
            
            # Parse feature name to get class
            parts = feature_name.split("_")
            if len(parts) >= 2:
                class_name = parts[0]
                if class_name in organized:
                    organized[class_name][feature_name] = feature_value
        
        # Remove empty classes
        organized = {k: v for k, v in organized.items() if v}
        
        return organized
    
    def _calculate_suv_metrics(self, image: sitk.Image, mask: sitk.Image) -> Dict[str, float]:
        """Calculate SUV-based metrics"""
        try:
            image_array = sitk.GetArrayFromImage(image)
            mask_array = sitk.GetArrayFromImage(mask)
            
            # Apply mask
            masked_image = image_array * (mask_array > 0)
            
            # Calculate SUV metrics
            suv_values = masked_image[masked_image > 0]
            
            if len(suv_values) == 0:
                return {
                    "SUVmax": 0.0,
                    "SUVmean": 0.0,
                    "SUVmin": 0.0,
                    "SUVstd": 0.0,
                    "MTV": 0.0,
                    "TLG": 0.0
                }
            
            # Basic SUV statistics
            suv_max = float(np.max(suv_values))
            suv_mean = float(np.mean(suv_values))
            suv_min = float(np.min(suv_values))
            suv_std = float(np.std(suv_values))
            
            # Calculate volume (assuming SUV units are g/mL)
            # This is a simplified calculation - in practice, you'd need
            # proper calibration and conversion factors
            voxel_volume = np.prod(image.GetSpacing()) / 1000  # Convert to cm³
            mtv = float(np.sum(mask_array > 0) * voxel_volume)  # cm³
            
            # Total Lesion Glycolysis (TLG)
            tlg = float(np.sum(suv_values) * voxel_volume)  # g
            
            return {
                "SUVmax": suv_max,
                "SUVmean": suv_mean,
                "SUVmin": suv_min,
                "SUVstd": suv_std,
                "MTV": mtv,
                "TLG": tlg
            }
            
        except Exception as e:
            logger.error(f"SUV metrics calculation failed: {e}")
            return {}
    
    def _get_image_info(self, image: sitk.Image) -> Dict[str, Any]:
        """Get image information"""
        try:
            return {
                "size": image.GetSize(),
                "spacing": image.GetSpacing(),
                "origin": image.GetOrigin(),
                "direction": image.GetDirection(),
                "pixel_type": image.GetPixelIDTypeAsString()
            }
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}
    
    def _get_mask_info(self, mask: sitk.Image) -> Dict[str, Any]:
        """Get mask information"""
        try:
            mask_array = sitk.GetArrayFromImage(mask)
            return {
                "size": mask.GetSize(),
                "spacing": mask.GetSpacing(),
                "voxel_count": int(np.sum(mask_array > 0)),
                "volume_cm3": float(np.sum(mask_array > 0) * np.prod(mask.GetSpacing()) / 1000)
            }
        except Exception as e:
            logger.error(f"Failed to get mask info: {e}")
            return {}
    
    def extract_texture_features(
        self, 
        image_path: str, 
        mask_path: str,
        texture_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extract specific texture features"""
        if texture_types is None:
            texture_types = ["glcm", "glrlm", "glszm"]
        
        # Create temporary config for texture features only
        temp_config = self.config.copy()
        temp_config["featureClass"] = texture_types
        
        try:
            temp_extractor = featureextractor.RadiomicsFeatureExtractor(**temp_config)
            
            # Load image and mask
            image = sitk.ReadImage(image_path)
            mask = sitk.ReadImage(mask_path)
            
            # Extract texture features
            features = temp_extractor.execute(image, mask)
            
            # Organize by texture type
            organized = {}
            for feature_name, feature_value in features.items():
                if feature_name.startswith("diagnostics"):
                    continue
                
                parts = feature_name.split("_")
                if len(parts) >= 2:
                    texture_type = parts[0]
                    if texture_type in texture_types:
                        if texture_type not in organized:
                            organized[texture_type] = {}
                        organized[texture_type][feature_name] = feature_value
            
            return {
                "success": True,
                "texture_features": organized
            }
            
        except Exception as e:
            logger.error(f"Texture feature extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    def calculate_percist_metrics(
        self, 
        baseline_image: str, 
        baseline_mask: str,
        followup_image: str, 
        followup_mask: str
    ) -> Dict[str, Any]:
        """Calculate PERCIST metrics for response assessment"""
        try:
            # Extract features from baseline
            baseline_result = self.extract_features(baseline_image, baseline_mask)
            if not baseline_result["success"]:
                return {"success": False, "error": "Baseline feature extraction failed"}
            
            # Extract features from follow-up
            followup_result = self.extract_features(followup_image, followup_mask)
            if not followup_result["success"]:
                return {"success": False, "error": "Follow-up feature extraction failed"}
            
            # Calculate PERCIST metrics
            baseline_suvmax = baseline_result["suv_metrics"]["SUVmax"]
            followup_suvmax = followup_result["suv_metrics"]["SUVmax"]
            
            if baseline_suvmax == 0:
                return {"success": False, "error": "Baseline SUVmax is zero"}
            
            # Calculate percentage change
            suv_change_percent = ((followup_suvmax - baseline_suvmax) / baseline_suvmax) * 100
            
            # Determine PERCIST category
            percist_category = self._categorize_percist(suv_change_percent)
            
            return {
                "success": True,
                "baseline_suvmax": baseline_suvmax,
                "followup_suvmax": followup_suvmax,
                "suv_change_percent": suv_change_percent,
                "percist_category": percist_category,
                "baseline_metrics": baseline_result["suv_metrics"],
                "followup_metrics": followup_result["suv_metrics"]
            }
            
        except Exception as e:
            logger.error(f"PERCIST calculation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _categorize_percist(self, suv_change_percent: float) -> str:
        """Categorize PERCIST response"""
        if suv_change_percent <= -30:
            return "PMR"  # Partial Metabolic Response
        elif suv_change_percent <= 30:
            return "SMD"  # Stable Metabolic Disease
        else:
            return "PMD"  # Progressive Metabolic Disease

def create_radiomics_extractor(config_path: Optional[str] = None) -> RadiomicsExtractor:
    """Factory function to create radiomics extractor"""
    return RadiomicsExtractor(config_path)

def run_radiomics_pipeline(
    image_path: str,
    mask_path: str,
    config_path: Optional[str] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """Complete radiomics pipeline"""
    pipeline_result = {
        "success": False,
        "outputs": {},
        "processing_time": 0.0,
        "errors": []
    }
    
    import time
    start_time = time.time()
    
    try:
        # Create extractor
        extractor = create_radiomics_extractor(config_path)
        
        # Extract features
        result = extractor.extract_features(image_path, mask_path)
        
        if result["success"]:
            pipeline_result["success"] = True
            pipeline_result["outputs"] = result
            
            # Save results if output path specified
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump(result, f, indent=2, default=str)
                pipeline_result["outputs"]["saved_to"] = output_path
        else:
            pipeline_result["errors"].append(result["error"])
        
    except Exception as e:
        pipeline_result["errors"].append(f"Pipeline failed: {e}")
    
    finally:
        pipeline_result["processing_time"] = time.time() - start_time
    
    return pipeline_result
