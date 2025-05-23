from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule
from ..utils import getClassName


class CleftStatusModule(ApiModule):
    def __init__(self, *args, **kwargs):
        pass

    def run(self, r: "Image.Image") -> dict[str, any]:
        results = self.model.predict(r, imgsz=640, verbose=False)
        out = getClassName(results)
        return {"cleft-status": out if out else "Null"}

    def __enter__(self):
        self.model = YOLO(str(Path(__file__).parent / "model_openvino_model"), task="detect", verbose=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
