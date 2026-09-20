"""
CPU-Bench-App
A small Flask benchmark application whose primary intended bottleneck is CPU.

Routes:
    GET /            - basic info page (JSON)
    GET /health       - lightweight health check
    GET /compute       - CPU-heavy computation (Fibonacci), controllable via ?n=
    GET /compute/<n>    - same, but n passed as a path parameter
    GET /status       - basic runtime/process status info

The heavy work is deliberately naive/recursive-ish so it burns CPU cycles,
but it is bounded so a single request cannot take minutes or crash the app.
"""

import os
import time
import math
import hashlib
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---- Configuration ---------------------------------------------------------

# Hard upper bound on the "n" parameter to keep requests safe & bounded.
MAX_N = int(os.environ.get("MAX_N", 35))          # for fibonacci (recursive)
MAX_ITER = int(os.environ.get("MAX_ITER", 2_000_000))  # for prime/hash mode
DEFAULT_N = int(os.environ.get("DEFAULT_N", 28))

START_TIME = time.time()


# ---- CPU-heavy workloads ----------------------------------------------------

def fib(n: int) -> int:
    """Naive recursive Fibonacci -- intentionally CPU-inefficient."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def cpu_hash_burn(iterations: int) -> str:
    """Hashes data repeatedly to burn CPU cycles in a controllable way."""
    data = b"cpu-bench-app"
    digest = hashlib.sha256(data).digest()
    for _ in range(iterations):
        digest = hashlib.sha256(digest).digest()
    return digest.hex()


def count_primes(limit: int) -> int:
    """Simple (non-optimized) prime counting up to `limit`."""
    count = 0
    for candidate in range(2, limit):
        is_prime = True
        upper = int(math.isqrt(candidate)) + 1
        for div in range(2, upper):
            if candidate % div == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


# ---- Routes -----------------------------------------------------------------

@app.route("/")
def index():
    return jsonify({
        "app": "CPU-Bench-App",
        "purpose": "CPU-intensive benchmark application",
        "expected_bottleneck": "CPU",
        "routes": ["/", "/health", "/compute", "/compute/<n>", "/status"],
    })


@app.route("/health")
def health():
    # Deliberately extremely lightweight -- no computation, no I/O.
    return jsonify({"status": "healthy"})


@app.route("/compute")
def compute():
    """
    Controllable CPU-heavy endpoint.

    Query params:
      n     - fibonacci input (default DEFAULT_N, capped at MAX_N)
      mode  - "fib" (default), "hash", or "prime"
      iters - iteration count for "hash" mode (capped at MAX_ITER)
      limit - upper bound for "prime" mode (capped at MAX_ITER)
    """
    mode = request.args.get("mode", "fib")

    start = time.perf_counter()

    if mode == "hash":
        iters = min(int(request.args.get("iters", 100_000)), MAX_ITER)
        result = cpu_hash_burn(iters)
        payload = {"mode": "hash", "iterations": iters, "result_prefix": result[:16]}

    elif mode == "prime":
        limit = min(int(request.args.get("limit", 50_000)), MAX_ITER)
        result = count_primes(limit)
        payload = {"mode": "prime", "limit": limit, "primes_found": result}

    else:  # fib
        n = min(int(request.args.get("n", DEFAULT_N)), MAX_N)
        result = fib(n)
        payload = {"mode": "fib", "n": n, "result": result}

    elapsed = time.perf_counter() - start
    payload["elapsed_seconds"] = round(elapsed, 4)
    return jsonify(payload)


@app.route("/compute/<int:n>")
def compute_path(n: int):
    """Same as /compute?mode=fib&n=<n>, but n given as a path parameter."""
    n = min(n, MAX_N)
    start = time.perf_counter()
    result = fib(n)
    elapsed = time.perf_counter() - start
    return jsonify({
        "mode": "fib",
        "n": n,
        "result": result,
        "elapsed_seconds": round(elapsed, 4),
    })


@app.route("/status")
def status():
    return jsonify({
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "pid": os.getpid(),
        "max_n": MAX_N,
        "max_iterations": MAX_ITER,
        "default_n": DEFAULT_N,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
