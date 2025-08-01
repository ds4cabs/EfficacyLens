import os
import logging
from typing import Dict, List, Tuple, Optional
import google.genai as genai
import pandas as pd
from tabulate import tabulate
import json
from pdf_processor import PDFProcessor

class EfficacyLensAgent:
    """
    AI Agent for comparing pharmaceutical publications using Google Gemini API.
    
    Takes two comparable pharmaceutical publication PDFs as input and generates:
    1. A comparison table with key results
    2. Two paragraphs of analysis for decision makers like Investment Managers, Head of R&D, Market Access Directors, and Chief Medical Officers (CMOs).
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
    
    def generate_validation_prompt(self, text1: str, text2: str) -> str:
        """
        Generate a prompt for disease validation only.
        
        Args:
            text1: Text content from first publication
            text2: Text content from second publication
            
        Returns:
            Formatted validation prompt for Gemini API
        """
        prompt = f"""
You are a Medical Research Analyst specializing in clinical trial validation.

Your ONLY task is to determine if these two pharmaceutical publications study the same disease or therapeutic indication.

PUBLICATION 1:
{text1[:15000]}

PUBLICATION 2:  
{text2[:15000]}

Analyze and respond in the following JSON format:

{{
    "compatible": true/false,
    "disease_analysis": {{
        "publication1_disease": "detected disease from publication 1",
        "publication2_disease": "detected disease from publication 2",
        "compatibility_reason": "explanation of why compatible or not"
    }}
}}

VALIDATION RULES:
- Compatible = Same disease or closely related therapeutic indications
- Incompatible = Different diseases (e.g. breast cancer vs melanoma)
- When incompatible, use this message: "These publications are not comparable since they study different diseases: '[disease1]' vs '[disease2]'. Comparative analysis requires publications investigating the same disease or therapeutic indication."

Focus ONLY on disease compatibility. Do not perform any comparative analysis.
"""
        return prompt

    def generate_comparison_prompt(self, text1: str, text2: str) -> str:
        """
        Generate a comprehensive prompt for full comparative analysis (after validation passes).
        
        Args:
            text1: Text content from first publication
            text2: Text content from second publication
            
        Returns:
            Formatted prompt for Gemini API
        """
        prompt = f"""
You are a Business Analyst in the Biopharmaceutical investment field analyzing two clinical trial publications.

These publications have already been validated as studying the same disease/indication. Perform a comprehensive comparative analysis.

PUBLICATION 1:
{text1[:15000]}  # Truncate to avoid token limits

PUBLICATION 2:  
{text2[:15000]}  # Truncate to avoid token limits

Analyze and respond in the following JSON format:

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

