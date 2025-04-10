import os
import sys
from pathlib import Path

# Add the project root directory to the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import modules
from config.config import ROOT_DIR, DATA_DIR
from src.data.import_data import analyze_csv, import_csv
from src.data.data_access import connect_db, get_specialties, search_transcriptions
from src.processor.processor import initialize_llm, analyze_transcription

def divider(title):
    """Print a divider with title."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def run_import():
    
    divider("DATA IMPORT")    
   
    csv_file = ROOT_DIR / "data" / "raw" / "mtsamples.csv"
    db_file = DATA_DIR / "processed" / "ehr_database.db"
    
    # Analyze the file
    print(f"Analyzing CSV file: {csv_file}")
    analysis = analyze_csv(csv_file)
    print(f"Found {analysis['row_count']} rows and {analysis['column_count']} columns")
    
    # Import too db
    print("\nImporting to database...")
    result = import_csv(csv_path=csv_file, db_path=db_file)
    
    print(f"Import complete: {result['rows_imported']} rows imported to '{result['table_name']}'")
    print(f"Database created at: {result['database_path']}")

def run_data_access():
    """Run data_access.py"""
    divider("DATA ACCESS")
    
    # Connect to db
    print("Connecting to database...")
    success = connect_db()
    if not success:
        print("Failed to connect to database or no tables found.")
        return False
    
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
    
    return True

def run_processor():
    """Run processor.py."""
    divider("PROCESSOR")
    
    print("Medical Transcription Analyzer")
    
    # Initialize the model
    try:
        initialize_llm()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please set your OpenAI API key in the environment variables.")
        return False
    
    # Sample transcription for testing
    sample = {
        "medical_specialty": "Cardiovascular / Pulmonary",
        "transcription": """
        2-D M-MODE:
        1. Left atrial enlargement with left atrial diameter of 4.7 cm.
        2. Normal size right and left ventricle.
        3. Normal LV systolic function with left ventricular ejection fraction of 51%.
        4. Normal LV diastolic function.
        5. No pericardial effusion.
        6. Normal morphology of aortic valve, mitral valve, tricuspid valve, and pulmonary valve.
        7. PA systolic pressure is 36 mmHg.
        DOPPLER:
        1. Mild mitral and tricuspid regurgitation.
        2. Trace aortic and pulmonary regurgitation.
        """
    }
    
    # Analyze the sample
    try:
        print("\nAnalyzing...")
        insight = analyze_transcription(sample)
        
        # Check if insight is a string (raw response) or object with attributes
        if isinstance(insight, str):
            print("\nANALYSIS RESULTS:")
            print(insight)
        else:
            # Process as structured object
            print("\nANALYSIS RESULTS:")
            print(f"\nSummary: {insight.summary}")
            
            print("\nKey Findings:")
            for finding in insight.key_findings:
                print(f"- {finding}")
            
            print("\nMedical Terms:")
            for term in insight.medical_terms:
                print(f"- {term}")
            
            print("\nRecommendations:")
            for rec in insight.recommendations:
                print(f"- {rec}")
            
            print(f"\nSpecialty Context: {insight.specialty_context}")
        
        return True
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return False

def main():
    """Run all in sequence."""
    print("Starting Medical Transcription Analysis")
    
    # Step 1: Import Data
    run_import()
    
    # Step 2: Data Access
    data_access_success = run_data_access()
    
    # Step 3: If previous steps are done, run processor
    if data_access_success:
        processor_success = run_processor()
    
    print("\nCompleted!")

if __name__ == "__main__":
    main()