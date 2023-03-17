import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from weather_service.router import router as router_weather

app = FastAPI(title='Weather Buddy')

app.include_router(router_weather)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=HTMLResponse)
async def get_home_page(request: Request):
    return templates.TemplateResponse('home.html', context={"request": request})


@app.get('/about', response_class=HTMLResponse)
async def get_home_page(request: Request):
    return templates.TemplateResponse('about.html', context={"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234)
