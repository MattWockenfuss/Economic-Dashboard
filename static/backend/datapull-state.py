import requests
import sys

# --- Configuration ---
# Your Census API Key - Provided by the user
API_KEY = "8c89ade2c8b3039efd1f9361da0add23b6374196"

# Census API Endpoint (using the American Community Survey 5-Year Estimates)
CENSUS_API_BASE_URL = "https://api.census.gov/data/{year}/acs/acs5"

# State FIPS Code Lookup (Includes all 50 states plus the District of Columbia)
# FIPS codes are necessary for geographic queries.
STATE_FIPS_MAP = {
    "AL": "01", "Alabama": "01",
    "AK": "02", "Alaska": "02",
    "AZ": "04", "Arizona": "04",
    "AR": "05", "Arkansas": "05",
    "CA": "06", "California": "06",
    "CO": "08", "Colorado": "08",
    "CT": "09", "Connecticut": "09",
    "DE": "10", "Delaware": "10",
    "DC": "11", "District of Columbia": "11",
    "FL": "12", "Florida": "12",
    "GA": "13", "Georgia": "13",
    "HI": "15", "Hawaii": "15",
    "ID": "16", "Idaho": "16",
    "IL": "17", "Illinois": "17",
    "IN": "18", "Indiana": "18",
    "IA": "19", "Iowa": "19",
    "KS": "20", "Kansas": "20",
    "KY": "21", "Kentucky": "21",
    "LA": "22", "Louisiana": "22",
    "ME": "23", "Maine": "23",
    "MD": "24", "Maryland": "24",
    "MA": "25", "Massachusetts": "25",
    "MI": "26", "Michigan": "26",
    "MN": "27", "Minnesota": "27",
    "MS": "28", "Mississippi": "28",
    "MO": "29", "Missouri": "29",
    "MT": "30", "Montana": "30",
    "NE": "31", "Nebraska": "31",
    "NV": "32", "Nevada": "32",
    "NH": "33", "New Hampshire": "33",
    "NJ": "34", "New Jersey": "34",
    "NM": "35", "New Mexico": "35",
    "NY": "36", "New York": "36",
    "NC": "37", "North Carolina": "37",
    "ND": "38", "North Dakota": "38",
    "OH": "39", "Ohio": "39",
    "OK": "40", "Oklahoma": "40",
    "OR": "41", "Oregon": "41",
    "PA": "42", "Pennsylvania": "42",
    "RI": "44", "Rhode Island": "44",
    "SC": "45", "South Carolina": "45",
    "SD": "46", "South Dakota": "46",
    "TN": "47", "Tennessee": "47",
    "TX": "48", "Texas": "48",
    "UT": "49", "Utah": "49",
    "VT": "50", "Vermont": "50",
    "VA": "51", "Virginia": "51",
    "WA": "53", "Washington": "53",
    "WV": "54", "West Virginia": "54",
    "WI": "55", "Wisconsin": "55",
    "WY": "56", "Wyoming": "56",
}

# Census Variable IDs and their Human-Readable Names (Estimates, ending in 'E')
# These variables provide the requested total population, sex, age groups, race, and Hispanic origin.
# Note: ACS data often uses non-overlapping categories (e.g., Race categories are "alone").
DEMOGRAPHIC_VARIABLES = {
    # Population Totals
    "B01001_001E": "Total Population (Estimate)",

    # Sex
    "B01001_002E": "Total Male",
    "B01001_026E": "Total Female",

    # Age Groups (Selected Key Ranges)
    "B01001_003E": "Age: Male, Under 5 years",
    "B01001_010E": "Age: Male, 25 to 34 years",
    "B01001_013E": "Age: Male, 45 to 54 years",
    "B01001_020E": "Age: Male, 65 to 74 years",
    "B01001_027E": "Age: Female, Under 5 years",
    "B01001_034E": "Age: Female, 25 to 34 years",
    "B01001_037E": "Age: Female, 45 to 54 years",
    "B01001_044E": "Age: Female, 65 to 74 years",

    # Race (Alone categories)
    "B02001_002E": "Race: White alone",
    "B02001_003E": "Race: Black or African American alone",
    "B02001_005E": "Race: Asian alone",
    "B02001_008E": "Race: Some other race alone",

    # Hispanic Origin (Note: Hispanic/Latino is considered an ethnicity, not a race by the Census)
    "B03003_003E": "Hispanic or Latino Origin",
}

def get_state_fips(state_name_or_abbr):
    """
    Looks up the state FIPS code based on the state name or abbreviation.
    Handles case-insensitivity.
    """
    normalized_input = state_name_or_abbr.strip().upper()
    
    # Try FIPS from map using the original input first
    fips = STATE_FIPS_MAP.get(state_name_or_abbr.strip(), None)
    if fips:
        return fips
    
    # Check abbreviations (TX, CA, etc.)
    if len(state_name_or_abbr.strip()) == 2:
        return STATE_FIPS_MAP.get(normalized_input, None)
    
    # Check full names (California, Texas, etc.)
    for key, val in STATE_FIPS_MAP.items():
        if key.upper() == normalized_input:
            return val
            
    return None

