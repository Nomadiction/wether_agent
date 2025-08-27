import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class MetricsCollector:
    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        self.requests_file = self.metrics_dir / "requests.csv"
        self.feedback_file = self.metrics_dir / "feedback.csv"
        self.errors_file = self.metrics_dir / "errors.csv"
        self._init_csv_files()

    def _init_csv_files(self):
        if not self.requests_file.exists():
            with open(self.requests_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([
                    "timestamp","session_id","message","response",
                    "response_time_ms","city_extracted","weather_found"
                ])
        if not self.feedback_file.exists():
            with open(self.feedback_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp","session_id","message","rating","feedback_text","response_quality"])
        if not self.errors_file.exists():
            with open(self.errors_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp","session_id","error_type","error_message","request_data"])

    def log_request(self, session_id: str, message: str, response: str, response_time_ms: float,
                    city_extracted: str, weather_found: bool):
        with open(self.requests_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(), session_id, message, response,
                response_time_ms, city_extracted, weather_found
            ])

    def log_feedback(self, session_id: str, message: str, rating: int,
                     feedback_text: str = "", response_quality: str = "good"):
        with open(self.feedback_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(), session_id, message, rating, feedback_text, response_quality
            ])

    def log_error(self, session_id: str, error_type: str, error_message: str, request_data: Dict[str, Any]):
        with open(self.errors_file, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                datetime.now().isoformat(), session_id, error_type, error_message,
                json.dumps(request_data, ensure_ascii=False)
            ])

    def get_metrics_summary(self) -> Dict[str, Any]:
        # Мини-сводка для /metrics
        summary = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "top_cities": {},
            "feedback_stats": {},
            "recent_errors": [],
        }
        # Requests
        if self.requests_file.exists():
            response_times = []
            rows = []
            with open(self.requests_file, "r", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                for row in rdr:
                    rows.append(row)
                    summary["total_requests"] += 1
                    ok = row["weather_found"] == "True"
                    if ok:
                        summary["successful_requests"] += 1
                    else:
                        summary["failed_requests"] += 1
                    response_times.append(float(row["response_time_ms"]))
                    city = row["city_extracted"].strip()
                    if city:
                        summary["top_cities"][city] = summary["top_cities"].get(city, 0) + 1
            if response_times:
                summary["avg_response_time"] = sum(response_times) / len(response_times)
        # Feedback
        if self.feedback_file.exists():
            ratings = []
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                for row in rdr:
                    ratings.append(int(row["rating"]))
            if ratings:
                summary["feedback_stats"] = {"avg_rating": sum(ratings)/len(ratings), "total_feedback": len(ratings)}
        # Errors (последние 10)
        if self.errors_file.exists():
            with open(self.errors_file, "r", encoding="utf-8") as f:
                rdr = list(csv.DictReader(f))
                summary["recent_errors"] = rdr[-10:]
        return summary
