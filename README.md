
# Medical Transcription Analysis Tool

A Python repository for importing, analyzing, and exploring medical transcription data.  
This project provides tools to:

- Work with medical transcription CSV files  
- Store and query data using a SQLite database  
- **Generate clinical insights using LangChain and the OpenAI API**

It supports both structured data exploration and AI-driven text analysis of medical transcriptions.

## Project Structure

Medical_Records/
├── config/                 # Configuration files
│   ├── config.py       # Application configuration
│   └── logger.py       # Logging configuration
├── data/                   # Data storage
│   ├── raw/                # Raw data files (CSV, etc.)
│   └── processed/          # Processed data, database
├── logs/                   # Log files
├── src/                    # Source code
│   ├── data/               # Data handling
│   │   ├── import_data.py  # Data import utilities
│   │   └── data_access.py  # Database access layer
│   └── processor/          # Processing
│       └── processor.py    # LangChain implementation
└── run_tests.py            # Entry point
└── requirements.txt        # Project dependencies