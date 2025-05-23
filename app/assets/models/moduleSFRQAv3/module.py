from pathlib import Path

from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class SFRQAv3Module(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(
        self,
        s: "Image.Image",          # side image (required)
        f: "Image.Image" = None,   # front image (optional)
        r: "Image.Image" = None,   # rear image (optional)
    ) -> dict[str, any]:
        """
        Run QA checks on the side image (required) plus optional front/rear images.
        Returns a dict of QA booleans/flags, skipping checks for any None images.
        """

        # Always do side QA since side image is required
        side_cow_present, stage2_output = self.detect_cow(s, is_side=True)
        is_side = self.detect_view(s, 2)  # e.g., '2' might correspond to a side view

        # Front QA checks only if we got a front image
        front_cow_present = None
        is_front = None
        if f is not None:
            front_cow_present = self.detect_cow(f)
            # If you want to confirm "front" view detection, pick the correct label below
            is_front = self.detect_view(f, 0)  # 0 might correspond to a front view

        # Rear QA checks only if we got a rear image
        rear_cow_present = None
        is_rear = None
        if r is not None:
            rear_cow_present = self.detect_cow(r)
            # If you want to confirm "rear" view detection, pick the correct label below
            is_rear = self.detect_view(r, 1)  # 1 might correspond to a rear view

        return {
            "front-cow-present": front_cow_present,
            "side-cow-present": side_cow_present,
            "rear-cow-present": rear_cow_present,
            "side-cow-stage2": stage2_output,
            "is-front": is_front,
            "is-side": is_side,
            "is-rear": is_rear,
        }

    def detect_cow(self, img, is_side=False):
        """
        Detect whether a cow/horse/elephant is present in `img`.
        If is_side=True, run a second classification (model2) to confirm species
        and return a tuple: (True/False, 'speciesName' or None).
        Otherwise, return a simple boolean.
        """
        if img is None:
            # Return None if the image wasn't provided (or cannot be processed).
            # If is_side=True, return a (None, None) tuple for consistency.
            return (None, None) if is_side else None

        results = self.model(img)
        for result in results:
            if len(result.boxes.conf) and result.boxes.conf[0] > 0.5:
                class_ids = result.boxes.cls.tolist()
                detected_classes = [
                    self.model.names[int(class_id)] for class_id in class_ids
                ]
                # If we detect any of these classes, we consider it a "cow present"
                if any(c in detected_classes for c in ["cow"]):
                    if is_side:
                        qa_out = self.model2(img)[0]
                        return (
                            qa_out.probs.top1 == 1 or qa_out.probs.top1 == 0,
                            self.model2.names[qa_out.probs.top1],
                        )
                    return True

        # If we got here, no cow or other large animal was detected
        return (False, None) if is_side else False

    def detect_view(self, img, view_label: int) -> bool:
        """
        Runs model3 to classify the image view.
        If the top predicted label matches `view_label`, return True.
        """
        if img is None:
            return False
        result = self.model3(img)[0]
        return (result.probs.top1 == view_label)

    def __enter__(self):
        """
        Load all necessary YOLO models upon entering the context.
        """
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
        """
        Clean up references to the YOLO models when exiting the context.
        """
        del self.model
        del self.model2
        del self.model3
