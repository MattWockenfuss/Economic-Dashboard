from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi import Form

import requests
import json
import random

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt 
import Database

# from Database import (
#     init_db, 
#     populate_states,
#     insert_gdp,
#     insert_population,
#     insert_unemployment,
#     insert_income,
#     insert_cost_of_living,
#     insert_growth,
#     get_gdp,
#     get_population,
#     get_unemployment,
#     get_income,
#     get_cost_of_living,
#     get_growth,
#     get_all_data_for_year
# )


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# # Initialize database on startup
# @app.on_event("startup")
# async def startup_event():
#     init_db()
#     populate_states()
#     print("Database initialized on startup!")


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title":"Welcome!"})

VALID_MAPMODES = ["POPULATION", "GDP"]

@app.get("/mapmode/{mapmode}")
async def mapdata(mapmode):
    print(f"HELLO {mapmode}")
    states = [
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
        "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
        "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
        "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
        "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
    ]

    years = [2000, 2001, 2021, 2022, 2023]

    gdp = {}

    for year in range(1950, 2025):
        gdp[str(year)] = {}
        for state in states:
            # random GDP value (replace with real data if needed)
            gdp[str(year)][state] = random.randint(100, 1000)

    output = {
        "gdp": gdp
    }

    
    json_data = json.dumps(output, indent=4)

    print(json_data)
    return json_data





    print(f"This function makes a request for data from the database")
    if mapmode not in VALID_MAPMODES:
        print(f"[ERROR] USER tried to pull '{mapmode}', which is not a valid mapmode!")

    #okay so the mapmode is defined, lets go fetch










{
  "mode": "GDP",
  "data": {
    "CA": {
      "1980": 12345.67,
      "1981": 13000.11
    },
    "TX": {
      "1980": 9876.54
    }
  }
}






@app.post("/submit")
async def submit(username: str = Form(...), age: int = Form(...)):
    print(f"Username: {username} Age: {age}")  #we can accept user input from front end in terms of form
    arr = np.array[1,2,3,4,5]
    return {"user": username, "age": age}

# New database-related endpoints
@app.get("/api/bls/{state}")
async def get_state_bls_data(state: str, year: int = None, metric: str = None):
    """Get BLS data for a specific state"""
    data = get_bls_data(state=state, year=year, metric_type=metric)
    return {"state": state, "data": data}


@app.get("/api/fred/{state}")
async def get_state_fred_data(state: str, metric: str = None):
   
    data = get_fred_data(state=state, metric_type=metric)
    return {"state": state, "data": data}


@app.post("/api/fetch-and-store")
async def fetch_and_store_data(state: str, metric: str, start_year: int, end_year: int):

    # This integrates with Our existing BLS data fetching logic
    SERIES = "LNS14000000"
    
    payload = {
        "seriesid": [SERIES],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    
    r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=payload)
    r.raise_for_status()
    data = r.json()["Results"]["series"][0]["data"]
    
    # Store in database
    stored_count = 0
    for item in data:
        if item["period"] != "M13":  # Skip annual average
            insert_bls_data(
                series_id=SERIES,
                state=state,
                
                year=int(item["year"]),
                period=item["period"],
                value=float(item["value"]),
                metric_type=metric
            )
            stored_count += 1


    
    return {"message": f"Stored {stored_count} data points", "state": state}



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

     #Store fetched data in database
    for _, row in df.iterrows():
        insert_bls_data(
            series_id=SERIES,
            state="National",
            year=row["date"].year,
            period=f"M{row['date'].month:02d}",
            value=row["unemployment_rate"],
            metric_type="unemployment_rate"
        )
    
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
