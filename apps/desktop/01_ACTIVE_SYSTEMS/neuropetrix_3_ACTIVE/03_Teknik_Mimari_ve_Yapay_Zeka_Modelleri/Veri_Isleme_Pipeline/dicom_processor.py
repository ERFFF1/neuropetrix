import pydicom
import numpy as np
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DICOMProcessor:
    """
    DICOM dosyalarını işleyen ve PET-CT verilerini çıkaran sınıf
    """
    
    def __init__(self):
        self.supported_modalities = ['PT', 'CT', 'PET', 'PETCT']
        self.radiomics_features = []
        
    def load_dicom_series(self, folder_path: str) -> Dict[str, pydicom.Dataset]:
        """
        DICOM serisini yükler ve organize eder
        
        Args:
            folder_path: DICOM dosyalarının bulunduğu klasör
            
        Returns:
            Modality'ye göre organize edilmiş DICOM dataset'leri
        """
        try:
            folder = Path(folder_path)
            dicom_files = list(folder.glob("*.dcm"))
            
            if not dicom_files:
                raise ValueError("DICOM dosyası bulunamadı")
            
            series_dict = {}
            
            for file_path in dicom_files:
                try:
                    ds = pydicom.dcmread(str(file_path))
                    modality = ds.Modality
                    
                    if modality not in series_dict:
                        series_dict[modality] = []
                    
                    series_dict[modality].append(ds)
                    
                except Exception as e:
                    logger.warning(f"Dosya yüklenemedi {file_path}: {e}")
                    continue
            
            # Her modality için dosyaları sırala
            for modality in series_dict:
                series_dict[modality].sort(key=lambda x: x.InstanceNumber)
            
            logger.info(f"DICOM serisi yüklendi: {list(series_dict.keys())}")
            return series_dict
            
        except Exception as e:
            logger.error(f"DICOM serisi yüklenirken hata: {e}")
            raise
    
    def extract_patient_info(self, ds: pydicom.Dataset) -> Dict:
        """
        Hasta bilgilerini çıkarır
        
        Args:
            ds: DICOM dataset
            
        Returns:
            Hasta bilgileri
        """
        try:
            patient_info = {
                "patient_id": getattr(ds, 'PatientID', 'Unknown'),
                "patient_name": getattr(ds, 'PatientName', 'Unknown'),
                "patient_birth_date": getattr(ds, 'PatientBirthDate', 'Unknown'),
                "patient_sex": getattr(ds, 'PatientSex', 'Unknown'),
                "patient_age": getattr(ds, 'PatientAge', 'Unknown'),
                "study_date": getattr(ds, 'StudyDate', 'Unknown'),
                "study_description": getattr(ds, 'StudyDescription', 'Unknown'),
                "modality": getattr(ds, 'Modality', 'Unknown'),
                "institution_name": getattr(ds, 'InstitutionName', 'Unknown'),
                "manufacturer": getattr(ds, 'Manufacturer', 'Unknown'),
                "model_name": getattr(ds, 'ManufacturerModelName', 'Unknown')
            }
            
            return patient_info
            
        except Exception as e:
            logger.error(f"Hasta bilgileri çıkarılırken hata: {e}")
            return {}
    
    def extract_pet_parameters(self, ds: pydicom.Dataset) -> Dict:
        """
        PET parametrelerini çıkarır
        
        Args:
            ds: PET DICOM dataset
            
        Returns:
            PET parametreleri
        """
        try:
            pet_params = {}
            
            # Radiopharmaceutical bilgileri
            if hasattr(ds, 'RadiopharmaceuticalInformationSequence'):
                rad_info = ds.RadiopharmaceuticalInformationSequence[0]
                pet_params.update({
                    "tracer": getattr(rad_info, 'RadiopharmaceuticalInformation', 'Unknown'),
                    "injected_dose": getattr(rad_info, 'RadionuclideTotalDose', 0.0),
                    "injected_dose_units": getattr(rad_info, 'RadionuclideTotalDoseUnits', 'MBq'),
                    "injection_time": getattr(rad_info, 'RadiopharmaceuticalStartTime', 'Unknown'),
                    "uptake_time": getattr(rad_info, 'RadiopharmaceuticalStartTime', 'Unknown')
                })
            
            # SUV parametreleri
            if hasattr(ds, 'SUVType'):
                pet_params["suv_type"] = ds.SUVType
            
            # Image scaling
            if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
                pet_params.update({
                    "rescale_slope": float(ds.RescaleSlope),
                    "rescale_intercept": float(ds.RescaleIntercept)
                })
            
            # Units
            if hasattr(ds, 'Units'):
                pet_params["units"] = ds.Units
            
            return pet_params
            
        except Exception as e:
            logger.error(f"PET parametreleri çıkarılırken hata: {e}")
            return {}
    
    def calculate_suv(self, pixel_array: np.ndarray, pet_params: Dict, 
                     patient_weight: float = 70.0) -> np.ndarray:
        """
        SUV değerlerini hesaplar
        
        Args:
            pixel_array: PET görüntü verisi
            pet_params: PET parametreleri
            patient_weight: Hasta ağırlığı (kg)
            
        Returns:
            SUV değerleri
        """
        try:
            if 'rescale_slope' not in pet_params:
                logger.warning("Rescale parametreleri bulunamadı, SUV hesaplanamıyor")
                return pixel_array
            
            # SUV hesaplama
            # SUV = (Pixel Value * Rescale Slope + Rescale Intercept) / (Injected Dose / Patient Weight)
            
            injected_dose = pet_params.get('injected_dose', 0.0)
            if injected_dose <= 0:
                logger.warning("Enjekte edilen doz bilgisi bulunamadı")
                return pixel_array
            
            # SUV hesaplama
            suv_array = (pixel_array * pet_params['rescale_slope'] + pet_params['rescale_intercept']) / (injected_dose / patient_weight)
            
            logger.info(f"SUV hesaplandı: min={suv_array.min():.2f}, max={suv_array.max():.2f}")
            return suv_array
            
        except Exception as e:
            logger.error(f"SUV hesaplanırken hata: {e}")
            return pixel_array
    
    def extract_radiomics_features(self, image_array: np.ndarray, 
                                 mask_array: Optional[np.ndarray] = None) -> Dict:
        """
        Radiomics özelliklerini çıkarır (basit implementasyon)
        
        Args:
            image_array: Görüntü verisi
            mask_array: ROI mask (opsiyonel)
            
        Returns:
            Radiomics özellikleri
        """
        try:
            features = {}
            
            # Eğer mask yoksa, tüm görüntüyü kullan
            if mask_array is None:
                mask_array = np.ones_like(image_array, dtype=bool)
            
            # Masked image
            masked_image = image_array[mask_array]
            
            if len(masked_image) == 0:
                logger.warning("Mask'da veri bulunamadı")
                return features
            
            # First order statistics
            features.update({
                "mean": float(np.mean(masked_image)),
                "std": float(np.std(masked_image)),
                "min": float(np.min(masked_image)),
                "max": float(np.max(masked_image)),
                "median": float(np.median(masked_image)),
                "skewness": float(self._calculate_skewness(masked_image)),
                "kurtosis": float(self._calculate_kurtosis(masked_image))
            })
            
            # SUV metrics
            features.update({
                "suv_mean": float(np.mean(masked_image)),
                "suv_max": float(np.max(masked_image)),
                "suv_peak": float(np.percentile(masked_image, 95)),
                "suv_total": float(np.sum(masked_image))
            })
            
            # Shape features
            features.update({
                "volume_ml": float(np.sum(mask_array) * 0.001),  # cm³ to ml
                "surface_area": float(self._calculate_surface_area(mask_array)),
                "sphericity": float(self._calculate_sphericity(mask_array))
            })
            
            logger.info(f"Radiomics özellikleri çıkarıldı: {len(features)} özellik")
            return features
            
        except Exception as e:
            logger.error(f"Radiomics özellikleri çıkarılırken hata: {e}")
            return {}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Skewness hesaplar"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            return np.mean(((data - mean) / std) ** 3)
        except:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Kurtosis hesaplar"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            return np.mean(((data - mean) / std) ** 4) - 3
        except:
            return 0.0
    
    def _calculate_surface_area(self, mask: np.ndarray) -> float:
        """Surface area hesaplar (basit implementasyon)"""
        try:
            # Basit surface area hesaplama
            return float(np.sum(mask) * 6)  # Yaklaşık değer
        except:
            return 0.0
    
    def _calculate_sphericity(self, mask: np.ndarray) -> float:
        """Sphericity hesaplar"""
        try:
            volume = np.sum(mask)
            surface_area = self._calculate_surface_area(mask)
            
            if surface_area == 0:
                return 0.0
            
            # Sphericity = (π^(1/3) * (6*V)^(2/3)) / A
            sphericity = (np.pi ** (1/3) * (6 * volume) ** (2/3)) / surface_area
            return float(sphericity)
        except:
            return 0.0
    
    def process_petct_series(self, folder_path: str, 
                           patient_weight: float = 70.0) -> Dict:
        """
        PET-CT serisini işler ve tüm bilgileri çıkarır
        
        Args:
            folder_path: DICOM dosyalarının bulunduğu klasör
            patient_weight: Hasta ağırlığı (kg)
            
        Returns:
            İşlenmiş PET-CT verileri
        """
        try:
            logger.info(f"PET-CT serisi işleniyor: {folder_path}")
            
            # DICOM serisini yükle
            series_dict = self.load_dicom_series(folder_path)
            
            if not series_dict:
                raise ValueError("DICOM serisi yüklenemedi")
            
            # Sonuç verisi
            result = {
                "patient_info": {},
                "pet_data": {},
                "ct_data": {},
                "suv_data": {},
                "radiomics_features": {},
                "processing_info": {
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "total_files": sum(len(files) for files in series_dict.values()),
                    "modalities": list(series_dict.keys())
                }
            }
            
            # Her modality için işle
            for modality, datasets in series_dict.items():
                if modality == 'PT' or modality == 'PET':
                    # PET verilerini işle
                    result["patient_info"] = self.extract_patient_info(datasets[0])
                    result["pet_data"] = self.extract_pet_parameters(datasets[0])
                    
                    # SUV hesapla
                    if datasets:
                        pixel_array = datasets[0].pixel_array
                        suv_array = self.calculate_suv(pixel_array, result["pet_data"], patient_weight)
                        result["suv_data"] = {
                            "suv_array_shape": suv_array.shape,
                            "suv_min": float(suv_array.min()),
                            "suv_max": float(suv_array.max()),
                            "suv_mean": float(suv_array.mean())
                        }
                        
                        # Radiomics özellikleri
                        result["radiomics_features"] = self.extract_radiomics_features(suv_array)
                
                elif modality == 'CT':
                    # CT verilerini işle
                    if datasets:
                        result["ct_data"] = {
                            "ct_series_count": len(datasets),
                            "ct_image_shape": datasets[0].pixel_array.shape,
                            "ct_window_center": getattr(datasets[0], 'WindowCenter', 'Unknown'),
                            "ct_window_width": getattr(datasets[0], 'WindowWidth', 'Unknown')
                        }
            
            logger.info("PET-CT serisi başarıyla işlendi")
            return result
            
        except Exception as e:
            logger.error(f"PET-CT serisi işlenirken hata: {e}")
            raise
    
    def save_results(self, results: Dict, output_path: str):
        """
        Sonuçları JSON formatında kaydeder
        
        Args:
            results: İşlenmiş sonuçlar
            output_path: Çıktı dosya yolu
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Sonuçlar kaydedildi: {output_path}")
            
        except Exception as e:
            logger.error(f"Sonuçlar kaydedilirken hata: {e}")
            raise

def main():
    """Test fonksiyonu"""
    processor = DICOMProcessor()
    
    # Test için örnek kullanım
    print("DICOM Processor başlatıldı")
    print("Kullanım:")
    print("processor = DICOMProcessor()")
    print("results = processor.process_petct_series('dicom_folder_path')")
    print("processor.save_results(results, 'output.json')")

if __name__ == "__main__":
    main()
