"""
Unit Tests
Birim testleri
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import uuid

from backend.core.auth import create_access_token, verify_password, get_password_hash
from backend.core.performance import PerformanceOptimizer, PerformanceMetrics
from backend.core.database import Patient, Report, SUVMeasurement
from backend.core.cache import CacheManager
from backend.core.connection_pool import DatabasePool, HTTPPool

class TestAuth:
    """Authentication unit tests"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "testuser", "roles": ["admin"]}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_password(self):
        """Test password verification"""
        password = "testpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

class TestPerformance:
    """Performance optimization unit tests"""
    
    def test_performance_optimizer_init(self):
        """Test performance optimizer initialization"""
        optimizer = PerformanceOptimizer()
        
        assert optimizer.optimization_enabled is True
        assert optimizer.gc_threshold == 80
        assert optimizer.cache_cleanup_interval == 300
        assert len(optimizer.metrics_history) == 0
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    def test_collect_metrics(self, mock_net, mock_disk, mock_memory, mock_cpu):
        """Test metrics collection"""
        # Mock system data
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, used=1024*1024*1024, available=1024*1024*1024)
        mock_disk.return_value = Mock(used=500*1024*1024*1024, total=1000*1024*1024*1024)
        mock_net.return_value = Mock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20)
        
        optimizer = PerformanceOptimizer()
        metrics = asyncio.run(optimizer.collect_metrics())
        
        assert metrics is not None
        assert metrics.cpu_percent == 50.0
        assert metrics.memory_percent == 60.0
        assert metrics.memory_used_mb == 1024.0
        assert metrics.memory_available_mb == 1024.0
        assert metrics.disk_usage_percent == 50.0
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        optimizer = PerformanceOptimizer()
        
        # Add mock metrics
        for i in range(5):
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=50.0 + i,
                memory_percent=60.0 + i,
                memory_used_mb=1024.0,
                memory_available_mb=1024.0,
                disk_usage_percent=50.0,
                network_io={"bytes_sent": 1000, "bytes_recv": 2000},
                active_connections=10,
                response_time_ms=100.0,
                requests_per_second=10.0,
                cache_hit_rate=85.0,
                gc_collections=5
            )
            optimizer.metrics_history.append(metrics)
        
        summary = optimizer.get_performance_summary()
        
        assert summary["status"] == "healthy"
        assert "current" in summary
        assert "averages" in summary
        assert summary["optimization_enabled"] is True

class TestDatabase:
    """Database model unit tests"""
    
    def test_patient_model(self):
        """Test Patient model creation"""
        patient = Patient(
            first_name="Test",
            last_name="Patient",
            date_of_birth=datetime.now(),
            gender="male",
            phone="+905551234567",
            email="test@example.com",
            is_active=True  # Explicitly set since SQLAlchemy defaults only apply on DB insert
        )
        
        assert patient.first_name == "Test"
        assert patient.last_name == "Patient"
        assert patient.gender == "male"
        assert patient.phone == "+905551234567"
        assert patient.email == "test@example.com"
        assert patient.is_active is True
    
    def test_report_model(self):
        """Test Report model creation"""
        report = Report(
            patient_id=uuid.uuid4(),
            report_type="pet-ct",
            study_date=datetime.now(),
            findings="Test findings",
            impression="Test impression",
            status="draft"  # Explicitly set since SQLAlchemy defaults only apply on DB insert
        )
        
        assert report.report_type == "pet-ct"
        assert report.findings == "Test findings"
        assert report.impression == "Test impression"
        assert report.status == "draft"
    
    def test_suv_measurement_model(self):
        """Test SUVMeasurement model creation"""
        measurement = SUVMeasurement(
            patient_id=uuid.uuid4(),
            measurement_date=datetime.now(),
            suv_max=8.5,
            suv_mean=4.2
        )
        
        assert measurement.suv_max == 8.5
        assert measurement.suv_mean == 4.2
        assert measurement.lesion_location is None

class TestCache:
    """Cache service unit tests"""
    
    def test_cache_service_init(self):
        """Test cache service initialization"""
        cache = CacheManager()
        
        assert cache.fallback_to_memory is True
        assert cache.memory_cache == {}
        # Redis connection may fail in test environment, that's OK
    
    def test_cache_set_get(self):
        """Test cache set and get operations"""
        cache = CacheManager()
        
        # Test memory cache
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")
        
        assert value == "test_value"
    
    def test_cache_delete(self):
        """Test cache delete operation"""
        cache = CacheManager()
        
        cache.set("test_key", "test_value")
        cache.delete("test_key")
        value = cache.get("test_key")
        
        assert value is None

class TestConnectionPool:
    """Connection pool unit tests"""
    
    def test_database_pool_config(self):
        """Test database pool configuration"""
        from backend.core.connection_pool import PoolConfig
        
        config = PoolConfig(
            min_connections=5,
            max_connections=20,
            timeout=30
        )
        
        assert config.min_connections == 5
        assert config.max_connections == 20
        assert config.timeout == 30
    
    def test_http_pool_config(self):
        """Test HTTP pool configuration"""
        from backend.core.connection_pool import PoolConfig
        
        config = PoolConfig(
            min_connections=10,
            max_connections=50,
            timeout=30
        )
        
        assert config.min_connections == 10
        assert config.max_connections == 50
        assert config.timeout == 30

class TestUtilities:
    """Utility function unit tests"""
    
    def test_uuid_generation(self):
        """Test UUID generation"""
        patient_id = uuid.uuid4()
        
        assert isinstance(patient_id, uuid.UUID)
        assert str(patient_id) is not None
        assert len(str(patient_id)) == 36  # Standard UUID length
    
    def test_datetime_operations(self):
        """Test datetime operations"""
        now = datetime.now()
        future = now + timedelta(days=1)
        
        assert future > now
        assert (future - now).days == 1
    
    def test_json_serialization(self):
        """Test JSON serialization"""
        import json
        
        data = {
            "name": "Test",
            "age": 30,
            "active": True,
            "items": [1, 2, 3]
        }
        
        json_str = json.dumps(data)
        parsed_data = json.loads(json_str)
        
        assert parsed_data == data
        assert parsed_data["name"] == "Test"
        assert parsed_data["age"] == 30
        assert parsed_data["active"] is True
        assert parsed_data["items"] == [1, 2, 3]

# Performance tests
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    def test_metrics_collection_performance(self):
        """Test metrics collection performance"""
        import time
        
        optimizer = PerformanceOptimizer()
        
        start_time = time.time()
        metrics = asyncio.run(optimizer.collect_metrics())
        end_time = time.time()
        
        collection_time = end_time - start_time
        
        # Should collect metrics in less than 2 seconds (allowing for system load)
        assert collection_time < 2.0
        assert metrics is not None
    
    def test_cache_performance(self):
        """Test cache performance"""
        import time
        
        cache = CacheManager()
        
        # Test cache set performance
        start_time = time.time()
        for i in range(100):
            cache.set(f"key_{i}", f"value_{i}")
        set_time = time.time() - start_time
        
        # Test cache get performance
        start_time = time.time()
        for i in range(100):
            value = cache.get(f"key_{i}")
            assert value == f"value_{i}"
        get_time = time.time() - start_time
        
        # Should be fast (less than 0.1 seconds for 100 operations)
        assert set_time < 0.1
        assert get_time < 0.1

if __name__ == "__main__":
    pytest.main([__file__])
