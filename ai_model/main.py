import json
import os
import random
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# OpenMP 라이브러리 충돌 해결
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from ultralytics import YOLO


# =========================
# 기본 경로 설정
# =========================

PROJECT_ROOT = Path(r"c:\Users\user\Desktop\major_project_road")
DATA_DIR = PROJECT_ROOT / "01. 데이터"

# 훈련 및 검증 데이터 경로
TRAIN_LABEL_DIR = DATA_DIR / "1.Training" / "라벨링데이터"
TRAIN_IMAGE_DIR = DATA_DIR / "1.Training" / "원천데이터"
VAL_LABEL_DIR = DATA_DIR / "2.Validation" / "라벨링데이터"
VAL_IMAGE_DIR = DATA_DIR / "2.Validation" / "원천데이터"

# RAW_LABEL_DIR과 RAW_IMAGE_DIR은 모든 species 폴더의 파일을 포함
RAW_LABEL_DIR = DATA_DIR  # rglob으로 재귀적으로 모든 JSON 찾기
RAW_IMAGE_DIR = DATA_DIR  # rglob으로 재귀적으로 모든 JPG 찾기

YOLO_DATASET_DIR = DATA_DIR / "yolo_animals"

TRAIN_RATIO = 0.8
RANDOM_SEED = 42

# AIHub species 값 기준 매핑
# JSON 안 species가 "고라니", "멧돼지", "너구리"라고 들어있다고 가정
CLASS_MAP: Dict[str, int] = {
    "고라니": 0,
    "멧돼지": 1,
    "너구리": 2,
}

CLASS_NAMES: Dict[int, str] = {
    0: "gorani",
    1: "wild_boar",
    2: "raccoon",
}


# =========================
# 유틸
# =========================

