#!/usr/bin/env python3
"""
Example usage of EfficacyLens AI Agent for comparing pharmaceutical publications.

This script demonstrates how to use the EfficacyLens agent to compare 
two clinical trial publications and generate insights for decision makers.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path for imports
sys.path.append('src')

from src.efficacy_lens_agent import EfficacyLensAgent

def main():
    """
    Example usage of the EfficacyLens AI Agent.
    """
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your Gemini API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return
    
    print("🔬 EfficacyLens: Clinical Trial Comparison AI Agent")
    print("=" * 50)
    
    # Example with sample data
    sample_comparisons = [
        {
            "name": "Breast Cancer Studies",
            "pdf1": "example publications/BreastCancer1.pdf",
            "pdf2": "example publications/BreastCancer2.pdf"
        },
        {
            "name": "NSCLC Studies", 
            "pdf1": "example publications/NSCLC_1.pdf",
            "pdf2": "example publications/NSCLC_2.pdf"
        },
        {
            "name": "Migraine Studies",
            "pdf1": "example publications/Migraine1.pdf", 
            "pdf2": "example publications/Migraine2.pdf"
        }
    ]
    
    print("\nAvailable sample comparisons:")
    for i, comparison in enumerate(sample_comparisons, 1):
        print(f"{i}. {comparison['name']}")
    
    print("\nSelect a comparison (1-3) or press Enter to use Breast Cancer studies:")
    choice = input().strip()
    
    if choice == "":
        choice = "1"
    
    try:
        selected = sample_comparisons[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice, using Breast Cancer studies.")
        selected = sample_comparisons[0]
    
    pdf1_path = selected["pdf1"]
    pdf2_path = selected["pdf2"]
    
    # Check if files exist
    if not (Path(pdf1_path).exists() and Path(pdf2_path).exists()):
        print(f"❌ Error: Sample files not found.")
        print(f"Expected: {pdf1_path} and {pdf2_path}")
        print("Please ensure the 'example publications' directory contains the sample PDFs.")
        return
    
    print(f"\n🔍 Analyzing: {selected['name']}")
    print(f"📄 Publication 1: {Path(pdf1_path).name}")
    print(f"📄 Publication 2: {Path(pdf2_path).name}")
    print("\n🤖 Starting AI analysis... This may take a few minutes.")
    
    try:
        # Initialize the AI agent
        agent = EfficacyLensAgent(api_key=api_key, model_name="gemini-2.0-flash")
        
        print("\n🔍 Validating publication compatibility...")
        
        # Perform comparison (includes validation)
        results = agent.compare_publications(pdf1_path, pdf2_path)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 COMPARISON RESULTS")
        print("=" * 80)
        
        print("\n📋 DETAILED COMPARISON TABLE")
        print("-" * 40)
        print(results["comparison_table"])
        
        print("\n💡 EXECUTIVE SUMMARY")
        print("-" * 40)
        
        print("\n🎯 Investment Opportunity:")
        print(results.get("investment_opportunity", results.get("efficacy_analysis", "Analysis not available")))
        
        print("\n⚠️ Risk Assessment & Strategy:")
        print(results.get("risk_assessment_and_strategy", results.get("safety_recommendations", "Analysis not available")))
        
        # Save results to file
        output_file = f"comparison_results_{Path(pdf1_path).stem}_{Path(pdf2_path).stem}.md"
        agent.save_results(results, output_file)
        print(f"\n💾 Results saved to: {output_file}")
        
        print("\n✅ Analysis completed successfully!")
        
    except ValueError as e:
        if "Comparative Analysis Not Possible" in str(e):
            print(f"\n🚫 {str(e)}")
            print("\n" + "="*60)
            print("❌ THESE PUBLICATIONS CANNOT BE COMPARED")
            print("="*60)
            print("Cross-disease comparisons produce scientifically invalid results.")
            print("Each disease has unique biology that prevents meaningful comparison.")
            print("\n💡 NEXT STEPS:")
            print("✅ Select publications studying the same disease or therapeutic indication")
            print("✅ Use our validated sample pairs for testing:")
            print("   - Breast Cancer: BreastCancer1.pdf + BreastCancer2.pdf")
            print("   - Melanoma: Melanoma1.pdf + melanoma2.pdf") 
            print("   - Lung Cancer: NSCLC_1.pdf + NSCLC_2.pdf")
            print("   - Migraine: Migraine1.pdf + Migraine2.pdf")
            print("\n🔬 EfficacyLens maintains scientific integrity by preventing invalid comparisons.")
        else:
            print(f"\n❌ Validation error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("Please check your API key and internet connection.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 