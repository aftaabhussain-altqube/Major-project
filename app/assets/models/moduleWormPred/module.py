from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule
from ..utils import getClassName


class WormPredModule(ApiModule):
    def __init__(self, *args, **kwargs):
        pass

    def run(self, s: "Image.Image") -> dict[str, any]:
        results = self.model.predict(s, imgsz=1280, verbose=False)
        out = getClassName(results)
        return {"worm-load": out if out else "Null"}

    def __enter__(self):
        self.model = YOLO(str(Path(__file__).parent / "model_openvino_model"), task="detect", verbose=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
