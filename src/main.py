import uvicorn

from fastapi import FastAPI

from weather_service.router import router as router_weather

app = FastAPI()


app.include_router(router_weather)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234)
