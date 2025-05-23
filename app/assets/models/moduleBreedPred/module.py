from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class BreedPredModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, s: "Image.Image") -> dict[str, any]:
        out = None
        results = self.model.predict(s, verbose=False)
        if results[0].probs.top1conf > 0.65:
            out = self.model.names[results[0].probs.top1]
        else:
            out = "Cow-Non-Descript-Breed"
        return {"breed": out}

    def __enter__(self):
        self.model = YOLO(str(Path(__file__).parent / "model" / "breed1.pt"), task="classify", verbose=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
