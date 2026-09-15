<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0,2,5&height=180&section=header&text=PulseAPI&fontSize=52&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Sentiment%20Analysis%2C%20Served&descAlignY=58&descSize=16" width="100%"/>

<h1 align="center">📊 PulseAPI</h1>
<p align="center"><i>Sentiment Analysis, Served</i></p>

<img src="https://img.shields.io/badge/Python-3.10-0EA5E9.svg?style=for-the-badge&logo=python&logoColor=white&labelColor=0f172a"/>
<img src="https://img.shields.io/badge/FastAPI-Async-14B8A6.svg?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0f172a"/>
<img src="https://img.shields.io/badge/HuggingFace-Transformers-38BDF8.svg?style=for-the-badge&logo=huggingface&logoColor=white&labelColor=0f172a"/>
<img src="https://img.shields.io/badge/Pydantic-Validation-0891B2.svg?style=for-the-badge&logo=pydantic&logoColor=white&labelColor=0f172a"/>
<img src="https://img.shields.io/badge/Docker-Ready-0EA5E9.svg?style=for-the-badge&logo=docker&logoColor=white&labelColor=0f172a"/>

<br/><br/>

<p align="center">
<b>PulseAPI classifies text into positive, negative, or neutral sentiment with confidence scores — served through a production-hardened FastAPI layer with authentication, caching, and request logging built in.</b>
</p>

<p align="center">
Powered by <b>cardiffnlp/twitter-roberta-base-sentiment-latest</b> via Hugging Face <b>transformers</b>, containerized with the model baked into the image for fast, cold-start-free scaling.
</p>

</div>

<br/>

---

## <img src="https://img.shields.io/badge/-Overview-0EA5E9?style=flat-square"/>

Most sentiment demos are a single unguarded endpoint wrapping a model call. PulseAPI is built to actually sit behind a frontend or another service: it authenticates callers, caches repeated requests, validates input aggressively, and logs every request's timing — without needing extra infrastructure bolted on.

A request hits `/api/analyze` (or the batch variant), the cached `predict_text` pipeline scores it against the RoBERTa sentiment model, and the response returns a top label, a confidence score, and the full per-class score breakdown — so a caller can build their own threshold logic instead of trusting a single label blindly.

<br/>

---

## <img src="https://img.shields.io/badge/-Core%20Principle-0EA5E9?style=flat-square"/>

<div align="center">

> **PulseAPI scores text. Callers decide what to do with it.**

| PulseAPI does | PulseAPI doesn't |
|:--|:--|
| Requires an `X-API-Key` on every analysis call | Expose analysis endpoints without authentication |
| Caches repeated text via LRU to save compute | Re-run inference on identical inputs |
| Validates text length and batch size before inference | Let unbounded payloads reach the model |
| Logs every request's method, path, status, and latency | Fail silently on slow or errored requests |
| Loads the model once at startup via a lifespan hook | Reload the model per-request |

</div>

<br/>

---

## <img src="https://img.shields.io/badge/-Feature%20Breakdown-0EA5E9?style=flat-square"/>

<details>
<summary><b>🔐 Authentication</b></summary>
<br/>

- API key required via the `X-API-Key` header on both `/api/analyze` and `/api/analyze/batch`.
- Public, unauthenticated health check at `GET /` so uptime monitors don't need credentials.

</details>

<details>
<summary><b>⚡ Performance</b></summary>
<br/>

- `lru_cache`-backed prediction function (`predict_text`) — identical text is never re-scored.
- Model loaded once at process startup via FastAPI's `lifespan` context, and released cleanly on shutdown.

</details>

<details>
<summary><b>🛡️ Validation & Safety</b></summary>
<br/>

- Pydantic models enforce a 1–2000 character limit per text (`TextRequest`).
- Batch requests capped at 10 texts per call (`BatchTextRequest`) to bound memory and latency.

</details>

<details>
<summary><b>📈 Observability</b></summary>
<br/>

- Custom middleware (`log_requests`) logs method, path, status code, and processing time for every request.
- Structured logging configured at module load via Python's `logging` module.

</details>

<details>
<summary><b>🌐 Integration-Ready</b></summary>
<br/>

