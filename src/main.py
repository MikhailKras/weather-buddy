import time
from typing import Optional

from redis import asyncio as aioredis
import uvicorn

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from src.auth.jwt import is_authenticated
from src.auth.schemas import UserInDB
from src.config import REDIS_HOST, REDIS_PORT
from src.database import mongo_db
from src.logger import logger
from src.utils import get_jinja_templates
from src.weather_service.router import router as router_weather
from src.auth.router import router as router_auth

app = FastAPI(title='Weather Buddy')


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    await FastAPILimiter.init(redis)

    await mongo_db.connect()


@app.on_event("shutdown")
async def shutdown():
    await mongo_db.disconnect()


@app.middleware('http')
async def log_request(request: Request, call_next):
    log_data = {
        'client_ip': request.client.host,
        'path': request.url.path,
        'query_params': request.query_params,
        'headers': request.headers,
    }
    start_time = time.process_time()
    try:
        response = await call_next(request)
    except Exception as e:
        end_time = time.process_time() - start_time
        log_data.update(processing_time=round(end_time, 3))
        logger.error("log_request_error", extra=log_data, exc_info=True)
        raise
    end_time = time.process_time() - start_time
    log_data.update(processing_time=round(end_time, 3), status_code=response.status_code)
    logger.info("log_request", extra=log_data)
    return response

app.include_router(router_weather)
app.include_router(router_auth)

app.mount('/static', StaticFiles(directory='src/static'), name='static')

templates = get_jinja_templates()


@app.get('/', response_class=HTMLResponse)
async def get_home_page(request: Request, user_data: Optional[UserInDB] = Depends(is_authenticated)):
    return templates.TemplateResponse('home.html', context={"request": request, "is_auth": user_data})


@app.get('/about', response_class=HTMLResponse)
async def get_home_page(request: Request, user_data: Optional[UserInDB] = Depends(is_authenticated)):
    return templates.TemplateResponse('about.html', context={"request": request, "is_auth": user_data})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234)
