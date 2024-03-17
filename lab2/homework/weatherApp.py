from fastapi import FastAPI, HTTPException, Body, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from requests.exceptions import HTTPError, RequestException
import os
from dotenv import load_dotenv
import requests
import httpx
from httpx import HTTPStatusError


load_dotenv()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/pages")

METEO_API_KEY = os.getenv("METEO_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")


async def fetch_json(city: str, url: str, api_key: str, param_key=str, param_city=str):
    params = {param_key: api_key, param_city: city}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    
async def fetch_photo(city:str, url: str):
    params = {"query": city}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params = params)
        response.raise_for_status()
        return response.json()


async def create_data(
    request: Request,
    city: str,
    meteo_data: float,
    tomorrow_data: float,
    weather_data: float,
    unsplash_data: str
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
        "unsplash_photo": unsplash_data
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
    elif not UNSPLASH_API_KEY:
        raise HTTPException(
            status_code=500, detail="Tomorrow API key is not configured."
        )

    try:
        try:
            meteo_response = await fetch_json(
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
            tomorrow_response = await fetch_json(
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
            weather_response = await fetch_json(
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
            
        try:
            unsplash_response = await fetch_photo(
                city, f"https://api.unsplash.com/search/photos/?client_id={UNSPLASH_API_KEY}&"
            )
            unsplash_data = unsplash_response["results"][0]["urls"]["raw"]
        except (KeyError, HTTPError, RequestException) as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch or parse Unsplash data: {e}"
            )
        
    except HTTPStatusError as http_err:
        if http_err.response.status_code == 404:
            error_message = f"The city '{city}' could not be found. Please check the city name and try again."
            return templates.TemplateResponse(
                "error.html", {"request": request, "detail": error_message}, status_code=404
            )
        else:
            return templates.TemplateResponse(
                "error.html", {"request": request, "detail": "An error occurred while fetching data. Please try again later."}, status_code=500
            )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "detail": f"An unexpected error occurred: {e}"}, status_code=500
        )

    data = await create_data(request, city, meteo_data, tomorrow_data, weather_data, unsplash_data)
    return templates.TemplateResponse("results.html", context=data)
