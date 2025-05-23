from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class SFRQAModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(
        self, f: "Image.Image", s: "Image.Image", r: "Image.Image"
    ) -> dict[str, any]:
        side_cow_present, stage2_output = self.detect_cow(s, is_side=True)
        return {
            "front-cow-present": self.detect_cow(f),
            "side-cow-present": side_cow_present,
            "rear-cow-present": self.detect_cow(r),
            "side-cow-stage2": stage2_output,
            "is-front": True,
            "is-side": self.detect_view(s, 2),
            "is-rear": True,
        }

    def detect_cow(self, img, is_side=False) -> bool | tuple[bool, str]:
        results = self.model(img)
        for result in results:
            class_ids = None
            if len(result.boxes.conf) and result.boxes.conf[0] > 0.5:
                class_ids = result.boxes.cls.tolist()
                detected_classes = [
                    self.model.names[int(class_id)] for class_id in class_ids
                ]
                if any(c in detected_classes for c in ["cow", "horse", "elephant"]):
                    if is_side:
                        qa_out = self.model2(img)[0]
                        return (
                            qa_out.probs.top1 == 1 or qa_out.probs.top1 == 0,
                            self.model2.names[qa_out.probs.top1],
                        )
                    return True
        return False if not is_side else (False, None)

    def detect_view(self, img, view_label: int) -> bool:
        return self.model3(img)[0].probs.top1 == view_label

    def __enter__(self):
        self.model = YOLO(
            str(Path(__file__).parent / "model" / "yolo11n.pt"),
            task="detect",
            verbose=False,
        )
        self.model2 = YOLO(
            str(Path(__file__).parent / "model" / "cow_horse_elephant_buffalo.pt"),
            task="classify",
            verbose=False,
        )
        self.model3 = YOLO(
            str(Path(__file__).parent / "model" / "cow_view_qa.pt"),
            task="classify",
            verbose=False,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
        del self.model2
        del self.model3
