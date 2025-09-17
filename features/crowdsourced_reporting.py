import json
from datetime import datetime
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

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
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.kmeans = None
        self.n_clusters = 3  # You can tune this

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
            "votes": 0,
            "cluster": None  # ML cluster assignment
        }
        self.reports.append(report)
        self._update_clusters()
        return {
            "success": True,
            "report_id": report["id"],
            "message": "Report submitted successfully. Thank you for contributing to community water monitoring!",
            "verification_pending": True,
            "cluster": report["cluster"]
        }

    def _update_clusters(self):
        """Apply unsupervised ML clustering to group similar reports by description"""
        if len(self.reports) < self.n_clusters:
            return  # Not enough data to cluster
        descriptions = [r["description"] for r in self.reports]
        X = self.vectorizer.fit_transform(descriptions)
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        clusters = self.kmeans.fit_predict(X)
        for idx, report in enumerate(self.reports):
            report["cluster"] = int(clusters[idx])

    def get_reports_by_location(self, location, radius_km=10):
        """Get reports near a specific location"""
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
        """Get community reporting statistics, including ML clusters"""
        total_reports = len(self.reports)
        verified_reports = len([r for r in self.reports if r.get("verified", False)])
        cluster_counts = {}
        for r in self.reports:
            c = r.get("cluster")
            if c is not None:
                cluster_counts[c] = cluster_counts.get(c, 0) + 1
        return {
            "total_reports": total_reports,
            "verified_reports": verified_reports,
            "verification_rate": (verified_reports / total_reports * 100) if total_reports > 0 else 0,
            "categories": self.report_categories,
            "recent_reports": self.reports[-5:] if self.reports else [],
            "cluster_distribution": cluster_counts
        }

# Global crowdsourced reporting instance
crowdsourced_reporting = CrowdsourcedReporting()