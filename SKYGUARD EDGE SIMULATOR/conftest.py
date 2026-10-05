import sys
from pathlib import Path

# Add edge simulator root directory to sys.path for test discovery
sim_root = str(Path(__file__).resolve().parent)
if sim_root not in sys.path:
    sys.path.insert(0, sim_root)
