from pathlib import Path
from typing import Literal

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class BreedGradeModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, s: "Image.Image") -> dict[str, any]:
        if self.breed == "Cow-Non-Descript-Breed":
            return {"breed-grade": "Breed-Grade-C"}
        results = self.model.predict(s, verbose=False)
        if self.model_name == "gir" or self.model_name == "sahiwal" and results[0].probs.top1conf <= 0.4:
            out = "Breed-Grade-B"
        out = self.model.names[results[0].probs.top1]
        return {"breed-grade": out}

    def __call__(
            self,
            breed: Literal["Cow-Gir", "Cow-HF-Crossbreed", "Cow-Jersey-Crossbreed", "Cow-Sahiwal"]
    ) -> "BreedGradeModule":
        breed_model_dict = {
            "Cow-HF-Crossbreed": "hf",
            "Cow-Jersey-Crossbreed": "jersey",
            "Cow-Gir": "gir",
            "Cow-Sahiwal": "sahiwal"
        }
        self.breed = breed
        self.model_name = breed_model_dict.get(breed, "hf")
        return self

    def __enter__(self) -> "BreedGradeModule":
        self.model = YOLO(str(Path(__file__).parent / "models" / f"{self.model_name}.pt"), task="classify",
                          verbose=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
        self.breed = None
