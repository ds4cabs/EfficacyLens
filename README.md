# EfficacyLens: Clinical Trial Efficacy Comparison AI Agent

## Objective
Develop an AI agent that compares key results from clinical trial publications (e.g., treatment efficacy, endpoints) and generates comparative insights for decision-makers.

## 10-Week Development Plan

### Phase 1: Data Collection & Preparation (Weeks 1-2)
- Select 20 clinical trial result sections from journal articles and ClinicalTrials.gov
- Set up data collection infrastructure using n8n automation
- Create data standardization pipeline

### Phase 2: Parsing Pipeline Development (Weeks 3-5)
- Build parsing pipeline using LangChain to extract:
  - Treatment arms
  - Response rates
  - Endpoints
  - P-values
  - Patient demographics
- Implement data validation and quality checks

### Phase 3: AI Model Development (Weeks 6-8)
- Fine-tune or prompt GPT models for structured comparative summaries
- Develop comparison algorithms for efficacy outcomes
- Create insight generation system

### Phase 4: Validation & QA (Weeks 9-10)
- Validate output against expert-written summaries
- Calculate summary agreement and factual consistency
- Generate QA metrics report

## Deliverables
1. ✅ Comparison tool for trial efficacy outcomes
2. ✅ GPT-generated comparative summary dataset  
3. ✅ QA metrics report (factual correctness, hallucination rate)

## Tech Stack
- **Development Environment**: Google Colab
- **AI Pipeline**: LangChain
- **Data Automation**: n8n
- **Workflow Design**: LangFlow (optional)
- **Version Control**: Git

## Project Structure
```
EfficacyLens/
├── data/                    # Clinical trial data
├── notebooks/               # Colab notebooks
├── src/                     # Source code
├── workflows/               # n8n and LangFlow workflows
├── models/                  # Trained models and prompts
├── validation/              # Expert summaries and QA
└── docs/                    # Documentation
```

## Getting Started
1. Set up Google Colab environment
2. Install required dependencies
3. Configure data sources
4. Run Week 1 data collection pipeline

## Dependencies
- LangChain
- OpenAI API
- pandas
- scikit-learn
- matplotlib
- requests
- beautifulsoup4
- streamlit (for UI) 