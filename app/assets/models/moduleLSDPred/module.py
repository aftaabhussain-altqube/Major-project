from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class LSDPredModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, s: "Image.Image") -> dict[str, any]:
        results = self.model.predict(s, verbose=False)
        out = self.model.names[results[0].probs.top1]
        if out == 'Normal Skin': out = "healthy"
        return {"lsd-pred": out}

    def __enter__(self):
        self.model = YOLO(
            str(Path(__file__).parent / "model" / "lsd.pt"), task="classify", verbose=False
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
