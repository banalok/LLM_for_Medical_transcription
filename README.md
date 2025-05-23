
# Medical Transcription Analysis Tool

A Python repository for importing, analyzing, and exploring medical transcription data.  
This project provides tools to:

- Work with medical transcription CSV files  
- Store and query data using a SQLite database  
- **Generate clinical insights using LangChain and the OpenAI API**

It supports both structured data exploration and AI-driven text analysis of medical transcriptions.

[Dataset](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions?resource=download)

## Project Structure
```
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
└── run.py            # Entry point
└── requirements.txt        # Project dependencies
```

![Data Import Module Output](images/data_import.PNG)
![Data Access Module Output](images/data_access.PNG)
![LangChain Implementation Output](images/LangChain.PNG)

Run "run.py" after installation of the required dependencies using 
```bash
pip install -r requirements.txt
```
**.env** file should be created that looks like:
```bash
EHR_DATABASE_URL=sqlite:///path_to_ehr_database.db
OPENAI_API_KEY=your_api_key
```
