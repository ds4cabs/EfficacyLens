#!/usr/bin/env python3
"""
Demo script for EfficacyLens AI Agent.

This script demonstrates the structure and expected output format
without requiring API keys or large dependencies.
"""

import json
from pathlib import Path

def mock_agent_demo():
    """
    Demonstrate the EfficacyLens agent with mock data.
    """
    print("🔬 EfficacyLens: Clinical Trial Comparison AI Agent - DEMO")
    print("=" * 60)
    print()
    
    # Mock comparison data that would come from Gemini API
    mock_results = {
        "comparison_table": {
            "study_characteristics": {
                "Publication 1": {
                    "study_name": "MONARCH 3 Trial",
                    "drug_intervention": "Abemaciclib + Anastrozole",
                    "patient_population": "Postmenopausal women with HR+/HER2- advanced breast cancer",
                    "sample_size": "493 patients",
                    "study_phase": "Phase III",
                    "primary_endpoint": "Progression-free survival",
                    "follow_up_duration": "28.3 months"
                },
                "Publication 2": {
                    "study_name": "PALOMA-2 Trial", 
                    "drug_intervention": "Palbociclib + Letrozole",
                    "patient_population": "Postmenopausal women with ER+/HER2- advanced breast cancer",
                    "sample_size": "666 patients",
                    "study_phase": "Phase III",
                    "primary_endpoint": "Progression-free survival",
                    "follow_up_duration": "23 months"
                }
            },
            "efficacy_results": {
                "Publication 1": {
                    "primary_outcome_result": "PFS: 28.2 months vs 14.8 months",
                    "hazard_ratio": "0.54",
                    "confidence_interval": "95% CI: 0.41-0.72",
                    "p_value": "p < 0.001",
                    "response_rate": "48.2%",
                    "progression_free_survival": "28.2 months",
                    "overall_survival": "67.1 months"
                },
                "Publication 2": {
                    "primary_outcome_result": "PFS: 24.8 months vs 14.5 months", 
                    "hazard_ratio": "0.58",
                    "confidence_interval": "95% CI: 0.46-0.72",
                    "p_value": "p < 0.001",
                    "response_rate": "42.1%",
                    "progression_free_survival": "24.8 months",
                    "overall_survival": "53.9 months"
                }
            },
            "safety_profile": {
                "Publication 1": {
                    "grade_3_4_adverse_events": "54.1%",
                    "serious_adverse_events": "18.5%", 
                    "discontinuation_rate": "16.9%",
                    "most_common_aes": "Diarrhea (81.3%), Neutropenia (41.3%), Fatigue (39.9%)"
                },
                "Publication 2": {
                    "grade_3_4_adverse_events": "65.0%",
                    "serious_adverse_events": "20.1%",
                    "discontinuation_rate": "9.7%", 
                    "most_common_aes": "Neutropenia (79.5%), Fatigue (37.4%), Nausea (35.1%)"
                }
            }
        },
        "executive_summary": {
            "efficacy_comparison": "Both MONARCH 3 and PALOMA-2 demonstrated significant improvements in progression-free survival compared to endocrine therapy alone in postmenopausal women with hormone receptor-positive, HER2-negative advanced breast cancer. MONARCH 3 showed a slightly longer median PFS (28.2 vs 24.8 months) and superior overall survival (67.1 vs 53.9 months), suggesting potentially greater long-term benefit with abemaciclib plus anastrozole. The hazard ratios were comparable (0.54 vs 0.58), indicating similar relative risk reduction, but the absolute survival benefit appears more pronounced with abemaciclib.",
            
            "safety_and_recommendations": "Both regimens showed manageable safety profiles with distinct toxicity patterns. Abemaciclib showed lower rates of severe neutropenia but higher gastrointestinal toxicity, particularly diarrhea, while palbociclib was associated with more hematologic toxicity. For clinical decision-making, abemaciclib may be preferred for patients where neutropenia risk is a concern, while palbociclib might be suitable for patients who cannot tolerate gastrointestinal side effects. Patient counseling should emphasize the specific adverse event profiles, and close monitoring protocols should be tailored accordingly."
        }
    }
    
    # Display formatted results
    print("📋 STUDY CHARACTERISTICS")
    print("-" * 40)
    for pub_name, characteristics in mock_results["comparison_table"]["study_characteristics"].items():
        print(f"\n{pub_name}:")
        for key, value in characteristics.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n📊 EFFICACY RESULTS") 
    print("-" * 40)
    for pub_name, results in mock_results["comparison_table"]["efficacy_results"].items():
        print(f"\n{pub_name}:")
        for key, value in results.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n⚠️ SAFETY PROFILE")
    print("-" * 40)
    for pub_name, safety in mock_results["comparison_table"]["safety_profile"].items():
        print(f"\n{pub_name}:")
        for key, value in safety.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n💡 EXECUTIVE SUMMARY")
    print("-" * 40)
    print("\n🎯 Efficacy Comparison:")
    print(mock_results["executive_summary"]["efficacy_comparison"])
    
    print("\n⚠️ Safety Profile & Recommendations:")
    print(mock_results["executive_summary"]["safety_and_recommendations"])
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\nThis demonstrates the expected output format of EfficacyLens.")
    print("To use with real data, set up your Gemini API key and run:")
    print("  python example_usage.py")
    print("  streamlit run src/streamlit_app.py")

def show_project_structure():
    """
    Show the project structure and files created.
    """
    print("\n📁 PROJECT STRUCTURE CREATED:")
    print("-" * 40)
    
    structure = {
        "requirements.txt": "Python dependencies including Google Gemini API",
        "src/": {
            "__init__.py": "Package initialization",
            "efficacy_lens_agent.py": "Main AI agent using Gemini API",
            "pdf_processor.py": "PDF text extraction utility", 
            "streamlit_app.py": "Web interface for easy usage"
        },
        "example_usage.py": "Command-line demo script",
        ".env.example": "Template for API key configuration",
        "demo.py": "This demo script",
        "README.md": "Comprehensive documentation"
    }
    
    def print_structure(items, indent=0):
        for name, content in items.items():
            prefix = "  " * indent + "├── " if indent > 0 else ""
            if isinstance(content, dict):
                print(f"{prefix}{name}")
                print_structure(content, indent + 1)
            else:
                print(f"{prefix}{name} - {content}")
    
    print_structure(structure)

if __name__ == "__main__":
    mock_agent_demo()
    show_project_structure()
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Get Google Gemini API key: https://makersuite.google.com/app/apikey")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Set up environment: cp .env.example .env")
    print("4. Add your API key to .env file")
    print("5. Run: python example_usage.py") 