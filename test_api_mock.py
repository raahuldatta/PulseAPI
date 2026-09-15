import unittest
from unittest.mock import patch, MagicMock
import main
from fastapi.testclient import TestClient
from main import app, API_KEY, API_KEY_NAME

class TestSentimentAPIMock(unittest.TestCase):
    @patch('main.pipeline')
    def setUp(self, mock_pipeline):
        # Mock the pipeline so lifespan doesn't actually download anything
        self.mock_model = MagicMock()
        mock_pipeline.return_value = self.mock_model
        
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def test_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "healthy")

    def test_analyze_no_auth(self):
        response = self.client.post("/api/analyze", json={"text": "Hello"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Could not validate API KEY")

    @patch("main.predict_text")
    def test_analyze_auth_success_mock(self, mock_predict):
        mock_predict.return_value = [{"label": "positive", "score": 0.99}]
        
        response = self.client.post(
            "/api/analyze", 
            json={"text": "I love this feature!"},
            headers={API_KEY_NAME: API_KEY}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["label"], "positive")
        self.assertAlmostEqual(data["confidence"], 0.99)

    @patch("main.predict_text")
    def test_analyze_batch_mock(self, mock_predict):
        mock_predict.side_effect = [
            [{"label": "positive", "score": 0.95}],
            [{"label": "negative", "score": 0.90}]
        ]
        
        response = self.client.post(
            "/api/analyze/batch", 
            json={"texts": ["Great!", "Terrible."]},
            headers={API_KEY_NAME: API_KEY}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["label"], "positive")
        self.assertEqual(data[1]["label"], "negative")

if __name__ == "__main__":
    unittest.main()
