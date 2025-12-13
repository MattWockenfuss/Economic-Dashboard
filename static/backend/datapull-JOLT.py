import requests


# ===============================================
# BLS STATE → JOLTS SERIES ID MAPPINGS
# ===============================================
# Note: These are the BLS JOLTS series IDs for state-level seasonally adjusted rates
# Format: JOLTS.<STATE CODE>.<SERIES> (rate)
# Series codes:
#   - JO = Job Openings Rate
#   - HI = Hires Rate
#   - QU = Quits Rate
#   - LA = Layoffs & Discharges Rate


STATE_CODES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District Of Columbia': 'DC'
}


SERIES_SUFFIX = {
    "job_openings": "JO",  # Job Openings Rate
    "hires": "HI",         # Hires Rate
    "quits": "QU",         # Quits Rate
    "layoffs": "LA"        # Layoffs & Discharges Rate
}


def get_jolts_series_id(state_name, metric):
    state_key = state_name.title()
    if state_key not in STATE_CODES:
        raise ValueError(f"State '{state_name}' not recognized.")
    if metric not in SERIES_SUFFIX:
        raise ValueError(f"Metric '{metric}' not recognized.")
    return f"JTS{STATE_CODES[state_key]}{SERIES_SUFFIX[metric]}"


# ===============================================
# FUNCTION 1: write_id_bls — universal BLS fetcher
# ===============================================
def write_id_bls(series_id, start_year, end_year):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
        # Remove registrationkey or replace with your own if available
    }


    response = requests.post(url, json=payload)
    data = response.json()
    results = {}


    if data.get("status") == "REQUEST_SUCCEEDED":
        for series in data["Results"]["series"]:
            for item in series["data"]:
                year = item["year"]
                month = item["periodName"]
                raw_value = item["value"]
                if raw_value == "-" or raw_value is None:
                    continue
                try:
                    value = float(raw_value)
                except ValueError:
                    continue
                results[f"{year}-{month}"] = value
    else:
        print("Error fetching data:", data.get("message"))


    return results


# ===============================================
# FUNCTION 2: get_state_data — picks correct JOLTS series
# ===============================================
def get_state_data(state_name, start_year, end_year, metric):
    series_id = get_jolts_series_id(state_name, metric)
    return write_id_bls(series_id, start_year, end_year)


# ===============================================
# FUNCTION 3: main — user-facing logic
# ===============================================
def main():
    print("=== BLS State JOLTS Data Puller ===\n")
    print("Choose a JOLTS data type:")
    print("1. Job Openings Rate (%)")
    print("2. Hires Rate (%)")
    print("3. Quits Rate (%)")
    print("4. Layoffs & Discharges Rate (%)")


    choice = input("Enter choice (1-4): ").strip()
    metric_choices = {"1": "job_openings", "2": "hires", "3": "quits", "4": "layoffs"}


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
            "job_openings": "Job Openings Rate (%)",
            "hires": "Hires Rate (%)",
            "quits": "Quits Rate (%)",
            "layoffs": "Layoffs & Discharges Rate (%)"
        }


        print(f"\n{label_map[metric]} for {state_name} ({start_year}-{end_year}):")
        for period in sorted(results.keys()):
            print(f"  {period}: {results[period]}")
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
