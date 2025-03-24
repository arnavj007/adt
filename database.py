# database.py
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Database file path
DB_FILE = 'emergency_calls.db'

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def execute_sql(sql_file):
    """Execute SQL script from file."""
    conn = create_connection()
    if conn is not None:
        try:
            with open(sql_file, 'r') as file:
                sql_script = file.read()
            
            conn.executescript(sql_script)
            conn.commit()
            print(f"SQL script executed successfully: {sql_file}")
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")

def initialize_database():
    """Initialize the database schema if it doesn't exist."""
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        execute_sql('schema.sql')
        print("Database initialized with schema.")
    else:
        print("Database already exists.")

def load_csv_to_database(csv_file):
    """Load data from CSV file to database."""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        conn = create_connection()
        if conn is not None:
            # Split data into two tables
            calls_df = df[['recordid', 'callkey', 'calldatetime', 'priority', 'district', 
                            'description', 'callnumber', 'incidentlocation', 'location', 
                            'zipcode', 'needssync', 'esri_oid']]
            
            geography_df = df[['callkey', 'neighborhood', 'policedistrict', 'policepost',
                                'councildistrict', 'sheriffdistricts', 
                                'community_statistical_areas', 'census_tracts']]
            
            # Rename columns to match schema
            calls_df.columns = ['record_id', 'call_key', 'call_date_time', 'priority', 
                                'district', 'description', 'call_number', 
                                'incident_location', 'location', 'zip_code', 
                                'needs_sync', 'esri_oid']
            
            geography_df.columns = ['call_key', 'neighborhood', 'police_district', 
                                    'police_post', 'council_district', 
                                    'sheriff_districts', 'community_statistical_areas', 
                                    'census_tracts']
            
            # Insert data
            calls_df.to_sql('calls', conn, if_exists='replace', index=False)
            geography_df.to_sql('geography', conn, if_exists='replace', index=False)
            
            print(f"Data loaded from {csv_file} into database.")
            conn.close()
    except Exception as e:
        print(f"Error loading data: {e}")

# CRUD Operations

def get_all_calls(limit=100, offset=0):
    """Get all calls with pagination."""
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT c.*, g.neighborhood, g.police_district, g.police_post, 
               g.council_district, g.sheriff_districts, g.community_statistical_areas, 
               g.census_tracts
        FROM calls c
        LEFT JOIN geography g ON c.call_key = g.call_key
        ORDER BY c.call_date_time DESC
        LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        columns = [col[0] for col in cursor.description]
        calls = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return calls
    return []

def add_call(call_data):
    """Add a new call record."""
    conn = create_connection()
    if conn is not None:
        try:
            # Insert into calls table
            calls_cursor = conn.cursor()
            calls_cursor.execute('''
            INSERT INTO calls (call_key, call_date_time, priority, district, description, 
                              call_number, incident_location, location, zip_code, 
                              needs_sync, esri_oid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                call_data['call_key'],
                call_data['call_date_time'],
                call_data['priority'],
                call_data['district'],
                call_data['description'],
                call_data['call_number'],
                call_data['incident_location'],
                call_data['location'],
                call_data['zip_code'],
                call_data.get('needs_sync', 0),
                call_data.get('esri_oid', 0)
            ))
            
            # Insert into geography table
            geo_cursor = conn.cursor()
            geo_cursor.execute('''
            INSERT INTO geography (call_key, neighborhood, police_district, police_post,
                                  council_district, sheriff_districts, 
                                  community_statistical_areas, census_tracts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                call_data['call_key'],
                call_data.get('neighborhood', ''),
                call_data.get('police_district', ''),
                call_data.get('police_post', ''),
                call_data.get('council_district', 0),
                call_data.get('sheriff_districts', ''),
                call_data.get('community_statistical_areas', ''),
                call_data.get('census_tracts', '')
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error adding new call: {e}")
            conn.close()
            return False
    return False

def update_call(call_key, call_data):
    """Update an existing call record."""
    conn = create_connection()
    if conn is not None:
        try:
            # Update calls table
            calls_cursor = conn.cursor()
            calls_cursor.execute('''
            UPDATE calls
            SET call_date_time = ?, priority = ?, district = ?, description = ?, 
                call_number = ?, incident_location = ?, location = ?, zip_code = ?, 
                needs_sync = ?, esri_oid = ?
            WHERE call_key = ?
            ''', (
                call_data['call_date_time'],
                call_data['priority'],
                call_data['district'],
                call_data['description'],
                call_data['call_number'],
                call_data['incident_location'],
                call_data['location'],
                call_data['zip_code'],
                call_data.get('needs_sync', 0),
                call_data.get('esri_oid', 0),
                call_key
            ))
            
            # Update geography table
            geo_cursor = conn.cursor()
            geo_cursor.execute('''
            UPDATE geography
            SET neighborhood = ?, police_district = ?, police_post = ?,
                council_district = ?, sheriff_districts = ?, 
                community_statistical_areas = ?, census_tracts = ?
            WHERE call_key = ?
            ''', (
                call_data.get('neighborhood', ''),
                call_data.get('police_district', ''),
                call_data.get('police_post', ''),
                call_data.get('council_district', 0),
                call_data.get('sheriff_districts', ''),
                call_data.get('community_statistical_areas', ''),
                call_data.get('census_tracts', ''),
                call_key
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error updating call: {e}")
            conn.close()
            return False
    return False

def delete_call(call_key):
    """Delete a call record."""
    conn = create_connection()
    if conn is not None:
        try:
            # Delete from geography table first (due to foreign key constraint)
            geo_cursor = conn.cursor()
            geo_cursor.execute('DELETE FROM geography WHERE call_key = ?', (call_key,))
            
            # Delete from calls table
            calls_cursor = conn.cursor()
            calls_cursor.execute('DELETE FROM calls WHERE call_key = ?', (call_key,))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting call: {e}")
            conn.close()
            return False
    return False

# Analytics queries

def get_calls_by_priority():
    """Get count of calls by priority."""
    conn = create_connection()
    if conn is not None:
        df = pd.read_sql_query("SELECT * FROM calls_by_priority", conn)
        conn.close()
        return df
    return pd.DataFrame()

def get_calls_by_district():
    """Get count of calls by district."""
    conn = create_connection()
    if conn is not None:
        df = pd.read_sql_query("SELECT * FROM calls_per_district", conn)
        conn.close()
        return df
    return pd.DataFrame()

def get_custom_query(query):
    """Execute custom SQL query."""
    conn = create_connection()
    if conn is not None:
        try:
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except sqlite3.Error as e:
            print(f"Error executing custom query: {e}")
            conn.close()
    return pd.DataFrame()
