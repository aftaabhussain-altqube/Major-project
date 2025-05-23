from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule
from ..utils import getClassName


class ScrotumPredModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, s: "Image.Image") -> dict[str, any]:
        results = self.model.predict(s, verbose=False)
        out = getClassName(results)
        return {"scrotum": out == "scrotum"}

    def __enter__(self):
        self.model = YOLO(str(Path(__file__).parent / "model" / "scrotum.pt"), task="detect", verbose=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
