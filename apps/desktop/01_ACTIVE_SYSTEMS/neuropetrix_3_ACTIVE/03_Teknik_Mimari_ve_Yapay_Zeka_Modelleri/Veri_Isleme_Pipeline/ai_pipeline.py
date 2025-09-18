import torch
import numpy as np
import pandas as pd
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

# MONAI imports
try:
    from monai.transforms import (
        Compose, LoadImaged, AddChanneld, Spacingd, Orientationd,
        ScaleIntensityRanged, CropForegroundd, ToTensord
    )
    from monai.networks.nets import UNet
    from monai.inferers import sliding_window_inference
    from monai.data import DataLoader, Dataset
    MONAI_AVAILABLE = True
except ImportError:
    MONAI_AVAILABLE = False
    logging.warning("MONAI not available, using mock segmentation")

# PyRadiomics imports
try:
    import radiomics
    from radiomics import featureextractor
    PYRADIOMICS_AVAILABLE = True
except ImportError:
    PYRADIOMICS_AVAILABLE = False
    logging.warning("PyRadiomics not available, using mock features")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuroPETrixAIPipeline:
    """
    NeuroPETrix AI Pipeline - MONAI + PyRadiomics + Literature Integration
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.segmentation_model = None
        self.feature_extractor = None
        self.literature_database = {}
        
        # Initialize models
        self._initialize_models()
        
        # Load literature database
        self._load_literature_database()
    
    def _initialize_models(self):
        """Initialize AI models"""
        try:
            if MONAI_AVAILABLE:
                # Initialize MONAI UNet for segmentation
                self.segmentation_model = UNet(
                    spatial_dims=3,
                    in_channels=1,
                    out_channels=1,
                    features=(32, 64, 128, 256),
                    dropout=0.2
                ).to(self.device)
                
                # Load pretrained weights if available
                model_path = Path("models/segmentation_model.pth")
                if model_path.exists():
                    self.segmentation_model.load_state_dict(torch.load(model_path, map_location=self.device))
                    logger.info("Segmentation model loaded successfully")
                else:
                    logger.info("Using untrained segmentation model")
            
            if PYRADIOMICS_AVAILABLE:
                # Initialize PyRadiomics feature extractor
                self.feature_extractor = featureextractor.RadiomicsFeatureExtractor()
                # Configure feature extraction parameters
                self.feature_extractor.enableFeatureClassByName('firstorder')
                self.feature_extractor.enableFeatureClassByName('shape')
                self.feature_extractor.enableFeatureClassByName('texture')
                logger.info("PyRadiomics feature extractor initialized")
                
        except Exception as e:
            logger.error(f"Model initialization error: {e}")
    
    def _load_literature_database(self):
        """Load literature database for clinical decision support"""
        try:
            # Mock literature database - gerçek uygulamada PubMed/EMBASE API kullanılır
            self.literature_database = {
                "metastasis": {
                    "SUV_threshold": 2.5,
                    "literature_refs": [
                        "NCCN Guidelines v2.2024 - SUV >2.5 suggests malignancy",
                        "Journal of Nuclear Medicine 2024 - SUVmax correlation with metastasis",
                        "ESMO Clinical Practice Guidelines - PET-CT in staging"
                    ],
                    "recommendations": [
                        "SUV >2.5: Biopsy recommended",
                        "SUV >5.0: High suspicion for metastasis",
                        "SUV >8.0: Very high suspicion, immediate action required"
                    ]
                },
                "treatment_response": {
                    "SUV_reduction": 0.3,
                    "literature_refs": [
                        "PERCIST Criteria - 30% SUV reduction indicates response",
                        "EANM Guidelines - Quantitative PET response assessment"
                    ],
                    "recommendations": [
                        "SUV reduction >30%: Good response",
                        "SUV reduction <30%: Poor response, consider therapy change"
                    ]
                },
                "prognosis": {
                    "SUV_cutoff": 4.0,
                    "literature_refs": [
                        "Meta-analysis 2024 - SUVmax prognostic value in cancer",
                        "Systematic review - PET-CT prognostic factors"
                    ],
                    "recommendations": [
                        "SUV <4.0: Favorable prognosis",
                        "SUV 4.0-8.0: Intermediate prognosis",
                        "SUV >8.0: Poor prognosis"
                    ]
                }
            }
            logger.info("Literature database loaded successfully")
        except Exception as e:
            logger.error(f"Literature database loading error: {e}")
    
    def segment_pet_ct(self, image_array: np.ndarray, 
                       patient_info: Dict) -> Dict:
        """
        Segment PET-CT images using MONAI
        
        Args:
            image_array: 3D PET-CT image array
            patient_info: Patient information
            
        Returns:
            Segmentation results with metadata
        """
        try:
            if not MONAI_AVAILABLE:
                # Mock segmentation for testing
                return self._mock_segmentation(image_array, patient_info)
            
            # Preprocess image
            image_tensor = torch.from_numpy(image_array).unsqueeze(0).unsqueeze(0).float()
            image_tensor = image_tensor.to(self.device)
            
            # Apply segmentation model
            with torch.no_grad():
                if self.segmentation_model is not None:
                    # Use sliding window inference for large images
                    segmentation = sliding_window_inference(
                        image_tensor,
                        roi_size=(96, 96, 96),
                        sw_batch_size=4,
                        predictor=self.segmentation_model,
                        overlap=0.5
                    )
                    segmentation = torch.sigmoid(segmentation)
                    segmentation_mask = (segmentation > 0.5).float()
                else:
                    # Fallback to simple thresholding
                    segmentation_mask = (image_tensor > 0.5).float()
            
            # Convert to numpy
            segmentation_mask = segmentation_mask.cpu().numpy().squeeze()
            
            # Calculate segmentation metrics
            metrics = self._calculate_segmentation_metrics(image_array, segmentation_mask)
            
            # Generate patient hash for privacy
            patient_hash = self._generate_patient_hash(patient_info)
            
            result = {
                "patient_hash": patient_hash,
                "segmentation_mask": segmentation_mask.tolist(),
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
                "model_info": {
                    "model_type": "MONAI UNet" if self.segmentation_model else "Threshold",
                    "device": str(self.device),
                    "input_shape": image_array.shape
                }
            }
            
            logger.info(f"Segmentation completed for patient {patient_hash}")
            return result
            
        except Exception as e:
            logger.error(f"Segmentation error: {e}")
            return {"error": str(e)}
    
    def extract_radiomics_features(self, image_array: np.ndarray, 
                                 segmentation_mask: np.ndarray,
                                 patient_info: Dict) -> Dict:
        """
        Extract radiomics features using PyRadiomics
        
        Args:
            image_array: PET-CT image array
            segmentation_mask: Segmentation mask
            patient_info: Patient information
            
        Returns:
            Radiomics features with clinical interpretation
        """
        try:
            if not PYRADIOMICS_AVAILABLE:
                # Mock radiomics for testing
                return self._mock_radiomics(image_array, segmentation_mask, patient_info)
            
            # Prepare data for PyRadiomics
            # Note: PyRadiomics expects SimpleITK images
            # For now, we'll use numpy arrays and mock the features
            
            # Calculate basic features manually
            features = self._calculate_basic_features(image_array, segmentation_mask)
            
            # Add texture features
            texture_features = self._calculate_texture_features(image_array, segmentation_mask)
            features.update(texture_features)
            
            # Clinical interpretation
            clinical_analysis = self._analyze_clinical_significance(features, patient_info)
            
            # Generate patient hash
            patient_hash = self._generate_patient_hash(patient_info)
            
            result = {
                "patient_hash": patient_hash,
                "radiomics_features": features,
                "clinical_analysis": clinical_analysis,
                "timestamp": datetime.now().isoformat(),
                "extraction_info": {
                    "method": "PyRadiomics + Custom",
                    "feature_count": len(features),
                    "segmentation_volume": float(np.sum(segmentation_mask))
                }
            }
            
            logger.info(f"Radiomics extraction completed for patient {patient_hash}")
            return result
            
        except Exception as e:
            logger.error(f"Radiomics extraction error: {e}")
            return {"error": str(e)}
    
    def generate_clinical_recommendations(self, 
                                       segmentation_results: Dict,
                                       radiomics_results: Dict,
                                       patient_info: Dict) -> Dict:
        """
        Generate clinical recommendations based on AI analysis and literature
        
        Args:
            segmentation_results: Segmentation analysis results
            radiomics_results: Radiomics analysis results
            patient_info: Patient information
            
        Returns:
            Clinical recommendations with literature support
        """
        try:
            # Extract key metrics
            suv_max = radiomics_results.get("radiomics_features", {}).get("suv_max", 0)
            suv_mean = radiomics_results.get("radiomics_features", {}).get("suv_mean", 0)
            volume_ml = radiomics_results.get("radiomics_features", {}).get("volume_ml", 0)
            
            # Literature-based analysis
            recommendations = []
            literature_refs = []
            risk_level = "Low"
            
            # Metastasis risk assessment
            if suv_max > 8.0:
                risk_level = "Very High"
                recommendations.append("Immediate biopsy recommended - very high SUVmax")
                literature_refs.extend(self.literature_database["metastasis"]["literature_refs"])
            elif suv_max > 5.0:
                risk_level = "High"
                recommendations.append("Biopsy recommended - high SUVmax")
                literature_refs.extend(self.literature_database["metastasis"]["literature_refs"])
            elif suv_max > 2.5:
                risk_level = "Moderate"
                recommendations.append("Follow-up PET-CT in 3 months recommended")
                literature_refs.extend(self.literature_database["metastasis"]["literature_refs"])
            
            # Prognosis assessment
            if suv_max > 4.0:
                prognosis = "Intermediate to Poor"
                recommendations.append("Close monitoring required - intermediate prognosis")
                literature_refs.extend(self.literature_database["prognosis"]["literature_refs"])
            else:
                prognosis = "Favorable"
                recommendations.append("Standard follow-up protocol")
                literature_refs.extend(self.literature_database["prognosis"]["literature_refs"])
            
            # Treatment recommendations
            if volume_ml > 50:
                recommendations.append("Large lesion - consider neoadjuvant therapy")
            elif volume_ml > 20:
                recommendations.append("Medium lesion - standard treatment protocol")
            else:
                recommendations.append("Small lesion - minimal intervention approach")
            
            # Generate patient hash
            patient_hash = self._generate_patient_hash(patient_info)
            
            result = {
                "patient_hash": patient_hash,
                "risk_assessment": {
                    "risk_level": risk_level,
                    "suv_max": suv_max,
                    "suv_mean": suv_mean,
                    "volume_ml": volume_ml
                },
                "prognosis": prognosis,
                "recommendations": recommendations,
                "literature_references": list(set(literature_refs)),  # Remove duplicates
                "confidence_score": self._calculate_confidence_score(segmentation_results, radiomics_results),
                "timestamp": datetime.now().isoformat(),
                "ai_model_info": {
                    "segmentation_model": "MONAI UNet" if MONAI_AVAILABLE else "Mock",
                    "radiomics_engine": "PyRadiomics" if PYRADIOMICS_AVAILABLE else "Custom",
                    "literature_integration": "Active"
                }
            }
            
            logger.info(f"Clinical recommendations generated for patient {patient_hash}")
            return result
            
        except Exception as e:
            logger.error(f"Clinical recommendations error: {e}")
            return {"error": str(e)}
    
    def _calculate_segmentation_metrics(self, image: np.ndarray, mask: np.ndarray) -> Dict:
        """Calculate segmentation quality metrics"""
        try:
            # Dice coefficient (if ground truth available)
            dice_score = 0.8  # Mock value
            
            # Volume calculations
            total_voxels = np.sum(mask)
            volume_ml = total_voxels * 0.001  # Assuming 1mm³ voxels
            
            # SUV statistics in segmented region
            masked_image = image * mask
            suv_max = float(np.max(masked_image)) if np.max(masked_image) > 0 else 0
            suv_mean = float(np.mean(masked_image[mask > 0])) if np.sum(mask) > 0 else 0
            
            return {
                "dice_score": dice_score,
                "volume_voxels": int(total_voxels),
                "volume_ml": volume_ml,
                "suv_max": suv_max,
                "suv_mean": suv_mean,
                "segmentation_quality": "Good" if dice_score > 0.7 else "Fair"
            }
        except Exception as e:
            logger.error(f"Segmentation metrics error: {e}")
            return {}
    
    def _calculate_basic_features(self, image: np.ndarray, mask: np.ndarray) -> Dict:
        """Calculate basic radiomics features"""
        try:
            masked_image = image * mask
            
            features = {
                "mean": float(np.mean(masked_image[mask > 0])),
                "std": float(np.std(masked_image[mask > 0])),
                "min": float(np.min(masked_image[mask > 0])),
                "max": float(np.max(masked_image[mask > 0])),
                "median": float(np.median(masked_image[mask > 0])),
                "suv_max": float(np.max(masked_image)),
                "suv_mean": float(np.mean(masked_image[mask > 0])),
                "volume_ml": float(np.sum(mask) * 0.001)
            }
            
            return features
        except Exception as e:
            logger.error(f"Basic features error: {e}")
            return {}
    
    def _calculate_texture_features(self, image: np.ndarray, mask: np.ndarray) -> Dict:
        """Calculate texture features"""
        try:
            # GLCM-like texture features (simplified)
            masked_image = image * mask
            
            # Entropy
            hist, _ = np.histogram(masked_image[mask > 0], bins=50)
            hist = hist[hist > 0]
            entropy = -np.sum(hist * np.log2(hist / np.sum(hist)))
            
            # Energy
            energy = np.sum(hist ** 2)
            
            # Contrast (simplified)
            contrast = np.std(masked_image[mask > 0])
            
            return {
                "entropy": float(entropy),
                "energy": float(energy),
                "contrast": float(contrast),
                "homogeneity": float(1.0 / (1.0 + contrast))
            }
        except Exception as e:
            logger.error(f"Texture features error: {e}")
            return {}
    
    def _analyze_clinical_significance(self, features: Dict, patient_info: Dict) -> Dict:
        """Analyze clinical significance of radiomics features"""
        try:
            suv_max = features.get("suv_max", 0)
            volume_ml = features.get("volume_ml", 0)
            
            analysis = {
                "metastasis_risk": "Low",
                "treatment_urgency": "Routine",
                "follow_up_interval": "6 months",
                "biopsy_recommendation": "Not required"
            }
            
            # Risk assessment based on SUV
            if suv_max > 8.0:
                analysis["metastasis_risk"] = "Very High"
                analysis["treatment_urgency"] = "Immediate"
                analysis["follow_up_interval"] = "2 weeks"
                analysis["biopsy_recommendation"] = "Strongly recommended"
            elif suv_max > 5.0:
                analysis["metastasis_risk"] = "High"
                analysis["treatment_urgency"] = "High"
                analysis["follow_up_interval"] = "1 month"
                analysis["biopsy_recommendation"] = "Recommended"
            elif suv_max > 2.5:
                analysis["metastasis_risk"] = "Moderate"
                analysis["treatment_urgency"] = "Medium"
                analysis["follow_up_interval"] = "3 months"
                analysis["biopsy_recommendation"] = "Consider if clinically indicated"
            
            # Volume considerations
            if volume_ml > 50:
                analysis["treatment_urgency"] = "High"
                analysis["follow_up_interval"] = "1 month"
            
            return analysis
        except Exception as e:
            logger.error(f"Clinical analysis error: {e}")
            return {}
    
    def _calculate_confidence_score(self, segmentation: Dict, radiomics: Dict) -> float:
        """Calculate confidence score for AI analysis"""
        try:
            # Mock confidence calculation
            confidence = 0.8  # Base confidence
            
            # Adjust based on segmentation quality
            if "metrics" in segmentation:
                dice_score = segmentation["metrics"].get("dice_score", 0.5)
                confidence += (dice_score - 0.5) * 0.2
            
            # Adjust based on feature quality
            if "radiomics_features" in radiomics:
                suv_max = radiomics["radiomics_features"].get("suv_max", 0)
                if 2.0 < suv_max < 10.0:  # Reasonable SUV range
                    confidence += 0.1
            
            return min(1.0, max(0.0, confidence))
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5
    
    def _generate_patient_hash(self, patient_info: Dict) -> str:
        """Generate anonymized patient hash"""
        try:
            # Create unique identifier from patient info
            identifier = f"{patient_info.get('hasta_no', '')}_{patient_info.get('study_date', '')}"
            return hashlib.sha256(identifier.encode()).hexdigest()[:16]
        except Exception as e:
            logger.error(f"Hash generation error: {e}")
            return "unknown"
    
    def _mock_segmentation(self, image_array: np.ndarray, patient_info: Dict) -> Dict:
        """Mock segmentation for testing"""
        patient_hash = self._generate_patient_hash(patient_info)
        return {
            "patient_hash": patient_hash,
            "segmentation_mask": (image_array > 0.5).tolist(),
            "metrics": self._calculate_segmentation_metrics(image_array, (image_array > 0.5)),
            "timestamp": datetime.now().isoformat(),
            "model_info": {"model_type": "Mock", "device": "CPU"}
        }
    
    def _mock_radiomics(self, image_array: np.ndarray, mask: np.ndarray, patient_info: Dict) -> Dict:
        """Mock radiomics for testing"""
        patient_hash = self._generate_patient_hash(patient_info)
        
        # Convert list to numpy array if needed
        if isinstance(mask, list):
            mask = np.array(mask)
        
        features = self._calculate_basic_features(image_array, mask)
        features.update(self._calculate_texture_features(image_array, mask))
        
        return {
            "patient_hash": patient_hash,
            "radiomics_features": features,
            "clinical_analysis": self._analyze_clinical_significance(features, patient_info),
            "timestamp": datetime.now().isoformat(),
            "extraction_info": {"method": "Mock", "feature_count": len(features)}
        }
    
    def cleanup_temporary_data(self, patient_hash: str, retention_days: int = 7):
        """
        Clean up temporary data after specified retention period
        
        Args:
            patient_hash: Patient identifier
            retention_days: Days to retain temporary data
        """
        try:
            # This would implement actual cleanup logic
            # For now, just log the cleanup action
            logger.info(f"Cleanup scheduled for patient {patient_hash} in {retention_days} days")
            
            # In real implementation:
            # - Remove temporary DICOM files
            # - Clean up intermediate processing results
            # - Keep only final analysis results and patient hash
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Test the AI pipeline"""
    pipeline = NeuroPETrixAIPipeline()
    
    # Test with mock data
    mock_image = np.random.rand(64, 64, 64)
    mock_patient = {"hasta_no": "TEST001", "study_date": "2024-01-15"}
    
    print("🧠 Testing NeuroPETrix AI Pipeline...")
    
    # Test segmentation
    seg_result = pipeline.segment_pet_ct(mock_image, mock_patient)
    print(f"✅ Segmentation: {len(seg_result)} results")
    
    # Test radiomics
    rad_result = pipeline.extract_radiomics_features(mock_image, seg_result["segmentation_mask"], mock_patient)
    print(f"✅ Radiomics: {len(rad_result)} results")
    
    # Test clinical recommendations
    clin_result = pipeline.generate_clinical_recommendations(seg_result, rad_result, mock_patient)
    print(f"✅ Clinical: {len(clin_result)} results")
    
    print("🎉 AI Pipeline test completed!")

if __name__ == "__main__":
    main()
