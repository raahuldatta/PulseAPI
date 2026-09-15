import unittest
from fastapi.testclient import TestClient
from main import app, API_KEY, API_KEY_NAME

class TestSentimentAPI(unittest.TestCase):
    def setUp(self):
        # Using TestClient as a context manager triggers the lifespan (startup/shutdown) events
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def test_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertEqual(response.json()["status"], "healthy")
        self.assertTrue(response.json()["model_loaded"])

    def test_analyze_no_auth(self):
        response = self.client.post("/api/analyze", json={"text": "Hello"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Could not validate API KEY")

    def test_analyze_auth_success(self):
        response = self.client.post(
            "/api/analyze", 
            json={"text": "I love this feature!"},
            headers={API_KEY_NAME: API_KEY}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("label", data)
        self.assertIn("confidence", data)

    def test_analyze_batch(self):
        response = self.client.post(
            "/api/analyze/batch", 
            json={"texts": ["Great!", "Terrible."]},
            headers={API_KEY_NAME: API_KEY}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertIn("label", data[0])

if __name__ == "__main__":
    unittest.main()
