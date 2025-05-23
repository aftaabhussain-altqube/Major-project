import os
from pathlib import Path

import cv2
from PIL import Image
from ultralytics import YOLO

from ..module import ApiModule


class RuminationModule(ApiModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, video, frame_step: int = 3) -> dict[str, any]:
        if not video: return {"rumination-count": None}

        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / fps

        if video_duration < 15:
            video.release()
            return {"rumination-count": None}

        effective_fps = fps / frame_step

        chews_count = 0
        previous_state = "open"

        frame_idx = 0
        max_duration = 30
        max_frames = int(max_duration * effective_fps)
        processed_duration = 0

        timestamps = []
        states = []

        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                print("No frames read, breaking loop.")
                break

            if frame_idx % frame_step == 0:
                results = self.model(frame, imgsz=1280, task="predict", verbose=False)

                max_conf = 0
                current_state = "open"  # Default assumption
                for result in results:
                    best_box = None
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = box.conf[0]
                        cls = int(box.cls[0])
                        label = self.model.names[cls]

                        if conf > max_conf:
                            max_conf = conf
                            best_box = (x1, y1, x2, y2)
                            best_label = label.lower()

                    if best_box and max_conf >= 0.7:
                        x1, y1, x2, y2 = best_box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            label,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )

                        if best_label == "close":
                            current_state = "close"
                            break  # We only need the first 'closed' state per frame

                if current_state == "close" and previous_state == "open":
                    chews_count += 1
                previous_state = current_state  # Update the state for the next frame

                timestamp = frame_idx / effective_fps
                timestamps.append(timestamp)
                states.append(current_state)

            frame_idx += 1
            processed_duration = frame_idx / effective_fps

            if frame_idx >= max_frames:
                print(
                    f"Processed duration has reached {max_duration} seconds, stopping inference..."
                )
                break

        video.release()
        cv2.destroyAllWindows()

        chews_per_minute = (
            (chews_count / processed_duration) * frame_step * 60
            if processed_duration > 0
            else 0
        )

        out = None
        if chews_per_minute > 40:
            out = "Good"
        elif chews_per_minute > 20:
            out = "Fair"
        elif chews_per_minute >= 0:
            out = "Poor"

        return {"rumination-count": out if out else "Null"}

    def __enter__(self):
        self.model = YOLO(
            str(Path(__file__).parent / "model" / "rumination2.pt"), task="detect", verbose=False
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
