import os
from dataclasses import dataclass
from pathlib import Path


os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

MODEL_PATH = Path("ai_model/runs/animal_detector_yolov8n/weights/best.pt")
CONFIDENCE_THRESHOLD = 0.3

CLASS_NAMES = {
    0: "gorani",
    1: "wild_boar",
    2: "raccoon",
}


@dataclass(frozen=True)
class DetectedObject:
    species: str
    confidence: float
    bbox_x: float
    bbox_y: float
    bbox_width: float
    bbox_height: float


class YoloDetector:
    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ) -> None:
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._model = None

    def detect(self, image_path: Path) -> list[DetectedObject]:
        model = self._load_model()
        results = model.predict(
            source=str(image_path),
            conf=self.confidence_threshold,
            save=False,
            verbose=False,
        )

        detected_objects: list[DetectedObject] = []
        for result in results:
            image_height, image_width = result.orig_shape
            if result.boxes is None or len(result.boxes) == 0:
                continue

            for box in result.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                if confidence < self.confidence_threshold:
                    continue

                species = CLASS_NAMES.get(class_id)
                if species is None:
                    continue

                bbox = _xyxy_to_top_left_percent_bbox(
                    xyxy=box.xyxy[0].tolist(),
                    image_width=image_width,
                    image_height=image_height,
                )
                detected_objects.append(
                    DetectedObject(
                        species=species,
                        confidence=round(confidence, 6),
                        bbox_x=bbox["x"],
                        bbox_y=bbox["y"],
                        bbox_width=bbox["width"],
                        bbox_height=bbox["height"],
                    )
                )

        return detected_objects

    def _load_model(self):
        if self._model is not None:
            return self._model

        if not self.model_path.exists():
            raise FileNotFoundError(f"YOLO model file not found: {self.model_path}")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "ultralytics is required for YOLO inference. "
                "Install project dependencies and rebuild the Docker image."
            ) from exc

        self._model = YOLO(str(self.model_path))
        return self._model


def _xyxy_to_top_left_percent_bbox(
    xyxy: list[float],
    image_width: int,
    image_height: int,
) -> dict[str, float]:
    x_min, y_min, x_max, y_max = map(float, xyxy)

    box_width = x_max - x_min
    box_height = y_max - y_min

    return {
        "x": _clamp_percent((x_min / image_width) * 100),
        "y": _clamp_percent((y_min / image_height) * 100),
        "width": _clamp_percent((box_width / image_width) * 100),
        "height": _clamp_percent((box_height / image_height) * 100),
    }


def _clamp_percent(value: float) -> float:
    return round(min(max(value, 0.0), 100.0), 6)
