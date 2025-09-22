#!/usr/bin/env python3
"""
NeuroPETRIX v2.0 - System Monitor & Analytics
===========================================

Sistem durumu, resource kullanımı ve analytics
"""

import psutil
import requests
import json
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Sistem kaynaklarını ve performansını izle"""
    
    def __init__(self, db_path: str = "system_monitor.db"):
        self.db_path = db_path
        self.base_url = "http://localhost:8000"
        self._init_database()
    
    def _init_database(self):
        """Monitoring database'ini başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                memory_available_gb REAL,
                disk_usage_percent REAL,
                disk_free_gb REAL,
                network_bytes_sent INTEGER,
                network_bytes_recv INTEGER
            )
        """)
        
        # API metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                endpoint TEXT,
                method TEXT,
                response_time_ms REAL,
                status_code INTEGER,
                success BOOLEAN
            )
        """)
        
        # Error log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                error_type TEXT,
                error_message TEXT,
                source TEXT,
                severity TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Sistem metriklerini topla"""
        try:
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory kullanımı
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            # Network kullanımı
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available_gb, 2),
                "disk_usage_percent": round(disk_usage_percent, 2),
                "disk_free_gb": round(disk_free_gb, 2),
                "network_bytes_sent": network_bytes_sent,
                "network_bytes_recv": network_bytes_recv
            }
            
            # Database'e kaydet
            self._save_system_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"System metrics collection failed: {str(e)}")
            return {"error": str(e)}
    
    def _save_system_metrics(self, metrics: Dict[str, Any]):
        """Sistem metriklerini database'e kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, memory_available_gb, 
                 disk_usage_percent, disk_free_gb, network_bytes_sent, network_bytes_recv)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics["cpu_percent"],
                metrics["memory_percent"],
                metrics["memory_available_gb"],
                metrics["disk_usage_percent"],
                metrics["disk_free_gb"],
                metrics["network_bytes_sent"],
                metrics["network_bytes_recv"]
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save system metrics: {str(e)}")
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """API endpoint'leri test et ve metrikleri topla"""
        endpoints_to_test = [
            ("GET", "/health"),
            ("GET", "/api/status"),
            ("GET", "/patients/"),
            ("GET", "/intake/all-patients"),
            ("GET", "/hbys/health"),
            ("GET", "/monai/models"),
        ]
        
        results = {
            "tested_endpoints": len(endpoints_to_test),
            "successful": 0,
            "failed": 0,
            "average_response_time": 0,
            "endpoint_results": []
        }
        
        total_response_time = 0
        
        for method, endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", timeout=10)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # milliseconds
                
                success = 200 <= response.status_code < 300
                
                endpoint_result = {
                    "endpoint": f"{method} {endpoint}",
                    "response_time_ms": round(response_time, 2),
                    "status_code": response.status_code,
                    "success": success
                }
                
                results["endpoint_results"].append(endpoint_result)
                
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                
                total_response_time += response_time
                
                # Database'e kaydet
                self._save_api_metrics(method, endpoint, response_time, response.status_code, success)
                
            except Exception as e:
                endpoint_result = {
                    "endpoint": f"{method} {endpoint}",
                    "response_time_ms": 0,
                    "status_code": 0,
                    "success": False,
                    "error": str(e)
                }
                
                results["endpoint_results"].append(endpoint_result)
                results["failed"] += 1
                
                # Error log'a kaydet
                self._log_error("API_TEST", str(e), f"{method} {endpoint}", "ERROR")
        
        if results["tested_endpoints"] > 0:
            results["average_response_time"] = round(total_response_time / results["tested_endpoints"], 2)
            results["success_rate"] = round((results["successful"] / results["tested_endpoints"]) * 100, 2)
        
        return results
    
    def _save_api_metrics(self, method: str, endpoint: str, response_time: float, status_code: int, success: bool):
        """API metriklerini database'e kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO api_metrics (endpoint, method, response_time_ms, status_code, success)
                VALUES (?, ?, ?, ?, ?)
            """, (endpoint, method, response_time, status_code, success))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save API metrics: {str(e)}")
    
    def _log_error(self, error_type: str, error_message: str, source: str, severity: str):
        """Error'ları database'e kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_log (error_type, error_message, source, severity)
                VALUES (?, ?, ?, ?)
            """, (error_type, error_message, source, severity))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Genel sistem sağlığını değerlendir"""
        try:
            # En son sistem metrikleri
            system_metrics = self.collect_system_metrics()
            
            # API durumu
            api_metrics = self.test_api_endpoints()
            
            # Health status evaluation
            health_status = "healthy"
            warnings = []
            errors = []
            
            # CPU kontrolü
            if system_metrics.get("cpu_percent", 0) > 90:
                health_status = "critical"
                errors.append("High CPU usage detected")
            elif system_metrics.get("cpu_percent", 0) > 70:
                health_status = "warning"
                warnings.append("Elevated CPU usage")
            
            # Memory kontrolü
            if system_metrics.get("memory_percent", 0) > 90:
                health_status = "critical"
                errors.append("High memory usage detected")
            elif system_metrics.get("memory_percent", 0) > 80:
                health_status = "warning"
                warnings.append("Elevated memory usage")
            
            # Disk kontrolü
            if system_metrics.get("disk_usage_percent", 0) > 95:
                health_status = "critical"
                errors.append("Disk space critical")
            elif system_metrics.get("disk_usage_percent", 0) > 85:
                health_status = "warning"
                warnings.append("Low disk space")
            
            # API success rate kontrolü
            if api_metrics.get("success_rate", 0) < 50:
                health_status = "critical"
                errors.append("Multiple API endpoints failing")
            elif api_metrics.get("success_rate", 0) < 80:
                if health_status == "healthy":
                    health_status = "warning"
                warnings.append("Some API endpoints failing")
            
            result = {
                "overall_status": health_status,
                "timestamp": datetime.now().isoformat(),
                "system_metrics": system_metrics,
                "api_metrics": api_metrics,
                "warnings": warnings,
                "errors": errors,
                "uptime_hours": self._get_uptime_hours()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Health status check failed: {str(e)}")
            return {
                "overall_status": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_uptime_hours(self) -> float:
        """Sistem uptime'ını al"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            return round(uptime_seconds / 3600, 2)
        except:
            return 0.0
    
    def get_historical_data(self, hours: int = 24) -> Dict[str, Any]:
        """Geçmiş verilerini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            
            # System metrics
            cursor.execute("""
                SELECT timestamp, cpu_percent, memory_percent, disk_usage_percent
                FROM system_metrics
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 100
            """, (since_time,))
            
            system_history = []
            for row in cursor.fetchall():
                system_history.append({
                    "timestamp": row[0],
                    "cpu_percent": row[1],
                    "memory_percent": row[2],
                    "disk_usage_percent": row[3]
                })
            
            # API metrics
            cursor.execute("""
                SELECT endpoint, AVG(response_time_ms) as avg_response, 
                       COUNT(*) as total_requests,
                       SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests
                FROM api_metrics
                WHERE timestamp > ?
                GROUP BY endpoint
            """, (since_time,))
            
            api_history = []
            for row in cursor.fetchall():
                api_history.append({
                    "endpoint": row[0],
                    "avg_response_time_ms": round(row[1], 2),
                    "total_requests": row[2],
                    "successful_requests": row[3],
                    "success_rate": round((row[3] / row[2]) * 100, 2) if row[2] > 0 else 0
                })
            
            # Recent errors
            cursor.execute("""
                SELECT timestamp, error_type, error_message, source, severity
                FROM error_log
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 20
            """, (since_time,))
            
            recent_errors = []
            for row in cursor.fetchall():
                recent_errors.append({
                    "timestamp": row[0],
                    "error_type": row[1],
                    "error_message": row[2],
                    "source": row[3],
                    "severity": row[4]
                })
            
            conn.close()
            
            return {
                "time_range_hours": hours,
                "system_history": system_history,
                "api_history": api_history,
                "recent_errors": recent_errors,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {str(e)}")
            return {"error": str(e)}
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Detaylı performans raporu oluştur"""
        try:
            health_status = self.get_health_status()
            historical_data = self.get_historical_data(24)
            
            # Performance summary
            system_metrics = health_status.get("system_metrics", {})
            api_metrics = health_status.get("api_metrics", {})
            
            performance_score = 100
            
            # CPU score
            cpu_percent = system_metrics.get("cpu_percent", 0)
            if cpu_percent > 90:
                performance_score -= 30
            elif cpu_percent > 70:
                performance_score -= 15
            elif cpu_percent > 50:
                performance_score -= 5
            
            # Memory score
            memory_percent = system_metrics.get("memory_percent", 0)
            if memory_percent > 90:
                performance_score -= 25
            elif memory_percent > 80:
                performance_score -= 10
            elif memory_percent > 60:
                performance_score -= 5
            
            # API score
            api_success_rate = api_metrics.get("success_rate", 0)
            if api_success_rate < 50:
                performance_score -= 40
            elif api_success_rate < 80:
                performance_score -= 20
            elif api_success_rate < 95:
                performance_score -= 10
            
            # Response time score
            avg_response_time = api_metrics.get("average_response_time", 0)
            if avg_response_time > 2000:
                performance_score -= 15
            elif avg_response_time > 1000:
                performance_score -= 10
            elif avg_response_time > 500:
                performance_score -= 5
            
            performance_score = max(0, performance_score)
            
            # Performance grade
            if performance_score >= 90:
                performance_grade = "A"
            elif performance_score >= 80:
                performance_grade = "B"
            elif performance_score >= 70:
                performance_grade = "C"
            elif performance_score >= 60:
                performance_grade = "D"
            else:
                performance_grade = "F"
            
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "overall_performance": {
                    "score": performance_score,
                    "grade": performance_grade,
                    "status": health_status.get("overall_status", "unknown")
                },
                "current_metrics": {
                    "system": system_metrics,
                    "api": api_metrics
                },
                "historical_summary": {
                    "data_points": len(historical_data.get("system_history", [])),
                    "api_endpoints_monitored": len(historical_data.get("api_history", [])),
                    "recent_errors_count": len(historical_data.get("recent_errors", []))
                },
                "recommendations": self._generate_recommendations(health_status, historical_data)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, health_status: Dict, historical_data: Dict) -> List[str]:
        """Performans önerilerini oluştur"""
        recommendations = []
        
        try:
            system_metrics = health_status.get("system_metrics", {})
            api_metrics = health_status.get("api_metrics", {})
            
            # CPU recommendations
            cpu_percent = system_metrics.get("cpu_percent", 0)
            if cpu_percent > 80:
                recommendations.append("Consider scaling server resources or optimizing CPU-intensive operations")
            
            # Memory recommendations
            memory_percent = system_metrics.get("memory_percent", 0)
            if memory_percent > 80:
                recommendations.append("Monitor memory leaks and consider increasing RAM or implementing caching")
            
            # Disk recommendations
            disk_usage = system_metrics.get("disk_usage_percent", 0)
            if disk_usage > 85:
                recommendations.append("Clean up old files and implement disk space monitoring alerts")
            
            # API recommendations
            api_success_rate = api_metrics.get("success_rate", 0)
            if api_success_rate < 95:
                recommendations.append("Investigate failing API endpoints and implement better error handling")
            
            avg_response_time = api_metrics.get("average_response_time", 0)
            if avg_response_time > 500:
                recommendations.append("Optimize slow API endpoints and consider implementing caching")
            
            # General recommendations
            if len(health_status.get("errors", [])) > 0:
                recommendations.append("Address critical system errors to improve stability")
            
            if not recommendations:
                recommendations.append("System is performing well - continue monitoring")
            
        except Exception as e:
            recommendations.append(f"Failed to generate recommendations: {str(e)}")
        
        return recommendations

