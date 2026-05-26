import os
import warnings
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch


TEST_DB_PATH = Path("tests/.tmp/test_backend.db")
TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.resolve()}"
os.environ["CORS_ORIGINS"] = "http://testserver"

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.resetwarnings()
warnings.simplefilter("ignore", DeprecationWarning)
warnings.simplefilter("ignore", ResourceWarning)

from fastapi.testclient import TestClient

from ai.yolo_detector import DetectedObject
from database import ENGINE, SessionLocal, Base, init_db
from main import app
from models.comment import Comment
from models.event import Event
from routers import events as events_router


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=ENGINE)
        init_db()

    def tearDown(self) -> None:
        with SessionLocal() as session:
            session.query(Comment).delete()
            session.query(Event).delete()
            session.commit()

    def test_root_and_list_empty_events(self) -> None:
        with TestClient(app) as client:
            root = client.get("/")
            events = client.get("/api/events")
            v1_events = client.get("/api/v1/events")

        self.assertEqual(root.status_code, 200)
        self.assertEqual(events.status_code, 200)
        self.assertEqual(v1_events.status_code, 200)
        self.assertEqual(events.json(), [])
        self.assertEqual(v1_events.json(), [])

    def test_detect_creates_event_and_repeat_detection_updates_same_row(self) -> None:
        detected_object = DetectedObject(
            species="wild_boar",
            confidence=0.86,
            bbox_x=37.240786,
            bbox_y=63.989122,
            bbox_width=26.300697,
            bbox_height=23.523227,
        )

        async def fake_save_upload_image(image):
            return Path("tests/.tmp/sample.jpeg"), "/static/images/2026/05/26/sample.jpeg"

        with (
            TestClient(app) as client,
            patch.object(events_router.detector, "detect", return_value=[detected_object]),
            patch.object(events_router, "save_upload_image", new=AsyncMock(side_effect=fake_save_upload_image)),
        ):
            first = client.post(
                "/api/events/detect",
                data={
                    "cameraId": "CCTV-001",
                    "latitude": "37.5665",
                    "longitude": "126.9780",
                    "locationName": "테스트영역",
                },
                files={"image": ("sample.jpeg", b"fake-bytes", "image/jpeg")},
            )

            self.assertEqual(first.status_code, 201)
            self.assertEqual(len(first.json()), 1)
            self.assertEqual(first.json()[0]["cameraId"], "CCTV-001")
            self.assertEqual(first.json()[0]["objectType"], "멧돼지")
            self.assertEqual(first.json()[0]["riskLevel"], "후순위 확인")

            with SessionLocal() as session:
                event = session.query(Event).one()
                event.last_detected_at = datetime.now(timezone.utc) - timedelta(minutes=2)
                session.commit()

            second = client.post(
                "/api/events/detect",
                data={
                    "camera_id": "CCTV-001",
                    "latitude": "37.5665",
                    "longitude": "126.9780",
                    "location_name": "테스트영역",
                },
                files={"image": ("sample.jpeg", b"fake-bytes", "image/jpeg")},
            )

        self.assertEqual(second.status_code, 201)
        self.assertEqual(len(second.json()), 1)
        self.assertTrue(second.json()[0]["repeatDetection"])
        self.assertEqual(second.json()[0]["riskLevel"], "순차 확인")

        with SessionLocal() as session:
            events = session.query(Event).all()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].repeat_count, 1)
            self.assertTrue(events[0].repeat_detection)
            self.assertEqual(events[0].priority, 2)

    def test_status_patch_creates_comment_and_updates_status(self) -> None:
        detected_object = DetectedObject(
            species="gorani",
            confidence=0.91,
            bbox_x=10.0,
            bbox_y=20.0,
            bbox_width=30.0,
            bbox_height=40.0,
        )

        async def fake_save_upload_image(image):
            return Path("tests/.tmp/sample.jpeg"), "/static/images/2026/05/26/sample.jpeg"

        with (
            TestClient(app) as client,
            patch.object(events_router.detector, "detect", return_value=[detected_object]),
            patch.object(events_router, "save_upload_image", new=AsyncMock(side_effect=fake_save_upload_image)),
        ):
            create_response = client.post(
                "/api/events/detect",
                data={
                    "camera_id": "CCTV-002",
                    "latitude": "37.5665",
                    "longitude": "126.9780",
                    "location_name": "테스트영역",
                },
                files={"image": ("sample.jpeg", b"fake-bytes", "image/jpeg")},
            )
            event_id = create_response.json()[0]["id"]

            patch_response = client.patch(
                f"/api/events/{event_id}/status",
                json={
                    "status": "CHECKING",
                    "comment": "관제사 확인 시작",
                },
            )

        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["status"], "확인 중")

        with SessionLocal() as session:
            event = session.get(Event, int(event_id))
            comments = session.query(Comment).all()

        self.assertIsNotNone(event)
        self.assertEqual(event.status, "CHECKING")
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].content, "관제사 확인 시작")

    def test_missing_event_returns_standardized_error(self) -> None:
        with TestClient(app) as client:
            response = client.get("/api/events/999999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error_code"], "EVENT_NOT_FOUND")
        self.assertEqual(response.json()["message"], "해당 이벤트를 찾을 수 없습니다.")
def tearDownModule() -> None:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


if __name__ == "__main__":
    unittest.main()