def make_yolo_dirs() -> None:
    for split in ["train", "val"]:
        (YOLO_DATASET_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (YOLO_DATASET_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)


def build_image_index(image_dir: Path) -> Dict[str, Path]:
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    index: Dict[str, Path] = {}

    for path in image_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in image_exts:
            index[path.name] = path

    print(f"[INFO] 원천 이미지 인덱스 생성 완료: {len(index)}개")
    return index


def convert_bbox_aihub_to_yolo(
    bbox: List[List[float]],
    image_width: int,
    image_height: int,
) -> Optional[Tuple[float, float, float, float]]:
    """
    AIHub bbox:
      [[x_min, y_min], [x_max, y_max]]

    YOLO bbox:
      x_center y_center width height
      전부 0~1 정규화
    """

    try:
        x_min, y_min = bbox[0]
        x_max, y_max = bbox[1]

        x_min = max(0.0, min(float(x_min), float(image_width)))
        x_max = max(0.0, min(float(x_max), float(image_width)))
        y_min = max(0.0, min(float(y_min), float(image_height)))
        y_max = max(0.0, min(float(y_max), float(image_height)))

        box_w = x_max - x_min
        box_h = y_max - y_min

        if box_w <= 0 or box_h <= 0:
            return None

        x_center = x_min + box_w / 2.0
        y_center = y_min + box_h / 2.0

        return (
            x_center / image_width,
            y_center / image_height,
            box_w / image_width,
            box_h / image_height,
        )

    except Exception:
        return None


def parse_aihub_json(json_path: Path) -> Optional[Dict]:
    """
    AIHub 라벨 JSON 하나를 읽어서 YOLO 변환에 필요한 정보만 추출.
    """

    try:
        with json_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except UnicodeDecodeError:
        with json_path.open("r", encoding="cp949") as f:
            data = json.load(f)

    images = data.get("images", [])
    annotations = data.get("annotations", [])

    if not images:
        return None

    image_info = images[0]

    file_name = image_info.get("file_name")
    image_width = image_info.get("width")
    image_height = image_info.get("height")

    if not file_name or not image_width or not image_height:
        return None

    image_width = int(image_width)
    image_height = int(image_height)

    yolo_labels = []

    for ann in annotations:
        species = ann.get("species")
        bbox = ann.get("bbox")

        if species not in CLASS_MAP:
            continue

        if not bbox:
            continue

        class_id = CLASS_MAP[species]

        converted = convert_bbox_aihub_to_yolo(
            bbox=bbox,
            image_width=image_width,
            image_height=image_height,
        )

        if converted is None:
            continue

        x, y, w, h = converted
        yolo_labels.append((class_id, x, y, w, h))

    if not yolo_labels:
        return None

    return {
        "file_name": file_name,
        "labels": yolo_labels,
    }


def write_yolo_label(label_path: Path, labels: List[Tuple[int, float, float, float, float]]) -> None:
    with label_path.open("w", encoding="utf-8") as f:
        for class_id, x, y, w, h in labels:
            f.write(f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def write_data_yaml() -> None:
    yaml_path = YOLO_DATASET_DIR / "data.yaml"

    lines = [
        f"path: {YOLO_DATASET_DIR.resolve()}",
        "train: images/train",
        "val: images/val",
        "",
        "names:",
    ]

    for class_id, class_name in CLASS_NAMES.items():
        lines.append(f"  {class_id}: {class_name}")

    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[INFO] data.yaml 생성 완료: {yaml_path}")


# =========================
# 데이터셋 생성
# =========================

def build_yolo_dataset(reset: bool = True) -> None:
    if reset and YOLO_DATASET_DIR.exists():
        print(f"[INFO] 기존 YOLO 데이터셋 삭제: {YOLO_DATASET_DIR}")
        shutil.rmtree(YOLO_DATASET_DIR)

    make_yolo_dirs()

    json_files = list(RAW_LABEL_DIR.rglob("*.json"))
    image_index = build_image_index(RAW_IMAGE_DIR)

    print(f"[INFO] 라벨 JSON 수: {len(json_files)}")

    samples = []

    missing_image_count = 0
    invalid_label_count = 0

    for json_path in json_files:
        parsed = parse_aihub_json(json_path)

        if parsed is None:
            invalid_label_count += 1
            continue

        file_name = parsed["file_name"]
        image_path = image_index.get(file_name)

        if image_path is None:
            missing_image_count += 1
            continue

        samples.append({
            "image_path": image_path,
            "file_name": file_name,
            "labels": parsed["labels"],
        })

    print(f"[INFO] 매칭된 샘플 수: {len(samples)}")
    print(f"[INFO] 이미지 누락 수: {missing_image_count}")
    print(f"[INFO] 유효하지 않은 라벨 수: {invalid_label_count}")

    if not samples:
        raise RuntimeError(
            "이미지와 라벨이 매칭된 샘플이 없습니다. "
            "JSON의 file_name과 실제 이미지 파일명이 일치하는지 확인하세요."
        )

    random.seed(RANDOM_SEED)
    random.shuffle(samples)

    train_count = int(len(samples) * TRAIN_RATIO)

    train_samples = samples[:train_count]
    val_samples = samples[train_count:]

    print(f"[INFO] train 샘플 수: {len(train_samples)}")
    print(f"[INFO] val 샘플 수: {len(val_samples)}")

    def copy_split(split_name: str, split_samples: List[Dict]) -> None:
        image_target_dir = YOLO_DATASET_DIR / "images" / split_name
        label_target_dir = YOLO_DATASET_DIR / "labels" / split_name

        for sample in split_samples:
            src_image_path = sample["image_path"]
            file_name = sample["file_name"]

            target_image_path = image_target_dir / file_name
            target_label_path = label_target_dir / f"{Path(file_name).stem}.txt"

            shutil.copy2(src_image_path, target_image_path)
            write_yolo_label(target_label_path, sample["labels"])

    copy_split("train", train_samples)
    copy_split("val", val_samples)

    write_data_yaml()

    print("[INFO] YOLO 데이터셋 생성 완료")


# =========================
# YOLOv8 학습
# =========================

def train_yolov8() -> None:
    data_yaml = YOLO_DATASET_DIR / "data.yaml"

    if not data_yaml.exists():
        raise FileNotFoundError(f"data.yaml이 없습니다: {data_yaml}")

    model = YOLO("yolov8n.pt")

    model.train(
        data=str(data_yaml),
        epochs=50,
        imgsz=640,
        batch=16,
        workers=4,
        project=str(PROJECT_ROOT / "runs"),
        name="animal_detector_yolov8n",
        exist_ok=True,
        patience=10,
    )

    print("[INFO] YOLOv8 학습 완료")
    print(f"[INFO] best.pt 위치: {PROJECT_ROOT / 'runs' / 'animal_detector_yolov8n' / 'weights' / 'best.pt'}")


def main() -> None:
    print("[STEP 1] AIHub JSON + 원천 이미지 → YOLOv8 데이터셋 생성")
    build_yolo_dataset(reset=True)

    print("[STEP 2] YOLOv8 학습 시작")
    train_yolov8()


if __name__ == "__main__":
    main()