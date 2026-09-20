# CPU-Bench-App

## 1. Application name
CPU-Bench-App

## 2. Purpose
A minimal Flask benchmark application built to produce **CPU-bound** performance
behavior. It exists to be used as a test subject for a performance-prediction /
static-analysis + runtime-metrics research project — not as a real product.

## 3. Type of workload
CPU-intensive. The `/compute` endpoint performs configurable, bounded CPU work
(recursive Fibonacci by default, with optional hashing and prime-counting modes).
No database, no external network calls, no disk I/O of note — CPU utilization is
expected to be the limiting resource under load.

## 4. Technologies used
- Python 3.11
- Flask 3.x
- Gunicorn (WSGI server for a more realistic serving setup)
- Docker

## 5. Project structure
```
CPU-Bench-App/
│
├── app.py            # application source
├── requirements.txt   # Python dependencies
├── Dockerfile
├── .dockerignore
├── .env.example
└── README.md
```

## 6. Dependencies
See `requirements.txt`:
- Flask
- gunicorn

## 7. Local setup
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The app listens on `http://0.0.0.0:5000` by default.

## 8. Docker setup
Build:
```bash
docker build -t cpu-bench-app .
```
Run:
```bash
docker run -p 5000:5000 cpu-bench-app
```
Optional: pass env vars from `.env.example`:
```bash
docker run -p 5000:5000 --env-file .env cpu-bench-app
```

## 9. Docker Compose setup
Not required — this is a single-container application with no external
dependencies.

## 10. Available routes

| Method | Route            | Description                                              |
|--------|------------------|------------------------------------------------------------|
| GET    | `/`              | Basic info about the app and its routes                    |
| GET    | `/health`        | Lightweight health check → `{"status": "healthy"}`         |
| GET    | `/compute`       | CPU-heavy computation, controllable via query params        |
| GET    | `/compute/<n>`   | Same as `/compute?mode=fib&n=<n>`, n as a path parameter    |
| GET    | `/status`        | Process uptime / PID / configured limits                   |

### `/compute` query parameters
| Param   | Applies to     | Default | Notes                                    |
|---------|----------------|---------|-------------------------------------------|
| `mode`  | all            | `fib`   | `fib`, `hash`, or `prime`                  |
| `n`     | `fib`          | 28      | Capped at `MAX_N` (default 35)             |
| `iters` | `hash`         | 100000  | Capped at `MAX_ITER` (default 2,000,000)   |
| `limit` | `prime`        | 50000   | Capped at `MAX_ITER` (default 2,000,000)   |

Examples:
```
GET /compute?mode=fib&n=32
GET /compute?mode=hash&iters=500000
GET /compute?mode=prime&limit=100000
GET /compute/30
```

## 11. Expected bottleneck / workload
```
Expected primary bottleneck: CPU
```
At low concurrency, response times should stay low with moderate CPU usage.
As concurrent load increases (more simultaneous `/compute` requests, or higher
`n` / `iters` / `limit` values), CPU usage should climb toward saturation and
response times should increase accordingly. This is the *expected* behavior for
benchmarking purposes, not a guaranteed outcome — actual results depend on the
host machine and container resource limits.

## 12. How to test the application

Quick manual check:
```bash
curl http://localhost:5000/health
curl "http://localhost:5000/compute?mode=fib&n=30"
```

Load testing with a tool like [Locust](https://locust.io/) or `hey`/`wrk`:
```bash
# example with hey
hey -z 30s -c 50 "http://localhost:5000/compute?mode=fib&n=30"
```

To simulate escalating load, gradually increase concurrent users and/or the
`n` / `iters` / `limit` parameter and observe:
- `/status` uptime and process behavior
- container CPU usage (`docker stats`)
- response time growth in your load-testing tool's output

## Notes
- No authentication is implemented (by design — this is a benchmark app).
- No frontend is provided — pure JSON API.
- Workload intensity is intentionally bounded (`MAX_N`, `MAX_ITER`) so a single
  request cannot take minutes or crash the container; adjust these via
  environment variables if you need a heavier ceiling.
"# CPU-Bench-App" 
