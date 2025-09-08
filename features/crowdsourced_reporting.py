"""
Crowdsourced Reporting Module for INGRES AI Chatbot
Handles user-submitted water quality reports and community data
"""

import json
from datetime import datetime
import uuid

class CrowdsourcedReporting:
    def __init__(self):
        self.reports = []
        self.report_categories = [
            "Water Level Change",
            "Quality Issue",
            "Well Status",
            "Contamination",
            "Seasonal Variation",
            "Infrastructure Problem"
        ]
    
    def submit_report(self, user_data):
        """Submit a new crowdsourced report"""
        report = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "location": user_data.get("location", ""),
            "coordinates": user_data.get("coordinates", [0, 0]),
            "category": user_data.get("category", "General"),
            "description": user_data.get("description", ""),
            "water_level": user_data.get("water_level"),
            "quality_rating": user_data.get("quality_rating", 3),
            "photos": user_data.get("photos", []),
            "contact": user_data.get("contact", ""),
            "verified": False,
            "votes": 0
        }
        
        self.reports.append(report)
        
        return {
            "success": True,
            "report_id": report["id"],
            "message": "Report submitted successfully. Thank you for contributing to community water monitoring!",
            "verification_pending": True
        }
    
    def get_reports_by_location(self, location, radius_km=10):
        """Get reports near a specific location"""
        # Simple location matching - in production would use geospatial queries
        nearby_reports = [
            report for report in self.reports
            if location.lower() in report["location"].lower()
        ]
        
        return {
            "reports": nearby_reports,
            "total": len(nearby_reports),
            "location": location,
            "radius_km": radius_km
        }
    
    def get_report_categories(self):
        """Get available report categories"""
        return self.report_categories
    
    def verify_report(self, report_id, verified_by="system"):
        """Verify a crowdsourced report"""
        for report in self.reports:
            if report["id"] == report_id:
                report["verified"] = True
                report["verified_by"] = verified_by
                report["verified_at"] = datetime.now().isoformat()
                return {"success": True, "message": "Report verified"}
        
        return {"success": False, "message": "Report not found"}
    
    def get_community_stats(self):
        """Get community reporting statistics"""
        total_reports = len(self.reports)
        verified_reports = len([r for r in self.reports if r.get("verified", False)])
        
        return {
            "total_reports": total_reports,
            "verified_reports": verified_reports,
            "verification_rate": (verified_reports / total_reports * 100) if total_reports > 0 else 0,
            "categories": self.report_categories,
            "recent_reports": self.reports[-5:] if self.reports else []
        }

# Global crowdsourced reporting instance
crowdsourced_reporting = CrowdsourcedReporting()