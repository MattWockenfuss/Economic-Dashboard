import csv
import requests

# ===============================================
# Constants
# ===============================================
JOLTS_SERIES_URL = "https://download.bls.gov/pub/time.series/jolts/jolts.series"

# ===============================================
# Human-readable metrics
# ===============================================
JOLTS_METRICS = {
    "job_openings": "JO",
    "hires": "HI",
    "quits": "QU",
    "layoffs": "LD"
}

# ===============================================
# State codes (same as CES)
# ===============================================
STATE_CODES = {
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

# ===============================================
# Fetch JOLTS series metadata
# ===============================================
def fetch_jolts_series_csv(url=JOLTS_SERIES_URL):
    headers = {
        "User-Agent": "Mozilla/5.0"
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
# Search for a series by state and metric
# ===============================================
def search_jolts_series(state_name, metric):
    state_code = STATE_CODES.get(state_name.title())
    if not state_code:
        raise ValueError(f"State '{state_name}' not recognized.")

    metric_code = JOLTS_METRICS.get(metric)
    if not metric_code:
        raise ValueError(f"Metric '{metric}' not recognized.")

    series_list = fetch_jolts_series_csv()
    matches = []

    for row in series_list:
        series_id = row["series_id"]
        if series_id.startswith(f"JOLTS{state_code}{metric_code}"):
            matches.append({
                "series_id": series_id,
                "start_year": int(row["begin_year"]),
                "end_year": int(row["end_year"]),
                "seasonally_adjusted": row["seasonal"]
            })

    return matches

# ===============================================
# Fetch data from BLS API
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
# Main program
# ===============================================
def main():
    print("=== JOLTS State Data Puller ===\n")

    state_name = input("Enter state or territory name: ").strip()

    print("\nChoose a metric:")
    for i, key in enumerate(JOLTS_METRICS.keys(), start=1):
        print(f"{i}. {key.replace('_',' ').title()}")
    try:
        metric_idx = int(input("Enter metric number: ").strip()) - 1
        metric = list(JOLTS_METRICS.keys())[metric_idx]
    except (ValueError, IndexError):
        print("Invalid metric selection.")
        return

    matches = search_jolts_series(state_name, metric)
    if not matches:
        print("\nNo matching series found for this combination.")
        return

    series = matches[0]
    print(f"\nSeries ID: {series['series_id']}")
    print(f"Seasonally Adjusted: {series['seasonally_adjusted']}")
    print(f"Available years: {series['start_year']} - {series['end_year']}")

    try:
        start_year = int(input("\nEnter start year: "))
        end_year = int(input("Enter end year: "))
    except ValueError:
        print("Years must be integers.")
        return

    results = write_id_bls(series["series_id"], start_year, end_year)
    if not results:
        print("No data available for this selection.")
        return

    print(f"\nJOLTS {metric.replace('_',' ').title()} for {state_name} ({start_year}-{end_year}):")
    for year in sorted(results.keys()):
        print(f"  {year}: {results[year]}")

# ===============================================
# Run program
# ===============================================
if __name__ == "__main__":
    main()