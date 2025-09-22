#!/usr/bin/env python3
"""
NeuroPETRIX v2.0 - Performance Monitor
=====================================

Route response time'ları ve performans metriklerini izle
"""

import requests
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

class PerformanceMonitor:
    def __init__(self):
        self.results = {}
        
    def measure_endpoint(self, method: str, endpoint: str, payload: Dict = None, repeat: int = 5) -> Dict[str, Any]:
        """Endpoint performance'ını ölç"""
        times = []
        status_codes = []
        errors = []
        
        print(f"📊 Testing {method} {endpoint} ({repeat} times)...")
        
        for i in range(repeat):
            start_time = time.time()
            
            try:
                if method.upper() == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint}")
                elif method.upper() == "POST":
                    response = requests.post(f"{BASE_URL}{endpoint}", json=payload or {})
                elif method.upper() == "PUT":
                    response = requests.put(f"{BASE_URL}{endpoint}", json=payload or {})
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # milliseconds
                
                times.append(response_time)
                status_codes.append(response.status_code)
                
                if response.status_code >= 400:
                    errors.append(f"HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                times.append(response_time)
                status_codes.append(0)
                errors.append(str(e))
            
            # Small delay between requests
            time.sleep(0.1)
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        
        success_rate = (len([s for s in status_codes if 200 <= s < 300]) / repeat) * 100
        
        result = {
            "endpoint": f"{method} {endpoint}",
            "measurements": repeat,
            "avg_response_time_ms": round(avg_time, 2),
            "min_response_time_ms": round(min_time, 2),
            "max_response_time_ms": round(max_time, 2),
            "median_response_time_ms": round(median_time, 2),
            "success_rate_percent": round(success_rate, 2),
            "status_codes": status_codes,
            "errors": errors[:3]  # Sadece ilk 3 error
        }
        
        return result
    
    def test_legacy_endpoints(self):
        """Legacy endpoint'leri test et"""
        print("\n🔍 LEGACY ENDPOINTS PERFORMANCE")
        print("=" * 50)
        
        legacy_tests = [
            ("GET", "/health"),
            ("GET", "/api/status"),
            ("GET", "/patients/"),
            ("GET", "/suv/measurements"),
            ("GET", "/hbys/health"),
            ("GET", "/monai/models"),
            ("GET", "/desktop-runner/health"),
        ]
        
        for method, endpoint in legacy_tests:
            result = self.measure_endpoint(method, endpoint)
            self.results[f"legacy_{endpoint.replace('/', '_')}"] = result
            self._print_result(result)
    
    def test_v2_endpoints(self):
        """V2.0 endpoint'leri test et"""
        print("\n🚀 V2.0 ENDPOINTS PERFORMANCE")
        print("=" * 50)
        
        # Test data
        patient_data = {
            "patient_id": "PERF-001",
            "icd10": "C34.9",
            "clinical_goal": "staging",
            "hbys": {
                "ECOG": 1,
                "eGFR": 78,
                "BloodGlucose_mgdl": 96,
                "allergies": [],
                "meds": []
            }
        }
        
        evidence_data = {
            "search_query": "lung cancer PET CT",
            "max_results": 10
        }
        
        report_data = {
            "patient_id": "PERF-001",
            "include_imaging": False,
            "report_format": "tsnm"
        }
        
        v2_tests = [
            ("POST", "/intake/patient", patient_data),
            ("GET", "/intake/patient/PERF-001"),
            ("GET", "/intake/all-patients"),
            ("POST", "/evidence/search", evidence_data),
            ("POST", "/report/compose", report_data),
        ]
        
        for method, endpoint, payload in v2_tests:
            result = self.measure_endpoint(method, endpoint, payload)
            self.results[f"v2_{endpoint.replace('/', '_')}"] = result
            self._print_result(result)
    
    def test_integration_workflow(self):
        """Integration workflow performance test"""
        print("\n🔄 INTEGRATION WORKFLOW PERFORMANCE")
        print("=" * 50)
        
        workflow_data = {
            "patient_data": {
                "patient_id": "WORKFLOW-001",
                "icd10": "C34.9"
            },
            "clinical_goal": "staging"
        }
        
        result = self.measure_endpoint("POST", "/integration/workflow/start", workflow_data, repeat=3)
        self.results["integration_workflow_start"] = result
        self._print_result(result)
    
    def _print_result(self, result: Dict[str, Any]):
        """Sonucu yazdır"""
        endpoint = result["endpoint"]
        avg_time = result["avg_response_time_ms"]
        success_rate = result["success_rate_percent"]
        
        # Performance evaluation
        if avg_time < 100:
            perf_icon = "🟢"  # Excellent
        elif avg_time < 500:
            perf_icon = "🟡"  # Good
        elif avg_time < 2000:
            perf_icon = "🟠"  # Acceptable
        else:
            perf_icon = "🔴"  # Poor
        
        print(f"{perf_icon} {endpoint:<30} | {avg_time:>6.1f}ms avg | {success_rate:>5.1f}% success")
        
        if result["errors"]:
            print(f"   ❌ Errors: {', '.join(result['errors'])}")
    
    def generate_summary_report(self):
        """Özet rapor oluştur"""
        print("\n📈 PERFORMANCE SUMMARY REPORT")
        print("=" * 60)
        
        all_times = []
        total_tests = 0
        successful_tests = 0
        
        legacy_times = []
        v2_times = []
        
        for key, result in self.results.items():
            avg_time = result["avg_response_time_ms"]
            success_rate = result["success_rate_percent"]
            measurements = result["measurements"]
            
            all_times.append(avg_time)
            total_tests += measurements
            successful_tests += (measurements * success_rate / 100)
            
            if key.startswith("legacy_"):
                legacy_times.append(avg_time)
            elif key.startswith("v2_"):
                v2_times.append(avg_time)
        
        print(f"📊 Total Endpoints Tested: {len(self.results)}")
        print(f"📊 Total Requests: {total_tests}")
        print(f"📊 Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print(f"📊 Average Response Time: {statistics.mean(all_times):.1f}ms")
        print(f"📊 Fastest Response: {min(all_times):.1f}ms")
        print(f"📊 Slowest Response: {max(all_times):.1f}ms")
        
        if legacy_times and v2_times:
            print(f"\n🔍 COMPARISON:")
            print(f"   Legacy Avg: {statistics.mean(legacy_times):.1f}ms")
            print(f"   V2.0 Avg: {statistics.mean(v2_times):.1f}ms")
            
            if statistics.mean(v2_times) < statistics.mean(legacy_times):
                print("   ✅ V2.0 is faster than Legacy!")
            else:
                print("   ⚠️  Legacy is faster than V2.0")
        
        # Performance targets
        print(f"\n🎯 PERFORMANCE TARGETS:")
        fast_endpoints = len([t for t in all_times if t < 100])
        acceptable_endpoints = len([t for t in all_times if 100 <= t < 2000])
        slow_endpoints = len([t for t in all_times if t >= 2000])
        
        print(f"   🟢 Fast (<100ms): {fast_endpoints}")
        print(f"   🟡 Acceptable (100-2000ms): {acceptable_endpoints}")
        print(f"   🔴 Slow (>2000ms): {slow_endpoints}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "summary": {
                    "total_endpoints": len(self.results),
                    "total_requests": total_tests,
                    "overall_success_rate": (successful_tests/total_tests)*100,
                    "average_response_time_ms": statistics.mean(all_times),
                    "fastest_response_ms": min(all_times),
                    "slowest_response_ms": max(all_times)
                },
                "detailed_results": self.results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {filename}")

def main():
    """Performance test runner"""
    print("🚀 NEUROPETRIX v2.0 - PERFORMANCE MONITOR")
    print("=" * 60)
    print(f"Server: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    monitor = PerformanceMonitor()
    
    try:
        # Test legacy endpoints
        monitor.test_legacy_endpoints()
        
        # Test v2.0 endpoints
        monitor.test_v2_endpoints()
        
        # Test integration workflow
        monitor.test_integration_workflow()
        
        # Generate summary
        monitor.generate_summary_report()
        
    except Exception as e:
        print(f"\n❌ PERFORMANCE MONITORING FAILED: {str(e)}")

if __name__ == "__main__":
    main()