def main():
    """System monitor runner"""
    print("🔍 NEUROPETRIX v2.0 - SYSTEM MONITOR")
    print("=" * 60)
    
    monitor = SystemMonitor()
    
    try:
        # Health check
        print("\n📊 CURRENT HEALTH STATUS")
        health = monitor.get_health_status()
        
        status_icon = {
            "healthy": "🟢",
            "warning": "🟡", 
            "critical": "🔴",
            "unknown": "⚪"
        }.get(health.get("overall_status", "unknown"), "⚪")
        
        print(f"{status_icon} Overall Status: {health.get('overall_status', 'unknown').upper()}")
        
        if health.get("warnings"):
            print("\n⚠️  WARNINGS:")
            for warning in health["warnings"]:
                print(f"   • {warning}")
        
        if health.get("errors"):
            print("\n❌ ERRORS:")
            for error in health["errors"]:
                print(f"   • {error}")
        
        # System metrics
        print("\n💻 SYSTEM METRICS")
        sys_metrics = health.get("system_metrics", {})
        print(f"   CPU: {sys_metrics.get('cpu_percent', 0):.1f}%")
        print(f"   Memory: {sys_metrics.get('memory_percent', 0):.1f}%")
        print(f"   Disk: {sys_metrics.get('disk_usage_percent', 0):.1f}%")
        print(f"   Uptime: {health.get('uptime_hours', 0):.1f} hours")
        
        # API metrics
        print("\n🚀 API METRICS")
        api_metrics = health.get("api_metrics", {})
        print(f"   Success Rate: {api_metrics.get('success_rate', 0):.1f}%")
        print(f"   Avg Response Time: {api_metrics.get('average_response_time', 0):.1f}ms")
        print(f"   Successful: {api_metrics.get('successful', 0)}")
        print(f"   Failed: {api_metrics.get('failed', 0)}")
        
        # Performance report
        print("\n📈 PERFORMANCE REPORT")
        report = monitor.generate_performance_report()
        performance = report.get("overall_performance", {})
        print(f"   Score: {performance.get('score', 0)}/100")
        print(f"   Grade: {performance.get('grade', 'N/A')}")
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"system_report_{timestamp}.json"
        
        with open(report_file, "w") as f:
            json.dump({
                "health_status": health,
                "performance_report": report,
                "historical_data": monitor.get_historical_data(6)
            }, f, indent=2)
        
        print(f"\n💾 Full report saved: {report_file}")
        
    except Exception as e:
        print(f"\n❌ MONITORING FAILED: {str(e)}")

if __name__ == "__main__":
    main()
