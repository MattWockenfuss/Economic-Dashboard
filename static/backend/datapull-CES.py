import csv
import requests

# ===============================================
# Constants
# ===============================================
CES_SERIES_URL = "https://download.bls.gov/pub/time.series/ce/ce.series"

# ===============================================
# Map human-friendly names to codes
# ===============================================
STATE_CES_CODES = {
    "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
    "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10",
    "District Of Columbia": "11", "Florida": "12", "Georgia": "13", "Hawaii": "15",
    "Idaho": "16", "Illinois": "17", "Indiana": "18", "Iowa": "19",
    "Kansas": "20", "Kentucky": "21", "Louisiana": "22", "Maine": "23",
    "Maryland": "24", "Massachusetts": "25", "Michigan": "26", "Minnesota": "27",
    "Mississippi": "28", "Missouri": "29", "Montana": "30", "Nebraska": "31",
    "Nevada": "32", "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35",
    "New York": "36", "North Carolina": "37", "North Dakota": "38", "Ohio": "39",
    "Oklahoma": "40", "Oregon": "41", "Pennsylvania": "42", "Rhode Island": "44",
    "South Carolina": "45", "South Dakota": "46", "Tennessee": "47", "Texas": "48",
    "Utah": "49", "Vermont": "50", "Virginia": "51", "Washington": "53",
    "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56",
    "Puerto Rico": "72"
}

CES_INDUSTRIES = {
    "total_nonfarm": "000000",
    "total_private": "050000",
    "manufacturing": "310000",
    "construction": "200000",
    "education_health": "650000",
    "leisure_hospitality": "700000"
}

CES_DATA_TYPES = {
    "employment": "01",
    "avg_weekly_hours": "02",
    "avg_hourly_earnings": "03",
    "avg_weekly_earnings": "30"
}

VALID_COMBINATIONS = {
    "employment": list(CES_INDUSTRIES.keys()),
    "avg_weekly_hours": ["total_nonfarm", "total_private", "manufacturing"],
    "avg_hourly_earnings": ["total_nonfarm", "total_private", "manufacturing", "construction"],
    "avg_weekly_earnings": ["total_nonfarm", "total_private"]
}

# ===============================================
# Fetch CES series CSV
# ===============================================
def fetch_ces_series_csv(url=CES_SERIES_URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    decoded = response.content.decode("utf-8").splitlines()

    header = [h.strip() for h in decoded[0].split("\t")]
    reader = csv.DictReader(decoded[1:], fieldnames=header, delimiter="\t")

    series_list = []
    for row in reader:
        clean_row = {k.strip(): v.strip() for k, v in row.items()}
        series_list.append(clean_row)

    return series_list

# ===============================================
# Search CES series for state, industry, data type
# ===============================================
def search_ces_series(state_name, industry, data_type):
    state_code = STATE_CES_CODES.get(state_name.title())
    if not state_code:
        raise ValueError(f"State '{state_name}' not recognized.")

    industry_code = CES_INDUSTRIES.get(industry)
    if not industry_code:
        raise ValueError(f"Industry '{industry}' not recognized.")

    dtype_code = CES_DATA_TYPES.get(data_type)
    if not dtype_code:
        raise ValueError(f"Data type '{data_type}' not recognized.")

    series_list = fetch_ces_series_csv()
    matches = []

    for row in series_list:
        series_id = row["series_id"]
        if series_id.startswith(f"CES{state_code}{industry_code}{dtype_code}"):
            matches.append({
                "series_id": series_id,
                "start_year": int(row["begin_year"]),
                "end_year": int(row["end_year"]),
                "seasonally_adjusted": row["seasonal"]
            })

    return matches

# ===============================================
# Universal BLS fetcher
# ===============================================
def write_id_bls(series_id, start_year, end_year):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": "e3283f60a62541dcbc49267fd7d79d1e"
    }
    response = requests.post(url, json=payload)
    data = response.json()
    results = {}
    if data.get("status") == "REQUEST_SUCCEEDED":
        for series in data["Results"]["series"]:
            for item in series["data"]:
                value_raw = item["value"]
                if value_raw in ("-", None):
                    continue
                try:
                    results[item["year"]] = float(value_raw)
                except ValueError:
                    continue
    return results

# ===============================================
# Fetch CES data with validation
# ===============================================
def get_ces_data(series_id, start_year, end_year):
    results = write_id_bls(series_id, start_year, end_year)
    if not results:
        print("Warning: No data returned. Series may not exist for the requested years or combination.")
    return results

# ===============================================
# Main program
# ===============================================
def main():
    print("=== CES State Labor Data Puller ===\n")

    # Select state
    state_name = input("Enter state or territory name: ").strip()

    # Select industry
    print("\nChoose an industry:")
    for i, key in enumerate(CES_INDUSTRIES.keys(), start=1):
        print(f"{i}. {key.replace('_', ' ').title()}")
    try:
        industry_idx = int(input("Enter industry number: ").strip()) - 1
        industry = list(CES_INDUSTRIES.keys())[industry_idx]
    except (ValueError, IndexError):
        print("Invalid industry selection.")
        return

    # Select data type
    print("\nChoose a data type:")
    for i, key in enumerate(CES_DATA_TYPES.keys(), start=1):
        print(f"{i}. {key.replace('_', ' ').title()}")
    try:
        dtype_idx = int(input("Enter data type number: ").strip()) - 1
        data_type = list(CES_DATA_TYPES.keys())[dtype_idx]
    except (ValueError, IndexError):
        print("Invalid data type selection.")
        return

    # Search available series and show years
    matches = search_ces_series(state_name, industry, data_type)
    if not matches:
        print("\nNo matching series found for this combination.")
        return

    # Assume taking the first matching series
    series = matches[0]
    print(f"\nSeries ID: {series['series_id']}")
    print(f"Seasonally Adjusted: {series['seasonally_adjusted']}")
    print(f"Available years: {series['start_year']} - {series['end_year']}")

    # Ask for user-specified year range
    try:
        start_year = int(input("\nEnter start year: "))
        end_year = int(input("Enter end year: "))
    except ValueError:
        print("Years must be integers.")
        return

    # Fetch data
    results = get_ces_data(series["series_id"], start_year, end_year)
    if not results:
        print("No data available for this selection.")
        return

    print(f"\nCES {data_type.replace('_',' ').title()} for {industry.replace('_',' ').title()} in {state_name} ({start_year}-{end_year}):")
    for year in sorted(results.keys()):
        print(f"  {year}: {results[year]}")

# ===============================================
# Run program
# ===============================================
if __name__ == "__main__":
    main()