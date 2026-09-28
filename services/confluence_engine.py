import sys
import os
import importlib.util

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

target_file = os.path.join(backend_dir, "services", "confluence_engine.py")
spec = importlib.util.spec_from_file_location("backend_services_confluence", target_file)
mod = importlib.util.module_from_spec(spec)
sys.modules["backend_services_confluence"] = mod
spec.loader.exec_module(mod)

for attr in dir(mod):
    if not attr.startswith("__"):
        globals()[attr] = getattr(mod, attr)
