import requests
import json


# ===============================================
# BLS STATE → SERIES ID MAPPINGS
# ===============================================

UNEMP_RATE_SERIES = {    # ...003
    'Alabama': 'LASST010000000000003',
    'Alaska': 'LASST020000000000003',
    'Arizona': 'LASST040000000000003',
    'Arkansas': 'LASST050000000000003',
    'California': 'LASST060000000000003',
    'Colorado': 'LASST080000000000003',
    'Connecticut': 'LASST090000000000003',
    'Delaware': 'LASST100000000000003',
    'Florida': 'LASST120000000000003',
    'Georgia': 'LASST130000000000003',
    'Hawaii': 'LASST150000000000003',
    'Idaho': 'LASST160000000000003',
    'Illinois': 'LASST170000000000003',
    'Indiana': 'LASST180000000000003',
    'Iowa': 'LASST190000000000003',
    'Kansas': 'LASST200000000000003',
    'Kentucky': 'LASST210000000000003',
    'Louisiana': 'LASST220000000000003',
    'Maine': 'LASST230000000000003',
    'Maryland': 'LASST240000000000003',
    'Massachusetts': 'LASST250000000000003',
    'Michigan': 'LASST260000000000003',
    'Minnesota': 'LASST270000000000003',
    'Mississippi': 'LASST280000000000003',
    'Missouri': 'LASST290000000000003',
    'Montana': 'LASST300000000000003',
    'Nebraska': 'LASST310000000000003',
    'Nevada': 'LASST320000000000003',
    'New Hampshire': 'LASST330000000000003',
    'New Jersey': 'LASST340000000000003',
    'New Mexico': 'LASST350000000000003',
    'New York': 'LASST360000000000003',
    'North Carolina': 'LASST370000000000003',
    'North Dakota': 'LASST380000000000003',
    'Ohio': 'LASST390000000000003',
    'Oklahoma': 'LASST400000000000003',
    'Oregon': 'LASST410000000000003',
    'Pennsylvania': 'LASST420000000000003',
    'Rhode Island': 'LASST440000000000003',
    'South Carolina': 'LASST450000000000003',
    'South Dakota': 'LASST460000000000003',
    'Tennessee': 'LASST470000000000003',
    'Texas': 'LASST480000000000003',
    'Utah': 'LASST490000000000003',
    'Vermont': 'LASST500000000000003',
    'Virginia': 'LASST510000000000003',
    'Washington': 'LASST530000000000003',
    'West Virginia': 'LASST540000000000003',
    'Wisconsin': 'LASST550000000000003',
    'Wyoming': 'LASST560000000000003',
    'District Of Columbia': 'LASST110000000000003',
    'Puerto Rico': 'LASST720000000000003',
}

# Expand systematically using LAUS code conventions
EMPLOYMENT_SERIES   = {s: sid.replace("003", "005") for s, sid in UNEMP_RATE_SERIES.items()}
UNEMP_RAW_SERIES    = {s: sid.replace("003", "004") for s, sid in UNEMP_RATE_SERIES.items()}
LABOR_FORCE_SERIES  = {s: sid.replace("003", "006") for s, sid in UNEMP_RATE_SERIES.items()}


# ===============================================
# FUNCTION 1: write-id-BLS — universal BLS fetcher
# ===============================================

def write_id_bls(series_id, start_year, end_year):
    """
    Fetches ANY BLS time series.
    Returns: dict {year: value}
    Skips missing values ("-").
    """

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
                year = item["year"]
                raw_value = item["value"]

                if raw_value == "-" or raw_value is None:
                    continue

                try:
                    value = float(raw_value)
                except ValueError:
                    continue

                results[year] = value

    return results


# ===============================================
# FUNCTION 2: get-state-data — picks correct series
# ===============================================

def get_state_data(state_name, start_year, end_year, metric):
    """
    metric options:
      - 'unemployment_rate'
      - 'employment'
      - 'unemployment_raw'
      - 'labor_force'
    """

    state_key = state_name.title()

    METRIC_MAP = {
        "unemployment_rate": UNEMP_RATE_SERIES,
        "employment": EMPLOYMENT_SERIES,
        "unemployment_raw": UNEMP_RAW_SERIES,
        "labor_force": LABOR_FORCE_SERIES,
    }

    if metric not in METRIC_MAP:
        raise ValueError("Invalid metric.")

    series_dict = METRIC_MAP[metric]

    if state_key not in series_dict:
        raise ValueError(f"State '{state_name}' not recognized.")

    series_id = series_dict[state_key]

    return write_id_bls(series_id, start_year, end_year)


# ===============================================
# FUNCTION 3: main — unchanged user-facing logic
# ===============================================

def main():
    print("=== BLS State Labor Data Puller ===\n")

    print("Choose a data type:")
    print("1. Unemployment rate (%)")
    print("2. Employment level")
    print("3. Raw unemployment (number of unemployed persons)")
    print("4. Labor force (total employed + unemployed)")

    choice = input("Enter choice (1-4): ").strip()

    metric_choices = {
        "1": "unemployment_rate",
        "2": "employment",
        "3": "unemployment_raw",
        "4": "labor_force"
    }

    if choice not in metric_choices:
        print("Invalid choice.")
        return

    metric = metric_choices[choice]

    state_name = input("Enter state or territory name: ").strip()

    try:
        start_year = int(input("Enter start year: "))
        end_year = int(input("Enter end year: "))
    except ValueError:
        print("Years must be integers.")
        return

    try:
        results = get_state_data(state_name, start_year, end_year, metric)
        label_map = {
            "unemployment_rate": "Unemployment Rate (%)",
            "employment": "Employment Level",
            "unemployment_raw": "Raw Unemployment Level",
            "labor_force": "Total Labor Force"
        }

        print(f"\n{label_map[metric]} for {state_name} ({start_year}-{end_year}):")
        for year in sorted(results.keys()):
            print(f"  {year}: {results[year]}")

    except ValueError as e:
        print(f"Error: {e}")


# Run program
if __name__ == "__main__":
    main()