import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pandas as pd
import sqlite3
from pathlib import Path
import logging
import time

from config.config import DATA_DIR, ROOT_DIR
from config.logger import setup_logger

logger = setup_logger('ehr_app.data_import')

def import_csv(csv_path, db_path=None, table_name=None, if_exists='replace'):
    """Import a CSV file into a SQLite database.
    
    Args:
        csv_path: Path to the CSV file
        db_path: Path to the SQLite database file. If None, uses the default path
        table_name: Name of the table to create. If None, uses the CSV filename
        if_exists: How to handle existing tables ('replace', 'append', 'fail')
        
    Returns:
        dict: Results of the import operation
    """
    start_time = time.time()
    logger.info(f"Starting import of CSV file: {csv_path}")
    
    # Set default database path if not provided
    if db_path is None:
        db_path = DATA_DIR / "processed" / "ehr_database.db"
        
    # Ensure the directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Validate inputs
    if not os.path.exists(csv_path):
        error_msg = f"CSV file not found: {csv_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # Determine table name if not provided
    if table_name is None:
        table_name = Path(csv_path).stem.lower().replace(" ", "_")
        logger.info(f"Using table name derived from file: {table_name}")
    
    try:
        # Read the CSV file
        logger.info("Reading CSV data...")
        df = pd.read_csv(csv_path)
        rows_count = len(df)
        cols_count = len(df.columns)
        logger.info(f"Read {rows_count} rows and {cols_count} columns from CSV")
        
        # Connect to the database
        logger.info(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # Import the data
        logger.info(f"Importing data to table '{table_name}' with if_exists='{if_exists}'")
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        
        # Verify the import
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        db_count = cursor.fetchone()[0]
        
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        # Close the connection
        conn.close()
        
        # Calculate timing
        elapsed_time = time.time() - start_time
        
        # Prepare result information
        result = {
            "status": "success",
            "table_name": table_name,
            "rows_imported": db_count,
            "columns_count": cols_count,
            "columns": [col[1] for col in columns_info],
            "elapsed_seconds": elapsed_time,
            "database_path": db_path
        }
        
        logger.info(f"Import completed successfully: {db_count} rows imported in {elapsed_time:.2f} seconds")
        return result
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}", exc_info=True)
        raise

def analyze_csv(csv_path):
    """Analyze a CSV file without importing it.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        dict: Analysis of the CSV file
    """
    logger.info(f"Analyzing CSV file: {csv_path}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Basic statistics
        row_count = len(df)
        col_count = len(df.columns)
        
        # Column analysis
        columns = []
        for col in df.columns:
            null_count = df[col].isna().sum()
            unique_count = df[col].nunique()
            
            # Determine column type
            dtype = df[col].dtype
            if pd.api.types.is_numeric_dtype(df[col]):
                col_type = "numeric"
                stats = {
                    "min": df[col].min() if null_count < row_count else None,
                    "max": df[col].max() if null_count < row_count else None,
                    "mean": df[col].mean() if null_count < row_count else None
                }
            else:
                col_type = "text"
                # Get most common values if there are any non-null values
                if null_count < row_count:
                    most_common = df[col].value_counts().head(3).to_dict()
                else:
                    most_common = {}
                    
                stats = {
                    "most_common": most_common
                }
            
            columns.append({
                "name": col,
                "type": col_type,
                "dtype": str(dtype),
                "null_count": int(null_count),
                "null_percentage": (null_count / row_count) * 100,
                "unique_count": int(unique_count),
                "stats": stats
            })
        
        # Prepare result
        result = {
            "file_path": csv_path,
            "file_size_bytes": os.path.getsize(csv_path),
            "row_count": row_count,
            "column_count": col_count,
            "columns": columns
        }
        
        logger.info(f"CSV analysis completed: {row_count} rows, {col_count} columns")
        return result
        
    except Exception as e:
        logger.error(f"Error during CSV analysis: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    
    csv_file = ROOT_DIR / "data" / "raw" / "mtsamples.csv"
    db_file = DATA_DIR / "processed" / "ehr_database.db"
    
    # Analyze the file
    print(f"Analyzing CSV file: {csv_file}")
    analysis = analyze_csv(csv_file)
    print(f"Found {analysis['row_count']} rows and {analysis['column_count']} columns")
    
    # Import to db
    print("\nImporting to database...")
    result = import_csv(csv_path=csv_file, db_path=db_file)
    
    print(f"Import complete: {result['rows_imported']} rows imported to '{result['table_name']}'")
    print(f"Database created at: {result['database_path']}")