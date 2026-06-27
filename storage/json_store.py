import json
from pathlib import Path
from config import DATA_DIR
class JsonStore:
    def __init__(self, name: str, default):
        DATA_DIR.mkdir(parents=True, exist_ok=True); self.path = DATA_DIR / name; self.default = default
        if not self.path.exists(): self.write(default)
    def read(self):
        try: return json.loads(self.path.read_text())
        except Exception: return self.default
    def write(self, value):
        self.path.write_text(json.dumps(value, indent=2, sort_keys=True))
