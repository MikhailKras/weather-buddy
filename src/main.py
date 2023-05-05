import uvicorn

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.auth.jwt import is_authenticated
from src.weather_service.router import router as router_weather
from src.auth.router import router as router_auth

app = FastAPI(title='Weather Buddy')

app.include_router(router_weather)
app.include_router(router_auth)

app.mount('/static', StaticFiles(directory='src/static'), name='static')

templates = Jinja2Templates(directory='src/templates')


@app.get('/', response_class=HTMLResponse)
async def get_home_page(request: Request, is_auth: bool = Depends(is_authenticated)):
    return templates.TemplateResponse('home.html', context={"request": request, "is_auth": is_auth})


@app.get('/about', response_class=HTMLResponse)
async def get_home_page(request: Request, is_auth: bool = Depends(is_authenticated)):
    return templates.TemplateResponse('about.html', context={"request": request, "is_auth": is_auth})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234)
