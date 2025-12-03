import requests

def get_state_gdp():
    """Fetch state GDP data from FRED API"""
    
    # Get API key from user or environment
    api_key = input("Enter your FRED API key: ").strip()
    
    # List of US states and territories
    states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
        "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
        "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
        "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
        "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
        "New Hampshire", "New Jersey", "New Mexico", "New York",
        "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
        "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
        "West Virginia", "Wisconsin", "Wyoming"
    ]
    
    print("\nAvailable states:")
    for i, state in enumerate(states, 1):
        print(f"{i}. {state}")
    
    # Get user input
    while True:
        try:
            choice = int(input(f"\nSelect a state (1-{len(states)}): "))
            if 1 <= choice <= len(states):
                state = states[choice - 1]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # FRED series IDs for state GDP (example format)
    state_code = state.upper()[:2]
    series_id = f"NGP{state_code}"  # FRED state GDP series ID format
    
    # Call FRED API
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "observations" in data:
            print(f"\nGDP data for {state}:")
            for obs in data["observations"][-5:]:  # Last 5 observations
                print(f"{obs['date']}: {obs['value']}")
        else:
            print(f"No data found for {state}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    get_state_gdp()