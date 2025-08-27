import sys
from pathlib import Path

_here = Path(__file__).resolve()
_project_root = _here.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