- CORS middleware enabled out of the box so browser-based frontends can call the API directly.

</details>

<details>
<summary><b>🐳 Deployment</b></summary>
<br/>

- `Dockerfile` downloads and bakes the model into the image at build time, so containers start fast with no first-request cold start.

</details>

<br/>

---

## <img src="https://img.shields.io/badge/-System%20Architecture-0EA5E9?style=flat-square"/>

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

<div align="center">

| Layer | Technology | Notes |
|:--|:--|:--|
| API framework | FastAPI + Uvicorn | Async request handling, auto-generated OpenAPI docs |
| Model | Hugging Face `transformers` pipeline | `cardiffnlp/twitter-roberta-base-sentiment-latest` |
| Caching | `functools.lru_cache` | In-process, resets on restart |
| Validation | Pydantic `BaseModel` + `Field` | Enforces length/batch-size limits at the request boundary |
| Packaging | Docker (`python:3.10-slim`) | Model weights baked in at build time |

</div>

<br/>

---

## <img src="https://img.shields.io/badge/-API%20Reference-0EA5E9?style=flat-square"/>

<details>
<summary><b>View all routes</b></summary>
<br/>

| Method | Route | Auth | Purpose |
|:--|:--|:--:|:--|
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

</details>

<br/>

---

## <img src="https://img.shields.io/badge/-Validation%20Limits-0EA5E9?style=flat-square"/>

| Field | Constraint |
|:--|:--|
| `text` | 1–2000 characters |
| `texts` (batch) | 1–10 items |

<br/>

---

## <img src="https://img.shields.io/badge/-Project%20Directory%20Structure-0EA5E9?style=flat-square"/>

<details>
<summary><b>View full directory tree</b></summary>
<br/>

```
pulseapi/
├── main.py              # FastAPI app, routes, middleware, model lifecycle
├── requirements.txt     # fastapi, uvicorn, transformers, torch, pydantic
├── Dockerfile            # Model baked in at build time
├── test_api.py
├── test_api_mock.py
└── README.md
```

</details>

<br/>

---

## <img src="https://img.shields.io/badge/-Tech%20Stack-0EA5E9?style=flat-square"/>

<div align="center">

| Category | Technology |
|:--|:--|
| API framework | FastAPI + Uvicorn |
| Model | `cardiffnlp/twitter-roberta-base-sentiment-latest` (Hugging Face `transformers`) |
| ML runtime | PyTorch (`torch`) |
| Validation | Pydantic |
| Caching | `functools.lru_cache` |
| Packaging | Docker (`python:3.10-slim` base) |

</div>

<br/>

---

## <img src="https://img.shields.io/badge/-Quickstart%20Guide-0EA5E9?style=flat-square"/>

**1. Prerequisites** — Python 3.10+, and Docker if you want the containerized path.

**2. Docker (recommended)**

```bash
docker build -t pulseapi .
docker run -p 8000:8000 pulseapi
```

Model weights are downloaded during the build step, so the container starts up with no cold-start delay.

**3. Local virtual environment**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**4. Authentication**

Both analysis endpoints require an API key:

```
Header: X-API-Key: super-secret-key
```

> Change `API_KEY` in `main.py` (or load it from an environment variable) before deploying to production.

**5. Try it**

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive FastAPI Swagger UI, or hit `GET /` to confirm the model is loaded.

<br/>

---

## <img src="https://img.shields.io/badge/-Known%20Limitations%20%2F%20Roadmap-0EA5E9?style=flat-square"/>

- **Hardcoded API key** — `API_KEY` is a constant in `main.py`; move it to an environment variable before any real deployment.
- **In-memory LRU cache** — cache resets on restart and doesn't share across multiple instances; a shared cache (e.g. Redis) would be needed to scale horizontally.
- **No rate limiting** — the API key gates access but doesn't throttle request volume per key.
- **Single model** — only the CardiffNLP RoBERTa sentiment model is wired in; swapping or A/B testing models would need a config layer.

<br/>

---

## <img src="https://img.shields.io/badge/-License-0EA5E9?style=flat-square"/>

MIT

<br/>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=5,2,0&height=120&section=footer" width="100%"/>

</div>
