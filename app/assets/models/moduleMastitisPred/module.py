from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class MastitisPredModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, udder_type: str, teat_score: str) -> dict[str, any]:
        out = "healthy"
        if udder_type in ("Udder-Pendulous", "Udder-Balloon-Shaped"):
            if teat_score in ("Teat-Score-1", "Teat-Score-3"):
                out = "Mastitis"
        return {"mastitis-pred": out}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
