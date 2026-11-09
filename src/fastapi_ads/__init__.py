def main() -> None:
    import uvicorn
    uvicorn.run("fastapi_ads.main:app", host="0.0.0.0", port=8000)