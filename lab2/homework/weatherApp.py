from fastapi import FastAPI, HTTPException, Body, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from requests.exceptions import HTTPError, RequestException
import os
from dotenv import load_dotenv
import requests


load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/pages")

METEO_API_KEY = os.getenv("METEO_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")


def fetch_json(city: str, url: str, api_key: str, param_key=str, param_city=str):
    params = {f"{param_key}": api_key, f"{param_city}": city}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def create_data(
    request: Request,
    city: str,
    meteo_data: float,
    tomorrow_data: float,
    weather_data: float,
):
    max_temp = max(meteo_data, tomorrow_data, weather_data)
    min_temp = min(meteo_data, tomorrow_data, weather_data)
    avg_temp = round((meteo_data + tomorrow_data + weather_data) / 3, 2)

    data = {
        "request": request,
        "city": city,
        "meteo_api_temp": meteo_data,
        "weather_api_temp": weather_data,
        "tomorrow_api_temp": tomorrow_data,
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "min_temp": min_temp,
    }

    return data


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    status_code = exception.status_code
    detail = exception.detail

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "exception": exception,
            "status_code": status_code,
            "detail": detail,
        },
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.post("/results", response_class=HTMLResponse)
async def post_results(request: Request, city: str = Form(None)):

    if not city:
        return templates.TemplateResponse(
            "homepage.html", {"request": request, "error": "Provide city"}
        )

    if not METEO_API_KEY:
        raise HTTPException(status_code=500, detail="Meteo API key is not configured.")
    elif not WEATHER_API_KEY:
        raise HTTPException(
            status_code=500, detail="Weather API key is not configured."
        )
    elif not TOMORROW_API_KEY:
        raise HTTPException(
            status_code=500, detail="Tomorrow API key is not configured."
        )

    try:
        meteo_response = fetch_json(
            city,
            "https://www.meteosource.com/api/v1/free/point?sections=current&",
            METEO_API_KEY,
            "key",
            "place_id",
        )
        meteo_data = meteo_response["current"]["temperature"]
    except (KeyError, HTTPError, RequestException) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch or parse MeteoAPI data: {e}"
        )

    try:
        tomorrow_response = fetch_json(
            city,
            "https://api.tomorrow.io/v4/weather/realtime?",
            TOMORROW_API_KEY,
            "apikey",
            "location",
        )
        tomorrow_data = tomorrow_response["data"]["values"]["temperature"]
    except (KeyError, HTTPError, RequestException) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch or parse TomorrowAPI data: {e}"
        )

    try:
        weather_response = fetch_json(
            city,
            "http://api.weatherapi.com/v1/current.json?",
            WEATHER_API_KEY,
            "key",
            "q",
        )
        weather_data = weather_response["current"]["temp_c"]
    except (KeyError, HTTPError, RequestException) as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch or parse WeatherAPI data: {e}"
        )

    data = create_data(request, city, meteo_data, tomorrow_data, weather_data)
    return templates.TemplateResponse("results.html", context=data)
