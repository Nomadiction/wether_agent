import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class WeatherAgentDashboard:
    def __init__(self, metrics_dir: str = "metrics", output_dir: str = "dashboard"):
        self.metrics_dir = Path(metrics_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.requests_file = self.metrics_dir / "requests.csv"
        self.feedback_file = self.metrics_dir / "feedback.csv"
        self.errors_file = self.metrics_dir / "errors.csv"

    def load_data(self) -> Dict[str, pd.DataFrame]:
        data = {}
        if self.requests_file.exists():
            df = pd.read_csv(self.requests_file)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            data["requests"] = df
        if self.feedback_file.exists():
            df = pd.read_csv(self.feedback_file)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            data["feedback"] = df
        if self.errors_file.exists():
            df = pd.read_csv(self.errors_file)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            data["errors"] = df
        return data

    def generate_summary_report(self) -> Dict[str, Any]:
        data = self.load_data()
        report = {"generated_at": datetime.now().isoformat(), "period": "all_time", "metrics": {}}
        if "requests" in data:
            df = data["requests"]
            report["metrics"]["requests"] = {
                "total_requests": len(df),
                "successful_requests": int(df["weather_found"].sum()),
                "failed_requests": int((~df["weather_found"]).sum()),
                "success_rate": float(df["weather_found"].mean() * 100.0) if len(df) else 0.0,
                "avg_response_time_ms": float(df["response_time_ms"].mean()) if len(df) else 0.0,
                "top_cities": df["city_extracted"].value_counts().head(10).to_dict() if "city_extracted" in df else {},
            }
        if "feedback" in data:
            df = data["feedback"]
            report["metrics"]["feedback"] = {
                "total_feedback": len(df),
                "avg_rating": float(df["rating"].mean()) if len(df) else 0.0,
                "rating_distribution": df["rating"].value_counts().to_dict() if "rating" in df else {},
            }
        if "errors" in data:
            df = data["errors"]
            report["metrics"]["errors"] = {
                "total_errors": len(df),
                "error_types": df["error_type"].value_counts().to_dict() if "error_type" in df else {},
                "recent_errors": df.tail(5).to_dict("records") if len(df) else [],
            }
        return report

    def _save_line(self, x, y, path: Path, title: str, xlabel: str, ylabel: str):
        plt.figure(figsize=(10, 5))
        plt.plot(x, y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(path, dpi=200, bbox_inches="tight")
        plt.close()

    def _save_bar(self, labels, values, path: Path, title: str, xlabel: str, ylabel: str):
        plt.figure(figsize=(10, 6))
        bars = plt.bar(labels, values)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        for b, v in zip(bars, values):
            plt.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom")
        plt.tight_layout()
        plt.savefig(path, dpi=200, bbox_inches="tight")
        plt.close()

    def _save_hist(self, values, path: Path, title: str, xlabel: str, bins: int = 30):
        plt.figure(figsize=(10, 6))
        plt.hist(values, bins=bins)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(path, dpi=200, bbox_inches="tight")
        plt.close()

    def create_visualizations(self):
        data = self.load_data()
        if "requests" in data:
            df = data["requests"]
            # по дням
            daily = df.groupby(df["timestamp"].dt.date).size()
            self._save_line(daily.index, daily.values, self.output_dir / "daily_requests.png",
                            "Daily Requests", "Date", "Requests")
            # топ городов
            if "city_extracted" in df and not df["city_extracted"].isna().all():
                top = df["city_extracted"].value_counts().head(10)
                self._save_bar(top.index.tolist(), top.values.tolist(), self.output_dir / "top_cities.png",
                               "Top 10 Cities", "City", "Requests")
            # время ответа
            self._save_hist(df["response_time_ms"].astype(float).tolist(),
                            self.output_dir / "response_time_distribution.png",
                            "Response Time Distribution", "Response Time (ms)")
        if "feedback" in data:
            fb = data["feedback"]
            if not fb.empty:
                counts = fb["rating"].value_counts().sort_index()
                self._save_bar([str(x) for x in counts.index.tolist()], counts.values.tolist(),
                               self.output_dir / "feedback_ratings.png",
                               "Ratings Distribution", "Rating", "Count")
        if "errors" in data:
            err = data["errors"]
            if "error_type" in err and not err.empty:
                counts = err["error_type"].value_counts()
                self._save_bar(counts.index.tolist(), counts.values.tolist(),
                               self.output_dir / "error_types.png",
                               "Error Types", "Type", "Count")

    def generate_html_report(self) -> Path:
        report = self.generate_summary_report()
        self.create_visualizations()
        html = f"""
                    <!DOCTYPE html>
                    <html><head><meta charset="utf-8"><title>Weather Agent Dashboard</title>
                    <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .card {{ background:#fff;border:1px solid #ddd;border-radius:8px;padding:16px;margin:12px 0; }}
                    .value {{ font-size:22px;font-weight:700;color:#0b6; }}
                    h1 {{ margin-bottom:6px; }}
                    img {{ max-width:100%; height:auto; }}
                    </style></head><body>
                    <h1>🌤️ Weather Agent Dashboard</h1>
                    <p>Generated at: {report['generated_at']}</p>

                    <div class="card">
                    <h2>📊 Requests</h2>
                    <p><span class="value">{report['metrics'].get('requests',{}).get('total_requests',0)}</span> total</p>
                    <p><span class="value">{report['metrics'].get('requests',{}).get('successful_requests',0)}</span> success</p>
                    <p><span class="value">{report['metrics'].get('requests',{}).get('success_rate',0):.1f}%</span> success rate</p>
                    <p><span class="value">{report['metrics'].get('requests',{}).get('avg_response_time_ms',0):.1f} ms</span> avg latency</p>
                    </div>

                    <div class="card">
                    <h2>⭐ Feedback</h2>
                    <p><span class="value">{report['metrics'].get('feedback',{}).get('total_feedback',0)}</span> total</p>
                    <p><span class="value">{report['metrics'].get('feedback',{}).get('avg_rating',0):.1f}</span> avg rating</p>
                    </div>

                    <div class="card">
                    <h2>❌ Errors</h2>
                    <p><span class="value">{report['metrics'].get('errors',{}).get('total_errors',0)}</span> total</p>
                    </div>

                    <h3>📈 Daily Requests</h3><img src="daily_requests.png" alt="Daily Requests"/>
                    <h3>🏙️ Top Cities</h3><img src="top_cities.png" alt="Top Cities"/>
                    <h3>⏱️ Response Time Distribution</h3><img src="response_time_distribution.png" alt="Response Time"/>
                    <h3>⭐ Ratings</h3><img src="feedback_ratings.png" alt="Ratings"/>
                    <h3>🔧 Error Types</h3><img src="error_types.png" alt="Errors"/>
                    </body></html>
                """
        out = self.output_dir / "dashboard.html"
        out.write_text(html, encoding="utf-8")
        return out
