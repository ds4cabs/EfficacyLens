import os
import logging
from typing import Dict, List, Tuple, Optional
from google import genai
import pandas as pd
from tabulate import tabulate
import json
from pdf_processor import PDFProcessor

class EfficacyLensAgent:
    """
    AI Agent for comparing pharmaceutical publications using Google Gemini API.
    
    Takes two comparable pharmaceutical publication PDFs as input and generates:
    1. A comparison table with key results
    2. Two paragraphs of analysis for decision makers
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the EfficacyLens Agent.
        
        Args:
            api_key: Google Gemini API key
            model_name: Gemini model to use (default: gemini-1.5-pro)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.pdf_processor = PDFProcessor()
        
        # Configure Gemini API
        self.client = genai.Client(api_key=api_key)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def extract_text_from_pdfs(self, pdf_path1: str, pdf_path2: str) -> Tuple[str, str]:
        """
        Extract text content from two PDF files.
        
        Args:
            pdf_path1: Path to first PDF
            pdf_path2: Path to second PDF
            
        Returns:
            Tuple of extracted text from both PDFs
        """
        try:
            text1 = self.pdf_processor.extract_text(pdf_path1)
            text2 = self.pdf_processor.extract_text(pdf_path2)
            
            self.logger.info(f"Extracted {len(text1)} characters from {pdf_path1}")
            self.logger.info(f"Extracted {len(text2)} characters from {pdf_path2}")
            
            return text1, text2
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def generate_comparison_prompt(self, text1: str, text2: str) -> str:
        """
        Generate a comprehensive prompt for Gemini API to compare two pharmaceutical publications.
        
        Args:
            text1: Text content from first publication
            text2: Text content from second publication
            
        Returns:
            Formatted prompt for Gemini API
        """
        prompt = f"""
You are a Business Analyst in the Biopharmaceutical investment field analyzing two clinical trial publications. 
Your task is to compare these studies and generate strategic investment insights for senior decision makers including Investment Managers, Head of R&D, Market Access Directors, and Chief Medical Officers (CMOs).

PUBLICATION 1:
{text1[:15000]}  # Truncate to avoid token limits

PUBLICATION 2:  
{text2[:15000]}  # Truncate to avoid token limits

Please provide your analysis in the following JSON format:

{{
    "comparison_table": {{
        "study_characteristics": {{
            "Publication 1": {{
                "study_name": "",
                "drug_intervention": "",
                "patient_population": "",
                "sample_size": "",
                "study_phase": "",
                "primary_endpoint": "",
                "follow_up_duration": "",
                "market_size_potential": "",
                "competitive_landscape": ""
            }},
            "Publication 2": {{
                "study_name": "",
                "drug_intervention": "",
                "patient_population": "",
                "sample_size": "",
                "study_phase": "",
                "primary_endpoint": "",
                "follow_up_duration": "",
                "market_size_potential": "",
                "competitive_landscape": ""
            }}
        }},
        "efficacy_results": {{
            "Publication 1": {{
                "primary_outcome_result": "",
                "hazard_ratio": "",
                "confidence_interval": "",
                "p_value": "",
                "response_rate": "",
                "progression_free_survival": "",
                "overall_survival": "",
                "clinical_significance": "",
                "regulatory_implications": ""
            }},
            "Publication 2": {{
                "primary_outcome_result": "",
                "hazard_ratio": "",
                "confidence_interval": "",
                "p_value": "",
                "response_rate": "",
                "progression_free_survival": "",
                "overall_survival": "",
                "clinical_significance": "",
                "regulatory_implications": ""
            }}
        }},
        "safety_profile": {{
            "Publication 1": {{
                "grade_3_4_adverse_events": "",
                "serious_adverse_events": "",
                "discontinuation_rate": "",
                "most_common_aes": "",
                "safety_differentiation": "",
                "market_access_implications": ""
            }},
            "Publication 2": {{
                "grade_3_4_adverse_events": "",
                "serious_adverse_events": "",
                "discontinuation_rate": "",
                "most_common_aes": "",
                "safety_differentiation": "",
                "market_access_implications": ""
            }}
        }}
    }},
    "executive_summary": {{
        "investment_opportunity": "A strategic paragraph analyzing the investment potential of each study, highlighting competitive advantages, market differentiation, revenue potential, and key value drivers for Investment Managers and business stakeholders.",
        "risk_assessment_and_strategy": "A comprehensive paragraph analyzing safety profiles, regulatory risks, market access challenges, and strategic recommendations for portfolio management. Include considerations for Head of R&D (development strategy), Market Access Directors (payer perspectives), and CMOs (clinical implementation)."
    }}
}}

