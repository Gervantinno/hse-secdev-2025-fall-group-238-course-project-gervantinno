from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient


def create_app_with_inmemory_limiter(limit: int = 2):
    app = FastAPI()
    counters = {}

    @app.post("/login")
    async def login(request: Request):
        # For test purposes use a fixed client key (no real IP parsing)
        key = "test-client"
        counters[key] = counters.get(key, 0) + 1
        remaining = limit - counters[key]
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, remaining)),
        }
        if counters[key] > limit:
            return Response(
                status_code=429,
                content=b"Too Many Requests",
                headers={"Retry-After": "1"},
            )
        return Response(status_code=200, content=b"OK", headers=headers)

    return app


def test_rate_limit_allows_under_limit():
    app = create_app_with_inmemory_limiter(limit=2)
    client = TestClient(app)
    r1 = client.post("/login")
    r2 = client.post("/login")
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_rate_limit_blocks_after_limit():
    app = create_app_with_inmemory_limiter(limit=2)
    client = TestClient(app)
    client.post("/login")
    client.post("/login")
    r3 = client.post("/login")
    assert r3.status_code == 429
