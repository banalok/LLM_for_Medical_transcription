import os
import sys
import time
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Add the project root directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.config import OPENAI_API_KEY, DEFAULT_MODEL, MODEL_TEMPERATURE
from config.logger import setup_logger

logger = setup_logger('ehr_app.ai_processor')

# Define structured output for clinical insights
class ClinicalInsight(BaseModel):
    """Structured output for clinical insights."""
    summary: str = Field(description="Brief summary of the medical transcription")
    key_findings: List[str] = Field(description="Key medical findings from the transcription")
    medical_terms: List[str] = Field(description="Important medical terminology used")
    recommendations: List[str] = Field(description="Any recommendations or follow-up actions mentioned")
    specialty_context: str = Field(description="How this fits into the medical specialty context")

# Global variables for LLM and chain
_llm = None
_chain = None

def initialize_llm(api_key=None, model_name=None, temperature=None):
    """Initialize the language model and processing chain.
    
    Args:
        api_key: OpenAI API key
        model_name: Name of the LLM to use
        temperature: Model temperature setting
    """
    global _llm, _chain
    
    # Use provided values or defaults from config
    api_key = api_key or OPENAI_API_KEY
    model_name = model_name or DEFAULT_MODEL
    temp = temperature if temperature is not None else MODEL_TEMPERATURE
    
    if not api_key:
        logger.error("No OpenAI API key provided")
        raise ValueError("OpenAI API key is required")
    
    # Initialize the language model
    _llm = ChatOpenAI(
        model=model_name,
        temperature=temp,
        api_key=api_key
    )
    
    # Set up the output parser
    parser = PydanticOutputParser(pydantic_object=ClinicalInsight)
    
    # Create the analysis prompt
    prompt = PromptTemplate(
        template="""
        You are an AI assistant for healthcare professionals. Analyze the following medical transcription and provide insights.
        
        MEDICAL SPECIALTY: {specialty}
        
        TRANSCRIPTION:
        {transcription}
        
        {format_instructions}
        """,
        input_variables=["specialty", "transcription"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Create the chain
    _chain = LLMChain(
        llm=_llm,
        prompt=prompt,
        output_key="clinical_insight"
    )
    
    logger.info(f"LLM initialized with model: {model_name}, temperature: {temp}")
    return True

def analyze_transcription(transcription_data: Dict[str, Any]) -> ClinicalInsight:
    """Analyze a medical transcription to generate clinical insights.
    
    Args:
        transcription_data: Dictionary containing transcription data
        
    Returns:
        ClinicalInsight: Generated clinical insights
    """
    # Make sure LLM is initialized
    if _llm is None or _chain is None:
        initialize_llm()
    
    start_time = time.time()
    logger.info("Analyzing medical transcription")
    
    try:
        # Extract data from the transcription
        specialty = transcription_data.get('medical_specialty', 'Unknown')
        transcription_text = transcription_data.get('transcription', '')
        
        if not transcription_text:
            logger.error("Empty transcription text")
            raise ValueError("Transcription text is empty")
        
        # Generate insights
        result = _chain.invoke({
            "specialty": specialty,
            "transcription": transcription_text
        })
        parser = PydanticOutputParser(pydantic_object=ClinicalInsight)
        raw_output = result["clinical_insight"]
        # Parse result
        clinical_insight = parser.parse(raw_output)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Transcription analyzed in {elapsed_time:.2f} seconds")
        
        return clinical_insight
        
    except Exception as e:
        logger.error(f"Error analyzing transcription: {str(e)}")
        raise

if __name__ == "__main__":
    print("Medical Transcription Analyzer")
    
    # Initialize the model
    try:
        initialize_llm()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please set your OpenAI API key in the environment variables.")
        sys.exit(1)
    
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
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")