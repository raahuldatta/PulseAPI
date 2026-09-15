# 📊 PulseAPI

*Sentiment Analysis, Served*

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=1a1a2e)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=white&labelColor=1a1a2e)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white&labelColor=1a1a2e)

**PulseAPI classifies text into positive, negative, or neutral sentiment with confidence scores — served through a production-hardened FastAPI layer with auth, caching, and logging built in.**

Powered by `cardiffnlp/twitter-roberta-base-sentiment-latest` via Hugging Face `transformers`, containerized with the model baked into the image for fast, cold-start-free scaling.

---

## 🎯 Overview

Most sentiment demos are a single unguarded endpoint wrapping a model call. PulseAPI is built to actually sit behind a frontend or another service: it authenticates callers, caches repeated requests, validates input aggressively, and logs every request's timing — without needing extra infrastructure bolted on.

A request hits `/api/analyze` (or the batch variant), the cached `predict_text` pipeline scores it against the RoBERTa sentiment model, and the response returns a top label, a confidence score, and the full per-class score breakdown — so a caller can build their own threshold logic instead of trusting a single label blindly.

---

## ⚙️ Core Principle

| PulseAPI does | PulseAPI doesn't |
| --- | --- |
| Requires an `X-API-Key` on every analysis call | Expose analysis endpoints without authentication |
| Caches repeated text via LRU to save compute | Re-run inference on identical inputs |
| Validates text length and batch size before inference | Let unbounded payloads reach the model |
| Logs every request's method, path, status, and latency | Fail silently on slow or errored requests |
| Loads the model once at startup via a lifespan hook | Reload the model per-request |

---

## ✨ Features

**🔐 Authentication**
- API key required via the `X-API-Key` header on both analysis endpoints
- Public, unauthenticated health check at `GET /`

**⚡ Performance**
- `lru_cache`-backed prediction function — identical text is never re-scored
- Model loaded once at process startup (via FastAPI's `lifespan` context) and torn down cleanly on shutdown

**🛡️ Validation & Safety**
- `Pydantic` models enforce a 1–2000 character limit per text
- Batch requests capped at 10 texts per call to bound memory and latency

**📈 Observability**
- Custom middleware logs method, path, status code, and processing time for every request

**🌐 Integration-Ready**
- CORS enabled out of the box so browser-based frontends can call it directly

**🐳 Deployment**
- `Dockerfile` downloads and bakes the model into the image at build time, so containers start fast with no first-request cold start

---

## 🏗️ Architecture

```
                    Client Request
                          │
                          ▼
            ┌──────────────────────────┐
            │   CORS + Logging Middleware │
            │   (times every request)      │
            └──────────────────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │   X-API-Key Verification     │
            └──────────────────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │   Pydantic Validation        │
            │  (length / batch-size caps)  │
            └──────────────────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │   LRU-Cached Prediction      │
            │  (skips repeated inference)  │
            └──────────────────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │  RoBERTa Sentiment Pipeline  │
            │ (cardiffnlp/twitter-roberta) │
            └──────────────────────────┘
                          │
                          ▼
            label + confidence + full score breakdown
```

---

## 📡 API Reference

| Method | Route | Auth | Purpose |
| --- | --- | --- | --- |
| `GET` | `/` | Public | Health check — server status and whether the model is loaded |
| `POST` | `/api/analyze` | `X-API-Key` | Classify a single text's sentiment |
| `POST` | `/api/analyze/batch` | `X-API-Key` | Classify up to 10 texts in one call |

**`POST /api/analyze`**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: super-secret-key" \
  -d '{"text": "I absolutely love this new feature!"}'
```
```json
{
  "label": "positive",
  "confidence": 0.98,
  "scores": [
    {"label": "positive", "score": 0.98},
    {"label": "neutral", "score": 0.015},
    {"label": "negative", "score": 0.005}
  ]
}
```

**`POST /api/analyze/batch`**
```bash
curl -X POST http://localhost:8000/api/analyze/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: super-secret-key" \
  -d '{"texts": ["The movie was fantastic!", "The service was terrible.", "It was okay, nothing special."]}'
```

---

## 🧬 Validation Limits

| Field | Constraint |
| --- | --- |
| `text` | 1–2000 characters |
| `texts` (batch) | 1–10 items |

---

## 📁 Project Structure

```
pulseapi/
├── main.py              # FastAPI app, routes, middleware, model lifecycle
├── requirements.txt     # fastapi, uvicorn, transformers, torch, pydantic
├── Dockerfile           # Model baked in at build time
├── test_api.py
├── test_api_mock.py
└── README.md
```

---

## 🧱 Tech Stack

| Category | Technology |
| --- | --- |
| Framework | FastAPI + Uvicorn |
| Model | `cardiffnlp/twitter-roberta-base-sentiment-latest` (Hugging Face `transformers`) |
| Validation | Pydantic |
| Caching | `functools.lru_cache` |
| Packaging | Docker (`python:3.10-slim` base) |

---

## 🚀 Quickstart

**1. Docker (recommended)**
```bash
docker build -t pulseapi .
docker run -p 8000:8000 pulseapi
```
Model weights are downloaded during the build step, so the container starts up with no cold-start delay.

**2. Local virtual environment**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**3. Authentication**

Both analysis endpoints require an API key:
```
Header: X-API-Key: super-secret-key
```
> Change `API_KEY` in `main.py` (or load it from an environment variable) before deploying to production.

---

## 🧭 Known Limitations & Roadmap

- **Hardcoded API key** — `API_KEY` is a constant in `main.py`; move it to an environment variable before any real deployment.
- **In-memory LRU cache** — cache resets on restart and doesn't share across multiple instances; a shared cache (e.g. Redis) would be needed to scale horizontally.
- **No rate limiting** — the API key gates access but doesn't throttle request volume per key.
- **Single model** — only the CardiffNLP RoBERTa sentiment model is wired in; swapping or A/B testing models would need a config layer.

---

## 📄 License

MIT
