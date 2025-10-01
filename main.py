from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi import Form

import requests
import json
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title":"Welcome!"})


@app.post("/submit")
async def submit(username: str = Form(...), age: int = Form(...)):
    print(f"Username: {username} Age: {age}")  #we can accept user input from front end in terms of form
    arr = np.array[1,2,3,4,5]
    return {"user": username, "age": age}

@app.post("/crunchData")
async def crunch():
    print("Attempting!")
    SERIES = "LNS14000000"  # unemployment rate (CPS)
    import datetime as dt
    today = dt.date.today()
    ten_years_ago = today.replace(year=today.year - 10)

    # Ask BLS for a broad year window; we'll trim to the last 120 months below.
    payload = {
        "seriesid": [SERIES],
        "startyear": str(ten_years_ago.year),
        "endyear": str(today.year),
        # "registrationkey": "YOUR_BLS_KEY",  # optional
    }

    r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=payload)
    r.raise_for_status()
    data = r.json()["Results"]["series"][0]["data"]  # newest first

    df = pd.DataFrame(data)

    # Keep only monthly rows (M01..M12), drop annual average (M13)
    df = df[df["period"].str.fullmatch(r"M\d{2}")]
    df = df[df["period"] != "M13"]

    # Build a proper date and numeric value
    df["year"] = df["year"].astype(int)
    df["month"] = df["period"].str[1:].astype(int)   # "M09" -> 9
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    df["unemployment_rate"] = pd.to_numeric(df["value"])

    # Sort oldest→newest and trim to exactly the last 120 months
    df = df.sort_values("date")[["date", "unemployment_rate"]]
    df = df[df["date"] >= pd.Timestamp(ten_years_ago.replace(day=1))].tail(120).reset_index(drop=True)

    print(df.head())
    print(df.tail(), len(df))

    plt.figure(figsize=(10,5))
    plt.plot(df["date"], df["unemployment_rate"], marker="o", linewidth=1)
    plt.title("U.S. Unemployment Rate (Past 10 Years)")
    plt.xlabel("Date")
    plt.ylabel("Unemployment Rate (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