def fetch_census_data(state_name, year):
    """
    Constructs the API URL, fetches the data, and returns the parsed results.
    """
    fips_code = get_state_fips(state_name)
    if not fips_code:
        print(f"Error: State '{state_name}' FIPS code not found in the lookup map.")
        print("Please use a 2-letter abbreviation or full name from the supported list (or add more to STATE_FIPS_MAP).")
        return None

    # Join all requested variables into a single comma-separated string
    get_vars = ",".join(DEMOGRAPHIC_VARIABLES.keys())
    
    # Construct the full API URL
    api_url = CENSUS_API_BASE_URL.format(year=year)
    
    params = {
        "get": f"{get_vars},NAME", # Always request NAME to confirm the state
        "for": f"state:{fips_code}",
        "key": API_KEY,
    }

    print(f"Fetching data for {state_name} ({fips_code}) for the year {year}...")
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        
        # The first row is the header, the second row is the data
        if len(data) < 2:
            print("Error: No data found or API returned an empty response.")
            return None
        
        header = data[0]
        values = data[1]
        
        # Map the results to the friendly variable names
        results = {}
        for i, h in enumerate(header):
            # Check if the header is one of our requested variable IDs
            if h in DEMOGRAPHIC_VARIABLES:
                friendly_name = DEMOGRAPHIC_VARIABLES[h]
                # Convert the census value (string) to an integer for display
                try:
                    results[friendly_name] = int(values[i])
                except ValueError:
                    results[friendly_name] = values[i] # Keep as string if conversion fails
            elif h == "NAME":
                results["State Name"] = values[i]
                
        return results

    except requests.exceptions.RequestException as e:
        print(f"\nAn error occurred during the API request: {e}")
        return None
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return None

def display_results(results):
    """
    Formats and prints the demographic data.
    """
    if not results:
        return

    print("-" * 50)
    print(f"DEMOGRAPHIC DATA FOR: {results.get('State Name', 'N/A')}")
    print("-" * 50)
    
    # Total Population
    print(f"{'Total Population:':<35}{results.get('Total Population (Estimate)', 'N/A'):>15,}")
    print("-" * 50)

    # Sex Breakdown
    print("\n--- Sex ---")
    print(f"{'Total Male:':<35}{results.get('Total Male', 'N/A'):>15,}")
    print(f"{'Total Female:':<35}{results.get('Total Female', 'N/A'):>15,}")
    print("-" * 50)

    # Age Groups (Selected)
    print("\n--- Age Groups (Selected) ---")
    age_keys = [k for k in results.keys() if k.startswith("Age:")]
    for key in sorted(age_keys):
         print(f"{key:<35}{results.get(key, 'N/A'):>15,}")
    print("-" * 50)

    # Race/Hispanic Origin
    print("\n--- Race & Hispanic Origin ---")
    race_keys = [k for k in results.keys() if k.startswith("Race:")]
    for key in sorted(race_keys):
         print(f"{key:<35}{results.get(key, 'N/A'):>15,}")
         
    print(f"{'Hispanic or Latino Origin:':<35}{results.get('Hispanic or Latino Origin', 'N/A'):>15,}")
    print("-" * 50)


if __name__ == "__main__":
    print("--- US Census Data Fetcher ---")
    print("This tool fetches demographic data from the ACS 5-Year Estimates.")
    
    # 1. Get State Input
    # Extract only the full state names for the list display
    full_state_names = sorted([k for k, v in STATE_FIPS_MAP.items() if len(k) > 2 and k not in STATE_FIPS_MAP.values()])
    supported_abbreviations = sorted([k for k in STATE_FIPS_MAP.keys() if len(k) == 2])

    # Improved display of supported states
    print("\nSupported States (Enter Name or Abbreviation):")
    # Format the names into columns for easier reading
    num_cols = 5
    col_width = 15
    for i in range(0, len(full_state_names), num_cols):
        row = full_state_names[i:i + num_cols]
        print("  " + "".join(f"{name:<{col_width}}" for name in row))
    
    print("\n  Abbreviations: (e.g., CA, TX, NY, FL, etc.)")

    target_state = input("Enter the state name or 2-letter abbreviation: ").strip()

    # 2. Get Year Input
    while True:
        target_year_str = input("Enter the desired year (e.g., 2022): ").strip()
        try:
            target_year = int(target_year_str)
            if target_year < 2010 or target_year > 2023:
                 print("Warning: Census ACS 5-Year data is typically available up to 2022/2023. Using a very old or future year might fail, but proceeding anyway.")
            break
        except ValueError:
            print("Invalid year input. Please enter a numerical year.")
            
    print("-" * 30)

    # Run the fetch operation
    demographic_data = fetch_census_data(target_state, target_year)
    
    # Display the results
    if demographic_data:
        display_results(demographic_data)
    else:
        print("Failed to retrieve or display data. Please check your state name and year.")
        
    print("\nScript finished.")
    print("\nNote: The data is based on the 5-Year American Community Survey (ACS) estimates for the chosen year.")