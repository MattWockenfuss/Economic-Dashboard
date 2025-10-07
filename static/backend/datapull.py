import requests
import json
import prettytable

def read_BLS(series_id, start_year, end_year):
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year)
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise Exception(f"BLS API request failed: {response.status_code}, {response.text}")

    data = response.json()
    try:
        results = data['Results']['series'][0]['data']
    except (KeyError, IndexError):
        raise Exception("Invalid response format or series ID not found.")
    
    return results

def write_ID(state, data_type, seasonally_adjusted):
    state_codes = {
        'Alabama': '01', 'Alaska': '02', 'Arizona': '04', 'Arkansas': '05', 'California': '06',
        'Colorado': '08', 'Connecticut': '09', 'Delaware': '10', 'Florida': '12', 'Georgia': '13',
        'Hawaii': '15', 'Idaho': '16', 'Illinois': '17', 'Indiana': '18', 'Iowa': '19',
        'Kansas': '20', 'Kentucky': '21', 'Louisiana': '22', 'Maine': '23', 'Maryland': '24',
        'Massachusetts': '25', 'Michigan': '26', 'Minnesota': '27', 'Mississippi': '28',
        'Missouri': '29', 'Montana': '30', 'Nebraska': '31', 'Nevada': '32', 'New Hampshire': '33',
        'New Jersey': '34', 'New Mexico': '35', 'New York': '36', 'North Carolina': '37',
        'North Dakota': '38', 'Ohio': '39', 'Oklahoma': '40', 'Oregon': '41', 'Pennsylvania': '42',
        'Rhode Island': '44', 'South Carolina': '45', 'South Dakota': '46', 'Tennessee': '47',
        'Texas': '48', 'Utah': '49', 'Vermont': '50', 'Virginia': '51', 'Washington': '53',
        'West Virginia': '54', 'Wisconsin': '55', 'Wyoming': '56', 'District of Columbia': '11',
        'Puerto Rico': '72'
    } #No 67 state yet. Sad!

def main():
    print("Developer Testing: BLS Data Read")
    series_id = input("Enter BLS Series ID: ").strip()
    start_year = input("Enter start year: ").strip()
    end_year = input("Enter end year: ").strip()

    try:
        data = read_BLS(series_id, start_year, end_year)
        print(f"\n--- Top {min(10, len(data))} Data Points for {series_id} ---")
        for item in data[:10]:  # Show latest 10 results
            print(f"{item['year']} - {item['periodName']}: {item['value']}%")
    except Exception as e:
        print("Error fetching data:", str(e))

if __name__ == "__main__":
    main()