INSTRUCTIONS:
- Perform comprehensive comparative analysis between the two publications
- Focus on investment and business implications for decision-makers
- Ensure all data is accurately extracted from the publications
- If specific data is not available, use 'Not reported' or 'N/A'
"""
        return prompt
    
    def call_validation_api(self, prompt: str) -> Dict:
        """
        Call Google Gemini API for validation only.
        
        Args:
            prompt: Formatted validation prompt
            
        Returns:
            Parsed JSON response with validation results
        """
        try:
            self.logger.info("Calling Gemini API for disease validation...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract JSON from response
            response_text = response.text
            
            # Find JSON content
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
            
            self.logger.info("Successfully parsed validation response")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing validation JSON response: {str(e)}")
            self.logger.error(f"Response text: {response_text[:500]}...")
            raise
        except Exception as e:
            self.logger.error(f"Error calling validation API: {str(e)}")
            raise
    
    def call_gemini_api(self, prompt: str) -> Dict:
        """
        Call Google Gemini API for full comparative analysis (after validation).
        
        Args:
            prompt: Formatted analysis prompt
            
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
    
    def detect_disease_indication(self, pdf_text: str) -> Dict[str, str]:
        """
        Detect the disease/indication from a publication using AI.
        
        Args:
            pdf_text: Extracted text from PDF
            
        Returns:
            Dictionary with disease, indication, and therapeutic_area
        """
        try:
            prompt = f"""
            Analyze this pharmaceutical publication text and identify the disease/indication being studied.
            
            Publication text (first 10000 characters):
            {pdf_text[:10000]}
            
            Please respond in JSON format:
            {{
                "primary_disease": "main disease being studied (e.g., 'breast cancer', 'melanoma', 'NSCLC')",
                "indication": "specific indication (e.g., 'metastatic breast cancer', 'advanced melanoma')",
                "therapeutic_area": "broad category (e.g., 'oncology', 'neurology', 'cardiology')",
                "confidence": "high/medium/low",
                "patient_population": "brief description of patient population"
            }}
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=500
                )
            )
            
            response_text = response.text
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_text = response_text[json_start:json_end]
            
            result = json.loads(json_text)
            self.logger.info(f"Detected disease: {result.get('primary_disease', 'Unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting disease: {str(e)}")
            return {
                "primary_disease": "unknown",
                "indication": "unknown", 
                "therapeutic_area": "unknown",
                "confidence": "low",
                "patient_population": "unknown"
            }
    
    def validate_publication_compatibility(self, pdf_path1: str, pdf_path2: str) -> Dict[str, any]:
        """
        Validate that two publications are comparable before analysis.
        
        Args:
            pdf_path1: Path to first PDF
            pdf_path2: Path to second PDF
            
        Returns:
            Dictionary with validation results and disease information
        """
        try:
            self.logger.info("Validating publication compatibility...")
            
            # Extract text from both PDFs
            text1, text2 = self.extract_text_from_pdfs(pdf_path1, pdf_path2)
            
            # Detect diseases from both publications
            disease1 = self.detect_disease_indication(text1)
            disease2 = self.detect_disease_indication(text2)
            
            # Check compatibility
            compatible = self._check_disease_compatibility(disease1, disease2)
            
            return {
                "compatible": compatible,
                "publication1_disease": disease1,
                "publication2_disease": disease2,
                "compatibility_reason": self._get_compatibility_reason(disease1, disease2, compatible)
            }
            
        except Exception as e:
            self.logger.error(f"Error validating compatibility: {str(e)}")
            return {
                "compatible": False,
                "error": str(e),
                "compatibility_reason": "Error occurred during validation"
            }
    
    def _check_disease_compatibility(self, disease1: Dict, disease2: Dict) -> bool:
        """
        Check if two diseases/indications are compatible for comparison.
        
        Args:
            disease1: Disease info from first publication
            disease2: Disease info from second publication
            
        Returns:
            True if compatible, False otherwise
        """
        # Normalize disease names for comparison
        disease1_normalized = disease1.get("primary_disease", "").lower().strip()
        disease2_normalized = disease2.get("primary_disease", "").lower().strip()
        
        # Check exact match
        if disease1_normalized == disease2_normalized:
            return True
        
        # Check common synonyms and related conditions
        compatibility_map = {
            "breast cancer": ["breast carcinoma", "mammary carcinoma"],
            "melanoma": ["malignant melanoma", "cutaneous melanoma"],
            "nsclc": ["non-small cell lung cancer", "lung adenocarcinoma", "lung squamous cell carcinoma"],
            "lung cancer": ["nsclc", "non-small cell lung cancer"],
            "migraine": ["headache", "chronic migraine"],
            "colorectal cancer": ["colon cancer", "rectal cancer", "crc"]
        }
        
        # Check if diseases are related
        for main_disease, synonyms in compatibility_map.items():
            if (disease1_normalized == main_disease and disease2_normalized in synonyms) or \
               (disease2_normalized == main_disease and disease1_normalized in synonyms) or \
               (disease1_normalized in synonyms and disease2_normalized in synonyms):
                return True
        
        return False
    
    def _get_compatibility_reason(self, disease1: Dict, disease2: Dict, compatible: bool) -> str:
        """
        Generate explanation for compatibility decision.
        """
        if compatible:
            return f"Both publications study {disease1.get('primary_disease', 'unknown')} - comparison is valid and clinically meaningful"
        else:
            disease1_name = disease1.get('primary_disease', 'unknown disease')
            disease2_name = disease2.get('primary_disease', 'unknown disease')
            return f"These publications are not comparable since they study different diseases: '{disease1_name}' vs '{disease2_name}'. Comparative analysis requires publications investigating the same disease or therapeutic indication."

    def compare_publications(self, pdf_path1: str, pdf_path2: str) -> Dict[str, str]:
        """
        Main method to compare two pharmaceutical publications.
        Uses mandatory two-step process: validation first, then analysis.
        
        Args:
            pdf_path1: Path to first PDF
            pdf_path2: Path to second PDF
            
        Returns:
            Dictionary containing formatted comparison table and analysis
        """
        try:
            self.logger.info(f"Starting two-step analysis of {pdf_path1} and {pdf_path2}")
            
            # STEP 1: Extract text from PDFs
            text1, text2 = self.extract_text_from_pdfs(pdf_path1, pdf_path2)
            
            # STEP 2: Mandatory Validation
            self.logger.info("Step 1: Validating disease compatibility...")
            validation_prompt = self.generate_validation_prompt(text1, text2)
            validation_result = self.call_validation_api(validation_prompt)
            
            is_compatible = validation_result.get("compatible", False)
            disease_analysis = validation_result.get("disease_analysis", {})
            
            if not is_compatible:
                # Publications are not compatible
                disease1 = disease_analysis.get("publication1_disease", "Unknown disease")
                disease2 = disease_analysis.get("publication2_disease", "Unknown disease")
                compatibility_reason = disease_analysis.get("compatibility_reason", "Publications study different diseases")
                
                raise ValueError(f"""
Comparative Analysis Not Possible: {compatibility_reason}

Publication 1: {disease1}
Publication 2: {disease2}

Why This Matters:
Cross-disease comparisons are scientifically invalid and clinically meaningless. Each disease has unique pathophysiology, patient populations, treatment endpoints, and safety profiles that prevent meaningful comparison.

To Proceed:
- Select publications studying the same disease or therapeutic indication
- Use our validated sample pairs for testing

Validated Sample Pairs Available:
- Breast Cancer Studies: BreastCancer1.pdf + BreastCancer2.pdf  
- Melanoma Studies: Melanoma1.pdf + melanoma2.pdf
- Lung Cancer Studies: NSCLC_1.pdf + NSCLC_2.pdf
- Migraine Studies: Migraine1.pdf + Migraine2.pdf
                """)
            
            self.logger.info(f"✅ Validation passed: {disease_analysis.get('compatibility_reason', 'Same disease detected')}")
            
            # STEP 3: Full Analysis (only proceeds if validation passed)
            self.logger.info("Step 2: Performing comprehensive comparative analysis...")
            analysis_prompt = self.generate_comparison_prompt(text1, text2)
            analysis_result = self.call_gemini_api(analysis_prompt)
            
            # Format results
            comparison_table = self.format_comparison_table(analysis_result["comparison_table"])
            
            # Extract analysis paragraphs
            executive_summary = analysis_result["executive_summary"]
            
            final_result = {
                "comparison_table": comparison_table,
                "investment_opportunity": executive_summary["investment_opportunity"],
                "risk_assessment_and_strategy": executive_summary["risk_assessment_and_strategy"],
                "raw_data": analysis_result
            }
            
            self.logger.info("Two-step analysis completed successfully")
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