import sqlite3
from contextlib import contextmanager
from typing import Optional
import os

DATABASE_PATH = "economic_data.db"


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
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


def init_db():
    """Initialize database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Table for states (reference table)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                abbreviation TEXT UNIQUE NOT NULL,
                fips_code TEXT
            )
        ''')
        
        # Table for GDP data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gdp_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL,
                source TEXT DEFAULT 'FRED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, year)
            )
        ''')
        
        # Table for Population data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS population_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL,
                source TEXT DEFAULT 'CENSUS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, year)
            )
        ''')
        
        # Table for Unemployment data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unemployment_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                period TEXT,
                value REAL,
                source TEXT DEFAULT 'BLS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, year, period)
            )
        ''')
        
        # Table for Income data (median household income)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL,
                source TEXT DEFAULT 'CENSUS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, year)
            )
        ''')
        
        # Table for Cost of Living data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cost_of_living_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL,
                source TEXT DEFAULT 'BEA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, year)
            )
        ''')
        
        # Table for Economic Growth data (GDP growth rate)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS growth_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL,
                source TEXT DEFAULT 'BEA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, year)
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gdp_state ON gdp_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_gdp_year ON gdp_data(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pop_state ON population_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pop_year ON population_data(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_unemp_state ON unemployment_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_unemp_year ON unemployment_data(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_income_state ON income_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_income_year ON income_data(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_col_state ON cost_of_living_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_col_year ON cost_of_living_data(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_growth_state ON growth_data(state)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_growth_year ON growth_data(year)')
        
        print("Database initialized successfully!")


# ============================================
# INSERT FUNCTIONS - Use these to push data
# ============================================

def insert_gdp(state: str, year: int, value: float, source: str = "FRED"):
    """Insert GDP data for a state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO gdp_data (state, year, value, source)
            VALUES (?, ?, ?, ?)
        ''', (state, year, value, source))


def insert_population(state: str, year: int, value: float, source: str = "CENSUS"):
    """Insert population data for a state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO population_data (state, year, value, source)
            VALUES (?, ?, ?, ?)
        ''', (state, year, value, source))


def insert_unemployment(state: str, year: int, value: float, period: str = "annual", source: str = "BLS"):
    """Insert unemployment data for a state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO unemployment_data (state, year, period, value, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (state, year, period, value, source))


def insert_income(state: str, year: int, value: float, source: str = "CENSUS"):
    """Insert income data for a state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO income_data (state, year, value, source)
            VALUES (?, ?, ?, ?)
        ''', (state, year, value, source))


def insert_cost_of_living(state: str, year: int, value: float, source: str = "BEA"):
    """Insert cost of living data for a state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cost_of_living_data (state, year, value, source)
            VALUES (?, ?, ?, ?)
        ''', (state, year, value, source))


def insert_growth(state: str, year: int, value: float, source: str = "BEA"):
    """Insert economic growth data for a state."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO growth_data (state, year, value, source)
            VALUES (?, ?, ?, ?)
        ''', (state, year, value, source))


# ============================================
# GET FUNCTIONS - Use these to retrieve data
# ============================================

def get_gdp(state: Optional[str] = None, year: Optional[int] = None):
    """Get GDP data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM gdp_data WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_population(state: Optional[str] = None, year: Optional[int] = None):
    """Get population data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM population_data WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_unemployment(state: Optional[str] = None, year: Optional[int] = None):
    """Get unemployment data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM unemployment_data WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_income(state: Optional[str] = None, year: Optional[int] = None):
    """Get income data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM income_data WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_cost_of_living(state: Optional[str] = None, year: Optional[int] = None):
    """Get cost of living data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM cost_of_living_data WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_growth(state: Optional[str] = None, year: Optional[int] = None):
    """Get economic growth data with optional filters."""
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM growth_data WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if year:
            query += " AND year = ?"
            params.append(year)
        query += " ORDER BY year DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


# ============================================
# BULK INSERT - For loading lots of data at once
# ============================================

def bulk_insert_gdp(data_list):
    """Insert multiple GDP records. data_list = [(state, year, value), ...]"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO gdp_data (state, year, value)
            VALUES (?, ?, ?)
        ''', data_list)
        print(f"Inserted {len(data_list)} GDP records")


def bulk_insert_population(data_list):
    """Insert multiple population records. data_list = [(state, year, value), ...]"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO population_data (state, year, value)
            VALUES (?, ?, ?)
        ''', data_list)
        print(f"Inserted {len(data_list)} population records")


def bulk_insert_unemployment(data_list):
    """Insert multiple unemployment records. data_list = [(state, year, period, value), ...]"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO unemployment_data (state, year, period, value)
            VALUES (?, ?, ?, ?)
        ''', data_list)
        print(f"Inserted {len(data_list)} unemployment records")


def bulk_insert_income(data_list):
    """Insert multiple income records. data_list = [(state, year, value), ...]"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO income_data (state, year, value)
            VALUES (?, ?, ?)
        ''', data_list)
        print(f"Inserted {len(data_list)} income records")


def bulk_insert_cost_of_living(data_list):
    """Insert multiple cost of living records. data_list = [(state, year, value), ...]"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO cost_of_living_data (state, year, value)
            VALUES (?, ?, ?)
        ''', data_list)
        print(f"Inserted {len(data_list)} cost of living records")


def bulk_insert_growth(data_list):
    #Insert multiple growth records. data_list = [(state, year, value), ...]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO growth_data (state, year, value)
            VALUES (?, ?, ?)
        ''', data_list)
        print(f"Inserted {len(data_list)} growth records")


# ============================================
# HELPER FUNCTIONS
# ============================================

def populate_states():
    #Populate the states table with US states data
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


def get_all_data_for_year(year: int):
    """Get all datasets for a specific year - useful for the dashboard"""
    return {
        "gdp": get_gdp(year=year),
        "population": get_population(year=year),
        "unemployment": get_unemployment(year=year),
        "income": get_income(year=year),
        "cost_of_living": get_cost_of_living(year=year),
        "growth": get_growth(year=year)
    }


# Run initialization when this module is executed directly
if __name__ == "__main__":
    init_db()
    populate_states()
    print("Database setup complete!")