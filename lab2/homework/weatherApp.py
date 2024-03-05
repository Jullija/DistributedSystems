from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

METEO_API_KEY = os.getenv("METEO_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")