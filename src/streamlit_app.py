import streamlit as st
import os
import sys
import tempfile
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from efficacy_lens_agent import EfficacyLensAgent

load_dotenv()

def display_structured_tables(comparison_data: dict):
    """
    Display structured comparison tables using Streamlit's native components.
    
    Args:
        comparison_data: Dictionary containing study_characteristics, efficacy_results, safety_profile
    """
    import pandas as pd
    
    # Study Characteristics
    if "study_characteristics" in comparison_data:
        st.subheader("📋 Study Characteristics")
        char_df = pd.DataFrame(comparison_data["study_characteristics"]).T
        # Clean up column names for better display
        char_df.columns = [col.replace('_', ' ').title() for col in char_df.columns]
        st.dataframe(char_df, use_container_width=True)
        st.markdown("")
    
    # Efficacy Results
    if "efficacy_results" in comparison_data:
        st.subheader("📊 Efficacy Results")
        eff_df = pd.DataFrame(comparison_data["efficacy_results"]).T
        # Clean up column names for better display
        eff_df.columns = [col.replace('_', ' ').title() for col in eff_df.columns]
        st.dataframe(eff_df, use_container_width=True)
        st.markdown("")
    
    # Safety Profile
    if "safety_profile" in comparison_data:
        st.subheader("⚠️ Safety Profile")
        safety_df = pd.DataFrame(comparison_data["safety_profile"]).T
        # Clean up column names for better display
        safety_df.columns = [col.replace('_', ' ').title() for col in safety_df.columns]
        st.dataframe(safety_df, use_container_width=True)
        st.markdown("")

