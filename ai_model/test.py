import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

# OpenMP 라이브러리 충돌 해결
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO


PROJECT_ROOT = Path(r"c:\Users\user\Desktop\major_project_road")

MODEL_PATH = PROJECT_ROOT / "runs" / "animal_detector_yolov8n" / "weights" / "last.pt"

TEST_IMAGE_DIR = PROJECT_ROOT / "test"

# 결과 이미지 저장 경로
PREDICT_OUTPUT_DIR = PROJECT_ROOT / "runs" / "animal_detector_test"

CONF_THRESHOLD = 0.3

CLASS_NAMES: Dict[int, str] = {
    0: "gorani",
    1: "wild_boar",
    2: "raccoon",
}


def xyxy_to_normalized_bbox(
    xyxy,
    image_width: int,
    image_height: int,
) -> Dict[str, float]:
    x_min, y_min, x_max, y_max = map(float, xyxy)

    box_w = x_max - x_min
    box_h = y_max - y_min

    x_center = x_min + box_w / 2.0
    y_center = y_min + box_h / 2.0

    return {
        "x": round(x_center / image_width, 6),
        "y": round(y_center / image_height, 6),
        "width": round(box_w / image_width, 6),
        "height": round(box_h / image_height, 6),
    }


def build_event_metadata(
    image_path: Path,
    species: str,
    confidence: float,
    bbox: Dict[str, float],
    image_width: int,
    image_height: int,
) -> Dict:
    return {
        "objectType": "ANIMAL",
        "species": species,
        "confidence": round(float(confidence), 6),
        "bbox": bbox,
        "imageFileName": image_path.name,
        "imageWidth": image_width,
        "imageHeight": image_height,
        "detectedAt": datetime.now(timezone.utc).isoformat(),
    }


def collect_test_images(test_dir: Path) -> List[Path]:
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    if test_dir.is_file() and test_dir.suffix.lower() in image_exts:
        return [test_dir]

    if not test_dir.exists():
        raise FileNotFoundError(f"테스트 이미지 경로가 없습니다: {test_dir}")

    return [
        p for p in test_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in image_exts
    ]


def test_model() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"학습된 모델 best.pt가 없습니다: {MODEL_PATH}")

    model = YOLO(str(MODEL_PATH))

    test_images = collect_test_images(TEST_IMAGE_DIR)

    if not test_images:
        raise RuntimeError(f"테스트 이미지가 없습니다: {TEST_IMAGE_DIR}")

    print(f"[INFO] 테스트 이미지 수: {len(test_images)}")

    all_events = []

    for image_path in test_images:
        results = model.predict(
            source=str(image_path),
            conf=CONF_THRESHOLD,
            save=True,
            project=str(PREDICT_OUTPUT_DIR),
            name="predictions",
            exist_ok=True,
            verbose=False,
        )

        image_events = []

        for result in results:
            image_height, image_width = result.orig_shape

            if result.boxes is None or len(result.boxes) == 0:
                continue

            for box in result.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())

                if confidence < CONF_THRESHOLD:
                    continue

                species = CLASS_NAMES.get(class_id, "unknown")

                xyxy = box.xyxy[0].tolist()
                bbox = xyxy_to_normalized_bbox(
                    xyxy=xyxy,
                    image_width=image_width,
                    image_height=image_height,
                )

                event_metadata = build_event_metadata(
                    image_path=image_path,
                    species=species,
                    confidence=confidence,
                    bbox=bbox,
                    image_width=image_width,
                    image_height=image_height,
                )

                image_events.append(event_metadata)
                all_events.append(event_metadata)

        if image_events:
            print(f"\n[DETECTED] {image_path.name}")
            print(json.dumps(image_events, ensure_ascii=False, indent=2))
        else:
            print(f"[NO ANIMAL] {image_path.name}")

    output_json_path = PREDICT_OUTPUT_DIR / "detected_events.json"
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(all_events, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n[INFO] 전체 감지 이벤트 수: {len(all_events)}")
    print(f"[INFO] 예측 이미지 저장 위치: {PREDICT_OUTPUT_DIR / 'predictions'}")
    print(f"[INFO] 이벤트 JSON 저장 위치: {output_json_path}")


if __name__ == "__main__":
    test_model()