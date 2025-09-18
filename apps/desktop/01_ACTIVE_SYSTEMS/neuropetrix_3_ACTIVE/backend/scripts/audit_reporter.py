#!/usr/bin/env python3
"""
NeuroPETRIX Audit Reporter
Generates comprehensive audit reports for compliance and quality assurance
"""

import argparse
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditReporter:
    """Generates comprehensive audit reports"""
    
    def __init__(self, db_path: str = "neuropetrix.db"):
        self.db_path = db_path
        self.report_data = {}
        
    def generate_report(self, days: int = 30, output_format: str = "json") -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        try:
            logger.info(f"Generating audit report for last {days} days")
            
            # Collect all audit data
            self._collect_system_metrics()
            self._collect_user_activity()
            self._collect_case_processing()
            self._collect_model_usage()
            self._collect_error_logs()
            self._collect_performance_metrics()
            
            # Generate summary
            self._generate_summary(days)
            
            # Format output
            if output_format == "json":
                return self.report_data
            elif output_format == "csv":
                return self._format_csv()
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
        except Exception as e:
            logger.error(f"Error generating audit report: {e}")
            raise
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # System uptime and health
            cursor.execute("""
                SELECT COUNT(*) as total_requests,
                       COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_requests,
                       COUNT(CASE WHEN status_code >= 400 THEN 1 END) as failed_requests
                FROM request_logs
                WHERE timestamp >= datetime('now', '-30 days')
            """)
            
            result = cursor.fetchone()
            self.report_data["system_metrics"] = {
                "total_requests": result[0] if result else 0,
                "successful_requests": result[1] if result else 0,
                "failed_requests": result[2] if result else 0,
                "success_rate": (result[1] / result[0] * 100) if result and result[0] > 0 else 0
            }
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not collect system metrics: {e}")
            self.report_data["system_metrics"] = {"error": str(e)}
    
    def _collect_user_activity(self):
        """Collect user activity data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User activity summary
            cursor.execute("""
                SELECT user_id, COUNT(*) as activity_count,
                       MAX(timestamp) as last_activity
                FROM user_activity
                WHERE timestamp >= datetime('now', '-30 days')
                GROUP BY user_id
                ORDER BY activity_count DESC
                LIMIT 10
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    "user_id": row[0],
                    "activity_count": row[1],
                    "last_activity": row[2]
                })
            
            self.report_data["user_activity"] = {
                "active_users": len(users),
                "top_users": users
            }
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not collect user activity: {e}")
            self.report_data["user_activity"] = {"error": str(e)}
    
    def _collect_case_processing(self):
        """Collect case processing statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Case processing summary
            cursor.execute("""
                SELECT clinical_goal, COUNT(*) as case_count,
                       AVG(processing_time) as avg_processing_time,
                       MIN(processing_time) as min_processing_time,
                       MAX(processing_time) as max_processing_time
                FROM case_processing
                WHERE created_at >= datetime('now', '-30 days')
                GROUP BY clinical_goal
            """)
            
            cases = []
            for row in cursor.fetchall():
                cases.append({
                    "clinical_goal": row[0],
                    "case_count": row[1],
                    "avg_processing_time": row[2],
                    "min_processing_time": row[3],
                    "max_processing_time": row[4]
                })
            
            self.report_data["case_processing"] = {
                "total_cases": sum(c["case_count"] for c in cases),
                "by_clinical_goal": cases
            }
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not collect case processing: {e}")
            self.report_data["case_processing"] = {"error": str(e)}
    
    def _collect_model_usage(self):
        """Collect AI model usage statistics"""
        try:
            # Read model registry
            registry_path = Path("compliance/model_registry.json")
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                
                self.report_data["model_usage"] = {
                    "models": registry.get("models", {}),
                    "rules": registry.get("rules", {}),
                    "system_version": registry.get("system", {}).get("version", "unknown")
                }
            else:
                self.report_data["model_usage"] = {"error": "Model registry not found"}
                
        except Exception as e:
            logger.warning(f"Could not collect model usage: {e}")
            self.report_data["model_usage"] = {"error": str(e)}
    
    def _collect_error_logs(self):
        """Collect error logs and exceptions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Error summary
            cursor.execute("""
                SELECT error_type, COUNT(*) as error_count,
                       MAX(timestamp) as last_occurrence
                FROM error_logs
                WHERE timestamp >= datetime('now', '-30 days')
                GROUP BY error_type
                ORDER BY error_count DESC
                LIMIT 10
            """)
            
            errors = []
            for row in cursor.fetchall():
                errors.append({
                    "error_type": row[0],
                    "error_count": row[1],
                    "last_occurrence": row[2]
                })
            
            self.report_data["error_logs"] = {
                "total_errors": sum(e["error_count"] for e in errors),
                "error_types": errors
            }
            
            conn.close()
            
        except Exception as e:
            logger.warning(f"Could not collect error logs: {e}")
            self.report_data["error_logs"] = {"error": str(e)}
    
    def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            # Performance targets from eval metrics
            metrics_path = Path("eval/metrics.yaml")
            if metrics_path.exists():
                import yaml
                with open(metrics_path, 'r') as f:
                    metrics = yaml.safe_load(f)
                
                self.report_data["performance_metrics"] = {
                    "targets": metrics.get("performance_targets", {}),
                    "quality_targets": metrics.get("quality_targets", {}),
                    "audit_requirements": metrics.get("audit_requirements", {})
                }
            else:
                self.report_data["performance_metrics"] = {"error": "Metrics file not found"}
                
        except Exception as e:
            logger.warning(f"Could not collect performance metrics: {e}")
            self.report_data["performance_metrics"] = {"error": str(e)}
    
    def _generate_summary(self, days: int):
        """Generate executive summary"""
        try:
            total_cases = self.report_data.get("case_processing", {}).get("total_cases", 0)
            success_rate = self.report_data.get("system_metrics", {}).get("success_rate", 0)
            total_errors = self.report_data.get("error_logs", {}).get("total_errors", 0)
            
            self.report_data["summary"] = {
                "report_period_days": days,
                "generated_at": datetime.now().isoformat(),
                "total_cases_processed": total_cases,
                "system_success_rate_percent": round(success_rate, 2),
                "total_errors": total_errors,
                "compliance_status": "compliant" if total_errors < 10 else "needs_attention",
                "recommendations": self._generate_recommendations()
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            self.report_data["summary"] = {"error": str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            # Check success rate
            success_rate = self.report_data.get("system_metrics", {}).get("success_rate", 0)
            if success_rate < 95:
                recommendations.append("System success rate below 95%. Review error logs and optimize error handling.")
            
            # Check error count
            total_errors = self.report_data.get("error_logs", {}).get("total_errors", 0)
            if total_errors > 50:
                recommendations.append("High error count detected. Implement error monitoring and alerting.")
            
            # Check processing times
            case_processing = self.report_data.get("case_processing", {})
            for case in case_processing.get("by_clinical_goal", []):
                avg_time = case.get("avg_processing_time", 0)
                if avg_time > 300:  # 5 minutes
                    recommendations.append(f"Slow processing for {case['clinical_goal']}. Consider optimization.")
            
            # Check model versions
            model_usage = self.report_data.get("model_usage", {})
            if "error" in model_usage:
                recommendations.append("Model registry not accessible. Ensure compliance tracking is active.")
            
            if not recommendations:
                recommendations.append("System performing well. Continue monitoring and regular audits.")
                
        except Exception as e:
            recommendations.append(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _format_csv(self) -> str:
        """Format report as CSV"""
        try:
            output = []
            
            # Summary section
            summary = self.report_data.get("summary", {})
            output.append(["SUMMARY"])
            output.append(["Metric", "Value"])
            for key, value in summary.items():
                if key != "recommendations":
                    output.append([key, str(value)])
            
            output.append([])
            
            # Recommendations
            output.append(["RECOMMENDATIONS"])
            for rec in summary.get("recommendations", []):
                output.append([rec])
            
            output.append([])
            
            # System metrics
            metrics = self.report_data.get("system_metrics", {})
            output.append(["SYSTEM METRICS"])
            output.append(["Metric", "Value"])
            for key, value in metrics.items():
                output.append([key, str(value)])
            
            output.append([])
            
            # Case processing
            cases = self.report_data.get("case_processing", {})
            output.append(["CASE PROCESSING"])
            output.append(["Clinical Goal", "Count", "Avg Time", "Min Time", "Max Time"])
            for case in cases.get("by_clinical_goal", []):
                output.append([
                    case.get("clinical_goal", ""),
                    case.get("case_count", 0),
                    case.get("avg_processing_time", 0),
                    case.get("min_processing_time", 0),
                    case.get("max_processing_time", 0)
                ])
            
            # Convert to CSV string
            csv_output = []
            for row in output:
                csv_output.append(",".join(f'"{cell}"' for cell in row))
            
            return "\n".join(csv_output)
            
        except Exception as e:
            logger.error(f"Error formatting CSV: {e}")
            return f"Error formatting CSV: {e}"

def main():
    parser = argparse.ArgumentParser(description="Generate NeuroPETRIX audit report")
    parser.add_argument("--days", type=int, default=30, help="Number of days to report on")
    parser.add_argument("--output-format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("--output-file", help="Output file path")
    
    args = parser.parse_args()
    
    try:
        reporter = AuditReporter()
        report = reporter.generate_report(days=args.days, output_format=args.output_format)
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                if args.output_format == "json":
                    json.dump(report, f, indent=2)
                else:
                    f.write(report)
            logger.info(f"Report saved to {args.output_file}")
        else:
            if args.output_format == "json":
                print(json.dumps(report, indent=2))
            else:
                print(report)
                
    except Exception as e:
        logger.error(f"Failed to generate audit report: {e}")
        exit(1)

if __name__ == "__main__":
    main()


