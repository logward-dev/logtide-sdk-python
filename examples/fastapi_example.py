"""FastAPI middleware example for LogTide Python SDK."""

from fastapi import FastAPI

from logtide_sdk import ClientOptions, LogTideClient
from logtide_sdk.middleware import LogTideFastAPIMiddleware

app = FastAPI()

# Initialize LogTide client
client = LogTideClient(
    ClientOptions(
        api_url="http://localhost:8080",
        api_key="lp_your_api_key_here",
    )
)

# Add middleware
app.add_middleware(
    LogTideFastAPIMiddleware,
    client=client,
    service_name="fastapi-api",
    log_requests=True,
    log_responses=True,
    log_errors=True,
    include_headers=False,
    skip_health_check=True,
)


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "John Doe"}


@app.get("/error")
async def error_route():
    raise ValueError("Test error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
