import argparse
from pathlib import Path
import sys
from pathlib import Path as _Path

_here = _Path(__file__).resolve()
_project_root = _here.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.dashboard.dashboard import WeatherAgentDashboard

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metrics-dir", default="metrics")
    p.add_argument("--output-dir", default="dashboard")
    args = p.parse_args()

    dash = WeatherAgentDashboard(metrics_dir=args.metrics_dir, output_dir=args.output_dir)
    out = dash.generate_html_report()
    print(f"OK: dashboard -> {Path(out).absolute()}")

if __name__ == "__main__":
    main()
