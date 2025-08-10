# EfficacyLens: Clinical Trial Efficacy Comparison AI Agent

EfficacyLens is an AI-powered system that enables researchers to upload two comparable pharmaceutical publications and automatically generate comprehensive comparisons with actionable insights for decision-makers.

## 🌟 Features

- **Automated PDF Processing**: Extract and analyze text from pharmaceutical publication PDFs
- **AI-Powered Comparison**: Use Google Gemini API to compare clinical trial results
- **Comprehensive Analysis**: Generate detailed comparison tables with study characteristics, efficacy results, and safety profiles
- **Executive Summary**: Provide two focused paragraphs of analysis for decision makers
- **Multiple Interfaces**: Command-line tool and web interface via Streamlit
- **Export Results**: Save comparison results in Markdown format

## 🔧 Tech Stack

- **AI Engine**: Google Gemini API (gemini-2.0-flash)
- **PDF Processing**: PyPDF2
- **Web Interface**: Streamlit
- **Data Analysis**: Pandas
- **Environment Management**: python-dotenv

## 📁 Project Structure

```
EfficacyLens/
├── src/                          # Core AI engine
│   ├── __init__.py              # Package initialization
│   ├── efficacy_lens_agent.py   # Main AI agent with two-step validation
│   ├── pdf_processor.py         # PDF text extraction using PyPDF2
│   └── streamlit_app.py         # Web interface with mandatory validation
├── example publications/        # Real pharmaceutical publications (4 therapeutic areas)
│   ├── BreastCancer1.pdf        # Sample breast cancer studies
│   ├── BreastCancer2.pdf
│   ├── Melanoma1.pdf            # Sample melanoma studies  
│   ├── melanoma2.pdf
│   ├── NSCLC_1.pdf              # Sample lung cancer studies
│   ├── NSCLC_2.pdf
│   ├── Migraine1.pdf            # Sample migraine studies
│   └── Migraine2.pdf
├── models/                      # AI prompts and configurations
├── validation/                  # Validation data and QA
├── venv/                        # Virtual environment
├── requirements.txt             # Python dependencies (Google Gemini API, Streamlit, etc.)
├── example_usage.py             # Command-line interface
├── demo.py                      # Demo script (no API key required)
├── env.example                  # Environment variables template
├── .env                         # Your private API key (git-ignored)
├── .gitignore                   # Excludes sensitive files and API keys
├── comparison_results_*.md      # Generated analysis reports
└── README.md                    # Complete documentation
```

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EfficacyLens
```

### 2. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Set Up API Key

Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env
```

**Important:** Your `.env` file is automatically excluded from git via `.gitignore` to protect your API key.

### 4. Run the Project

```bash
# Command-line interface
python3 example_usage.py

# Web interface (recommended)
streamlit run src/streamlit_app.py
```

Then open your browser to `http://localhost:8501`

## 💻 Usage

### Command Line Interface

```python
from src.efficacy_lens_agent import EfficacyLensAgent

# Initialize the agent
agent = EfficacyLensAgent(api_key="your_api_key", model_name="gemini-2.0-flash")

# Compare two publications
results = agent.compare_publications("path/to/study1.pdf", "path/to/study2.pdf")

# Display results
print(results["comparison_table"])
print(results["efficacy_analysis"])
print(results["safety_recommendations"])

# Save results
agent.save_results(results, "comparison_results.md")
```

### Web Interface

```bash
streamlit run src/streamlit_app.py
```

Then open your browser to `http://localhost:8501` and:

1. Enter your Gemini API key in the sidebar
2. Upload two pharmaceutical publication PDFs
3. Click "Analyze Publications"
4. View the comprehensive comparison results
5. Download the results as a Markdown report

### Sample Data

The project includes sample pharmaceutical publications for testing:

- **Breast Cancer Studies**: BreastCancer1.pdf, BreastCancer2.pdf
- **NSCLC Studies**: NSCLC_1.pdf, NSCLC_2.pdf  
- **Migraine Studies**: Migraine1.pdf, Migraine2.pdf
- **Melanoma Studies**: Melanoma1.pdf, melanoma2.pdf

## 📊 Output Format

EfficacyLens generates structured comparisons with:

### Comparison Tables

1. **Study Characteristics**
   - Study name, drug intervention, patient population
   - Sample size, study phase, primary endpoint
   - Follow-up duration

2. **Efficacy Results**
   - Primary outcome results, hazard ratios
   - Confidence intervals, p-values
   - Response rates, survival metrics

3. **Safety Profile**
   - Grade 3-4 adverse events
   - Serious adverse events, discontinuation rates
   - Most common adverse events

### Executive Summary

1. **Efficacy Comparison**: Paragraph comparing efficacy results, highlighting key differences and clinical relevance
2. **Safety & Recommendations**: Paragraph analyzing safety profiles with clear recommendations for decision makers

## 🔧 Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for advanced users)
GEMINI_MODEL=gemini-2.0-flash  # Default model
LOG_LEVEL=INFO                 # Logging level
```

**Security Note:** Never commit your `.env` file to git. It's automatically excluded via `.gitignore`.

### Model Options

- `gemini-2.0-flash`: Fast, cost-effective (recommended)
- `gemini-1.5-pro`: More comprehensive analysis
- `gemini-1.5-flash`: Balanced speed and quality

## 📝 API Documentation

### EfficacyLensAgent Class

```python
class EfficacyLensAgent:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash")
    def compare_publications(self, pdf_path1: str, pdf_path2: str) -> Dict[str, str]
    def save_results(self, results: Dict[str, str], output_path: str) -> None
```

### Key Methods

#### `compare_publications(pdf_path1, pdf_path2)`

**Parameters:**
- `pdf_path1` (str): Path to first PDF file
- `pdf_path2` (str): Path to second PDF file

**Returns:**
- Dictionary with keys:
  - `comparison_table`: Formatted comparison tables
  - `efficacy_analysis`: Efficacy comparison paragraph
  - `safety_recommendations`: Safety analysis paragraph
  - `raw_data`: Complete structured data from AI

#### `save_results(results, output_path)`

**Parameters:**
- `results` (dict): Results from compare_publications
- `output_path` (str): Path to save Markdown report

## 🚀 Advanced Usage

### Custom Prompts

Modify the comparison prompt in `src/efficacy_lens_agent.py`:

```python
def generate_comparison_prompt(self, text1: str, text2: str) -> str:
    # Customize the prompt for specific therapeutic areas
    # or analysis requirements
```

### Error Handling

```python
try:
    results = agent.compare_publications(pdf1, pdf2)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Handle specific error cases
```

### Batch Processing

```python
# Process multiple comparisons
comparisons = [
    ("study1.pdf", "study2.pdf"),
    ("study3.pdf", "study4.pdf"),
]

for pdf1, pdf2 in comparisons:
    results = agent.compare_publications(pdf1, pdf2)
    agent.save_results(results, f"comparison_{pdf1}_{pdf2}.md")
```

## 🛠️ Development

### Testing

```bash
# Test with sample data
python example_usage.py

# Run web interface
streamlit run src/streamlit_app.py
```

---

**Built with ❤️ by DorisTheChef for pharmaceutical research and evidence-based medicine.**