def main():
    """
    Streamlit web interface for EfficacyLens AI Agent.
    """
    st.set_page_config(
        page_title="EfficacyLens: Clinical Trial Comparison AI",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 EfficacyLens: Clinical Trial Comparison AI")
    st.markdown("""
    Upload two comparable pharmaceutical publications in PDF format to get an automated comparison 
    with key results tables and analysis for decision makers.
    """)
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            value=os.getenv("GOOGLE_API_KEY", ""),
            help="Get your API key from https://makersuite.google.com/app/apikey"
        )
        
        model_name = st.selectbox(
            "Gemini Model",
            ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            index=0,
            help="Choose the Gemini model for analysis"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Gemini API key to continue.")
            st.stop()
    
    # Main interface
    st.warning("🔬 **Critical Requirement:** Both publications must study the same disease or therapeutic indication for scientifically valid comparison. Cross-disease comparisons are not supported as they produce clinically meaningless results.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Publication 1")
        pdf1 = st.file_uploader(
            "Upload first pharmaceutical publication",
            type="pdf",
            key="pdf1",
            help="Upload the first clinical trial publication for comparison"
        )
        
        if pdf1:
            st.success(f"✅ Uploaded: {pdf1.name}")
            st.info(f"File size: {pdf1.size / 1024:.1f} KB")
    
    with col2:
        st.subheader("📄 Publication 2")
        pdf2 = st.file_uploader(
            "Upload second pharmaceutical publication",
            type="pdf",
            key="pdf2",
            help="Upload the second clinical trial publication for comparison"
        )
        
        if pdf2:
            st.success(f"✅ Uploaded: {pdf2.name}")
            st.info(f"File size: {pdf2.size / 1024:.1f} KB")
    
    # Analysis button
    if pdf1 and pdf2:
        st.markdown("---")
        
        if st.button("🔍 Analyze Publications", type="primary", use_container_width=True):
            
            with st.spinner("🤖 AI is validating and analyzing the publications... This may take a few minutes."):
                try:
                    # Save uploaded files temporarily
                    with tempfile.TemporaryDirectory() as temp_dir:
                        pdf1_path = os.path.join(temp_dir, pdf1.name)
                        pdf2_path = os.path.join(temp_dir, pdf2.name)
                        
                        # Write PDFs to temporary files
                        with open(pdf1_path, "wb") as f:
                            f.write(pdf1.getvalue())
                        with open(pdf2_path, "wb") as f:
                            f.write(pdf2.getvalue())
                        
                        # Initialize the AI agent
                        agent = EfficacyLensAgent(api_key=api_key, model_name=model_name)
                        
                        # Perform comparison
                        results = agent.compare_publications(pdf1_path, pdf2_path)
                        
                        # Display results
                        display_results(results, pdf1.name, pdf2.name)
                        
                except ValueError as e:
                    # Handle validation errors specifically
                    if "Comparative Analysis Not Possible" in str(e):
                        st.error("🚫 **Publications Not Comparable**")
                        
                        # Display the error in a more user-friendly way
                        error_lines = str(e).split('\n')
                        for line in error_lines:
                            line = line.strip()
                            if line:
                                if "Publication 1:" in line or "Publication 2:" in line:
                                    st.info(line)
                                elif "Why This Matters:" in line:
                                    st.markdown("**Why This Matters:**")
                                elif "To Proceed:" in line:
                                    st.markdown("**To Proceed:**")
                                elif "Validated Sample Pairs Available:" in line:
                                    st.markdown("**Validated Sample Pairs Available:**")
                                elif line.startswith("- "):
                                    st.markdown(line)
                                elif "Cross-disease comparisons" in line:
                                    st.markdown(f"*{line}*")
                        
                        # Encourage using compatible publications
                        st.markdown("---")
                        st.success("💡 **Next Step:** Please upload publications that study the same disease or use our validated sample pairs above.")
                        
                    else:
                        st.error(f"❌ Validation error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    if "API key" in str(e).lower():
                        st.info("💡 Please check your Gemini API key in the sidebar.")
                    # st.exception(e)  # Comment out to reduce clutter in UI
    
    # Sample data section
    with st.expander("📚 Use Sample Data", expanded=False):
        st.markdown("""
        Don't have PDFs ready? Try the analysis with our sample pharmaceutical publications:
        """)
        
        sample_options = {
            "Breast Cancer Studies": ("BreastCancer1.pdf", "BreastCancer2.pdf"),
            "NSCLC Studies": ("NSCLC_1.pdf", "NSCLC_2.pdf"),
            "Migraine Studies": ("Migraine1.pdf", "Migraine2.pdf"),
            "Melanoma Studies": ("Melanoma1.pdf", "melanoma2.pdf")
        }
        
        selected_sample = st.selectbox(
            "Choose sample studies:",
            list(sample_options.keys())
        )
        
        if st.button("🔍 Analyze Sample Publications", key="sample_analysis"):
            pdf1_name, pdf2_name = sample_options[selected_sample]
            pdf1_path = f"example publications/{pdf1_name}"
            pdf2_path = f"example publications/{pdf2_name}"
            
            if os.path.exists(pdf1_path) and os.path.exists(pdf2_path):
                with st.spinner("🤖 AI is analyzing the sample publications..."):
                    try:
                        agent = EfficacyLensAgent(api_key=api_key, model_name=model_name)
                        results = agent.compare_publications(pdf1_path, pdf2_path)
                        display_results(results, pdf1_name, pdf2_name)
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
                        st.exception(e)
            else:
                st.error("❌ Sample files not found. Please upload your own PDFs.")

def display_results(results: dict, pdf1_name: str, pdf2_name: str):
    """
    Display the comparison results in the Streamlit interface.
    
    Args:
        results: Results dictionary from the AI agent
        pdf1_name: Name of first PDF
        pdf2_name: Name of second PDF
    """
    st.markdown("---")
    st.header("📊 Comparison Results")
    
    # Publication names
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Publication 1:** {pdf1_name}")
    with col2:
        st.info(f"**Publication 2:** {pdf2_name}")
    
    # Display structured tables instead of ASCII format
    if "raw_data" in results and "comparison_table" in results["raw_data"]:
        display_structured_tables(results["raw_data"]["comparison_table"])
    else:
        # Fallback to original format if raw data not available
        st.subheader("📋 Detailed Comparison Table")
        st.text(results["comparison_table"])
    
    # Executive summary
    st.subheader("💡 Executive Summary")
    
    # Investment opportunity analysis
    st.markdown("### 🎯 Investment Opportunity")
    if "investment_opportunity" in results:
        st.markdown(results["investment_opportunity"])
    else:
        st.markdown(results.get("efficacy_analysis", "Analysis not available"))
    
    # Risk assessment and strategy
    st.markdown("### ⚠️ Risk Assessment & Strategy")
    if "risk_assessment_and_strategy" in results:
        st.markdown(results["risk_assessment_and_strategy"])
    else:
        st.markdown(results.get("safety_recommendations", "Analysis not available"))
    
    # Download results
    st.markdown("---")
    st.subheader("💾 Export Results")
    
    # Format results for download
    export_content = f"""# Clinical Trial Comparison Analysis

## Publications Analyzed
- **Publication 1:** {pdf1_name}
- **Publication 2:** {pdf2_name}

## Comparison Table

{results["comparison_table"]}

## Executive Summary

### Investment Opportunity
{results.get("investment_opportunity", results.get("efficacy_analysis", "Analysis not available"))}

### Risk Assessment and Strategy
{results.get("risk_assessment_and_strategy", results.get("safety_recommendations", "Analysis not available"))}

---
Generated by EfficacyLens AI Agent
"""
    
    st.download_button(
        label="📄 Download Complete Report (Markdown)",
        data=export_content,
        file_name=f"efficacy_comparison_{pdf1_name}_{pdf2_name}.md",
        mime="text/markdown",
        use_container_width=True
    )
    
    # Show raw data with button toggle
    if st.button("🔍 View Raw Analysis Data", help="Click to show/hide raw JSON data"):
        st.json(results["raw_data"])

if __name__ == "__main__":
    main() 