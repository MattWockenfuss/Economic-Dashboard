#I was able to test everything except Seasonally Adjusted; if it isn't working, set
#it to "True" in the read_BLS def



import requests
import json
import prettytable #holdover from sample code; could be useful


API_KEY = "e3283f60a62541dcbc49267fd7d79d1e"



headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": ['CUUR0000SA0','SUUR0000SA0'],"startyear":"2011", "endyear":"2014"})
p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)



json_data = json.loads(p.text)



for series in json_data['Results']['series']:
    x=prettytable.PrettyTable(["series id","year","period","value","footnotes"])
    seriesId = series['seriesID']
    for item in series['data']:
        year = item['year']
        period = item['period']
        value = item['value']
        footnotes=""
        for footnote in item['footnotes']:
            if footnote:
                footnotes = footnotes + footnote['text'] + ','
        if 'M01' <= period <= 'M12':
            x.add_row([seriesId,year,period,value,footnotes[0:-1]])
    output = open(seriesId + '.txt','w')
    output.write (x.get_string())
    output.close()





def read_BLS(series_id, start_year, end_year): #this actually calls fata from the API
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    #series_id = LAUST42000000000003
    payload = {
        "seriesid":[str(series_id)], 
        "startyear":str(start_year), 
        "endyear":str(end_year),
        "catalog": True, 
        "calculations": True, 
        "annualaverage": True,
        "registrationkey":API_KEY 
        }
    
    response = requests.post(url, json=payload)

    if response.status_code != 200: #error handling
        raise Exception(f"BLS API request failed: {response.status_code}, {response.text}")

    data = response.json()
    try:
        results = data['Results']['series'][0]['data']
    except (KeyError, IndexError):
        raise Exception("Invalid response format or series ID not found.")
    
    


    return results

def write_ID(state_name, data_type, seasonally_adjusted):
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
    }

    state_code = state_codes.get(state_name.title())
    if not state_code:
        raise ValueError(f"State '{state_name}' not recognized.")

    prefix = "LAUST"  # Local Area Statistics - State; data series header
    #next expansion- incorporate different tables
    
    # Define suffixes for SA and NSA
    data_type_suffixes = {
        'unemployment_rate': {
            True:  '000000000003',
            False: '000000000004'
        },
        'unemployed': {
            True:  '000000000007',
            False: '000000000008'
        },
        'employment': {
            True:  '000000000005',
            False: '000000000006'
        },
        'labor_force': {
            True:  '000000000009',
            False: '000000000010'
        }
    }
    #Maybe include data validation- suffix should always be 12 characters

    data_type = data_type.lower()
    if data_type not in data_type_suffixes:
        raise ValueError(f"Data type '{data_type}' is not supported.")

    suffix = data_type_suffixes[data_type][seasonally_adjusted]

    return prefix + state_code + suffix

def main():
    print("Developer Testing: BLS Data Read")
    state = input("Enter State: ").strip()
    print("Available data types: unemployment_rate, employment, labor_force, unemployed")
    data_type = input("Enter Data Type: ").strip().lower()
    start_year = input("Enter Start Year: ").strip()
    end_year = input("Enter End Year: ").strip()
    sa_input = input("Seasonally Adjusted? (yes/no): ").strip().lower()
    seasonally_adjusted = sa_input.startswith('y')
    #seasonally_adjusted is true/false depending
    try:
        #series_id = write_ID(state, data_type, seasonally_adjusted)
        #print(f"Using Series ID: {series_id}")
        
        #data = read_BLS(series_id, start_year, end_year)
        data = read_BLS("LAUST42000000000003", 2020, 2025)

        if not data:
            print("No data returned. Check your inputs or try different years.")
            return

        print(f"\n--- Top {min(10, len(data))} Data Points for {state.title()} ({data_type}) ---")
        for item in data[:10]:
            print(f"{item['year']} - {item['periodName']}: {item['value']}")

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    main()