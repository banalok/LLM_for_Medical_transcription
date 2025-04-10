import os
import sys
from sqlalchemy import create_engine, text, inspect
import logging

# Add the project root directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.config import EHR_DATABASE_URL
from config.logger import setup_logger

logger = setup_logger('ehr_app.data_access')

# Global variables for database connection
_engine = None
_primary_table = None
_columns = []

def connect_db(connection_string=None):
    """Connect to the database and initialize global variables.
    
    Args:
        connection_string: Database connection string. If None, uses the default from config.
    """
    global _engine, _primary_table, _columns
    
    # Use provided connection string or default
    conn_string = connection_string or EHR_DATABASE_URL
    logger.info(f"Connecting to database: {conn_string}")
    
    # Connect to the database
    _engine = create_engine(conn_string)
    
    # Get table information
    inspector = inspect(_engine)
    tables = inspector.get_table_names()
    
    if not tables:
        logger.warning("No tables found in the database")
        return False
    
    # Use the first table as primary
    _primary_table = tables[0]
    _columns = [column['name'] for column in inspector.get_columns(_primary_table)]
    logger.info(f"Connected to table: {_primary_table} with {len(_columns)} columns")
    return True

def execute_query(query, params=None, connection_string=None):
    """Execute a custom SQL query.
    
    Args:
        query: SQL query string
        params: Query parameters
        connection_string: Optional database connection string
        
    Returns:
        list: Query results as list of dictionaries
    """
    global _engine
    
    # Make sure we're connected
    if _engine is None:
        connect_db(connection_string)
    
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query), params or {})  # example: query = "SELECT * FROM my_table WHERE name = :name" and params = {"name": "alok"}, substitutes :name with "alok"
            rows = result.fetchall()
            columns = result.keys()
            
            # Convert to list of dicts
            results = [dict(zip(columns, row)) for row in rows]
            return results
            
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return []

def get_specialties():
    """Get summary of medical specialties with counts.
    
    Returns:
        list: Dictionary with specialty names and counts
    """
    if _engine is None:
        connect_db()
    
    query = f"""
        SELECT medical_specialty, COUNT(*) as count
        FROM {_primary_table}
        GROUP BY medical_specialty
        ORDER BY count DESC
    """
    
    return execute_query(query)

def search_transcriptions(search_term, limit=10):
    """Search transcriptions by content.
    
    Args:
        search_term: Term to search for
        limit: Maximum number of results to return
        
    Returns:
        list: Matching transcription records
    """
    if _engine is None:
        connect_db()
    
    query = f"""
        SELECT *
        FROM {_primary_table}
        WHERE transcription LIKE :search_term
        OR description LIKE :search_term
        OR keywords LIKE :search_term
        LIMIT :limit
    """
    
    params = {
        "search_term": f"%{search_term}%",
        "limit": limit
    }
    
    return execute_query(query, params)

def get_transcriptions_by_specialty(specialty, limit=10):
    """Get transcriptions by medical specialty.
    
    Args:
        specialty: Medical specialty to filter by
        limit: Maximum number of transcriptions to return
        
    Returns:
        list: Transcription records
    """
    if _engine is None:
        connect_db()
    
    query = f"""
        SELECT *
        FROM {_primary_table}
        WHERE medical_specialty LIKE :specialty
        LIMIT :limit
    """
    
    params = {
        "specialty": f"%{specialty}%",
        "limit": limit
    }
    
    return execute_query(query, params)

if __name__ == "__main__":
    print("Medical Transcription Database Access")
    
    # Connect to database
    success = connect_db()
    if not success:
        print("Failed to connect to database or no tables found.")
        sys.exit(1)
    
    # Get medical specialties
    specialties = get_specialties()
    print("\nTranscriptions by specialty:")
    for item in specialties:
        print(f"  - {item['medical_specialty']}: {item['count']} records")
    
    # Search for a term
    search_term = input("\nEnter a search term (or press Enter to skip): ")
    if search_term:
        results = search_transcriptions(search_term, 3)
        print(f"\nFound {len(results)} results for '{search_term}':")
        for item in results:
            print(f"  - {item['sample_name']} ({item['medical_specialty']}): {item['description'][:100]}...")