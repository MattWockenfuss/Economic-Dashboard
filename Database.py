import sqlite3
from contextlib import contextmanager
from typing import Optional
import os

DATABASE_PATH = "economic_data.db"


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


'''






'''

def init_db():
    """Initialize database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Table for BLS time series data (unemployment, employment, etc.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bls_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id TEXT NOT NULL,
                state TEXT,
                year INTEGER NOT NULL,
                period TEXT NOT NULL,
                value REAL,
                metric_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(series_id, year, period)
            )
        ''')
        
        # Table for FRED data (GDP, etc.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fred_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_id TEXT NOT NULL,
                state TEXT,
                date TEXT NOT NULL,
                value REAL,
                metric_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(series_id, date)
            )
        ''')
        
        # Table for state metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                abbreviation TEXT UNIQUE NOT NULL,
                fips_code TEXT
            )
        ''')
        
        # Table for caching API responses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                params TEXT,
                response TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bls_state ON bls_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bls_year ON bls_data(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fred_state ON fred_data(state)')
        
        print("Database initialized successfully!")


# CRUD operations for BLS data
def insert_bls_data(series_id: str, state: str, year: int, period: str, 
                    value: float, metric_type: str):
    """Insert or update BLS data point."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO bls_data 
            (series_id, state, year, period, value, metric_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (series_id, state, year, period, value, metric_type))




def get_bls_data(state: Optional[str] = None, year: Optional[int] = None,
                 metric_type: Optional[str] = None):
                   
    """Retrieve BLS data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM bls_data WHERE 1=1"
        params = []
        
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type)
        
        query += " ORDER BY year DESC, period DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def insert_fred_data(series_id: str, state: str, date: str, 
                     value: float, metric_type: str):
    """Insert or update FRED data point."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO fred_data 
            (series_id, state, date, value, metric_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (series_id, state, date, value, metric_type))


def get_fred_data(state: Optional[str] = None, metric_type: Optional[str] = None):
    """Retrieve FRED data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM fred_data WHERE 1=1"
        params = []
        
        if state:
            query += " AND state = ?"
            params.append(state)


      
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type)
        
        query += " ORDER BY date DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def populate_states():
    """Populate the states table with US states data."""
    states_data = [
        ("Alabama", "AL", "01"), ("Alaska", "AK", "02"), ("Arizona", "AZ", "04"),
        ("Arkansas", "AR", "05"), ("California", "CA", "06"), ("Colorado", "CO", "08"),
        ("Connecticut", "CT", "09"), ("Delaware", "DE", "10"), ("Florida", "FL", "12"),
        ("Georgia", "GA", "13"), ("Hawaii", "HI", "15"), ("Idaho", "ID", "16"),
        ("Illinois", "IL", "17"), ("Indiana", "IN", "18"), ("Iowa", "IA", "19"),
        ("Kansas", "KS", "20"), ("Kentucky", "KY", "21"), ("Louisiana", "LA", "22"),
        ("Maine", "ME", "23"), ("Maryland", "MD", "24"), ("Massachusetts", "MA", "25"),
        ("Michigan", "MI", "26"), ("Minnesota", "MN", "27"), ("Mississippi", "MS", "28"),
        ("Missouri", "MO", "29"), ("Montana", "MT", "30"), ("Nebraska", "NE", "31"),
        ("Nevada", "NV", "32"), ("New Hampshire", "NH", "33"), ("New Jersey", "NJ", "34"),
        ("New Mexico", "NM", "35"), ("New York", "NY", "36"), ("North Carolina", "NC", "37"),
        ("North Dakota", "ND", "38"), ("Ohio", "OH", "39"), ("Oklahoma", "OK", "40"),
        ("Oregon", "OR", "41"), ("Pennsylvania", "PA", "42"), ("Rhode Island", "RI", "44"),
        ("South Carolina", "SC", "45"), ("South Dakota", "SD", "46"), ("Tennessee", "TN", "47"),
        ("Texas", "TX", "48"), ("Utah", "UT", "49"), ("Vermont", "VT", "50"),
        ("Virginia", "VA", "51"), ("Washington", "WA", "53"), ("West Virginia", "WV", "54"),
        ("Wisconsin", "WI", "55"), ("Wyoming", "WY", "56"), ("District of Columbia", "DC", "11"),
        ("Puerto Rico", "PR", "72")
    ]
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR IGNORE INTO states (name, abbreviation, fips_code)
            VALUES (?, ?, ?)
        ''', states_data)
        print(f"Populated {len(states_data)} states")



def getData(mapmode):
    #we can assume that the user is pulling specific data about the FRED or BLS in a given map mode.
    #we want to return all of the data associated with the 'gdp' mapmode,
    
    

    sqlcmd = f"""
        SELECT state_code, year, value
        FROM {mapmode}
        ORDER BY state_code, year
    """

    cur = get_db.cursor()
    try:
        cur.execute(sqlcmd)
        rows = cur.fetchall()
    finally:
        cur.close()
    
    if not rows:
        print(f"[ERROR] There was an error fetching the data for '{mapmode}'")

    # so now we have the data, looks like so
    #{
    #  "CA": { "1980": 12345.6, "1981": 13000.2 },
    #  "TX": { "1980": 9000.1 }
    #}

    #so lets reformat it
    data = {}
    for row in rows:
        state_code = row[0]
        year = row[1]
        value = row[2]

        #json keys must be strings so convert, might change format later
        year = str(year)

        #if the state hasnt been added, then add it
        if state_code not in data:
            data[state_code] = {}

        #otherwise we store it
        data[year][state_code] = value

    packet = {
        "ok": True,
        "mapmode": mapmode,
        "data": data
    }

    #okay so now we have our data we want to send to the front end
    return packet








# Run initialization when this module is executed directly
if __name__ == "__main__":
    init_db()
    populate_states()
    print("Database setup complete!")