Ensure all data is accurately extracted from the publications. If specific data is not available, use 'Not reported' or 'N/A'.
"""
        return prompt
    
    def call_gemini_api(self, prompt: str) -> Dict:
        """
        Call Google Gemini API with the comparison prompt.
        
        Args:
            prompt: Formatted prompt for analysis
            
        Returns:
            Parsed JSON response from Gemini
        """
        try:
            self.logger.info("Calling Gemini API for comparison analysis...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract JSON from response
            response_text = response.text
            
            # Find JSON content between ```json and ``` markers
            start_marker = "```json"
            end_marker = "```"
            
            start_idx = response_text.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = response_text.find(end_marker, start_idx)
                if end_idx != -1:
                    json_text = response_text[start_idx:end_idx].strip()
                else:
                    json_text = response_text[start_idx:].strip()
            else:
                # Try to find JSON structure directly
                json_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(json_text)
            
            self.logger.info("Successfully parsed Gemini API response")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON response: {str(e)}")
            self.logger.error(f"Response text: {response_text[:500]}...")
            raise
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def format_comparison_table(self, comparison_data: Dict) -> str:
        """
        Format the comparison data into a readable table.
        
        Args:
            comparison_data: Parsed comparison data from Gemini
            
        Returns:
            Formatted table as string
        """
        try:
            tables = []
            
            # Study Characteristics Table
            if "study_characteristics" in comparison_data:
                char_df = pd.DataFrame(comparison_data["study_characteristics"]).T
                tables.append("## Study Characteristics")
                tables.append(tabulate(char_df, headers=list(char_df.columns), tablefmt="grid"))
                tables.append("")
            
            # Efficacy Results Table
            if "efficacy_results" in comparison_data:
                eff_df = pd.DataFrame(comparison_data["efficacy_results"]).T
                tables.append("## Efficacy Results")
                tables.append(tabulate(eff_df, headers=list(eff_df.columns), tablefmt="grid"))
                tables.append("")
            
            # Safety Profile Table
            if "safety_profile" in comparison_data:
                safety_df = pd.DataFrame(comparison_data["safety_profile"]).T
                tables.append("## Safety Profile")
                tables.append(tabulate(safety_df, headers=list(safety_df.columns), tablefmt="grid"))
                tables.append("")
            
            return "\n".join(tables)
            
        except Exception as e:
            self.logger.error(f"Error formatting comparison table: {str(e)}")
            raise
    
    def compare_publications(self, pdf_path1: str, pdf_path2: str) -> Dict[str, str]:
        """
        Main method to compare two pharmaceutical publications.
        
        Args:
            pdf_path1: Path to first PDF
            pdf_path2: Path to second PDF
            
        Returns:
            Dictionary containing formatted comparison table and analysis
        """
        try:
            self.logger.info(f"Starting comparison of {pdf_path1} and {pdf_path2}")
            
            # Extract text from PDFs
            text1, text2 = self.extract_text_from_pdfs(pdf_path1, pdf_path2)
            
            # Generate prompt
            prompt = self.generate_comparison_prompt(text1, text2)
            
            # Call Gemini API
            result = self.call_gemini_api(prompt)
            
            # Format results
            comparison_table = self.format_comparison_table(result["comparison_table"])
            
            # Extract analysis paragraphs
            executive_summary = result["executive_summary"]
            
            final_result = {
                "comparison_table": comparison_table,
                            "investment_opportunity": executive_summary["investment_opportunity"],
            "risk_assessment_and_strategy": executive_summary["risk_assessment_and_strategy"],
                "raw_data": result
            }
            
            self.logger.info("Comparison completed successfully")
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error in compare_publications: {str(e)}")
            raise
    
    def save_results(self, results: Dict[str, str], output_path: str) -> None:
        """
        Save comparison results to file.
        
        Args:
            results: Results from compare_publications
            output_path: Path to save results
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# Clinical Trial Comparison Analysis\n\n")
                f.write("## Comparison Table\n\n")
                f.write(results["comparison_table"])
                f.write("\n\n## Executive Summary\n\n")
                f.write("### Investment Opportunity\n")
                f.write(results.get("investment_opportunity", results.get("efficacy_analysis", "Analysis not available")))
                f.write("\n\n### Risk Assessment and Strategy\n")
                f.write(results.get("risk_assessment_and_strategy", results.get("safety_recommendations", "Analysis not available")))
                
            self.logger.info(f"Results saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            raise 