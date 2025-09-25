# Menu Item Categorization & Enrichment with LLMs

This project implements an GenAI-powered system for categorizing and enriching messy menu data using Large Language Models (LLMs). It demonstrates the power of combining rule-based systems with modern LLMs for structured data extraction.

## 📋 Features

- **Data Preparation**: Synthetic messy menu data generation with typos and abbreviations
- **Rule-based Baseline**: Keyword-based categorization system for comparison
- **LLM Integration**: Uses Ollama for intelligent menu item enrichment (with fallback to mock)
- **Evaluation Framework**: Comprehensive metrics (F1-score, JSON validity rate, accuracy)
- **Interactive UI**: Streamlit web application for easy data processing and visualization
- **Filtering & Search**: Find specific menu items by category, cuisine, or dietary attributes
- **Model Comparison**: Side-by-side comparison of baseline vs LLM performance
- **Batch Processing**: Handle multiple menu items efficiently

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or later
- Ollama installed (optional, system works with mock enricher)

### Installation
```bash
# Navigate to project directory
cd menu-enrichment

# Install dependencies
pip install -r requirements.txt

# Run the application
python run_app.py
# or directly:
streamlit run streamlit_app/app.py
```

### Launch Application
1. Open your browser and go to: http://localhost:8501
2. Upload a CSV file with menu items (must have 'raw_name' column)
3. Or use "Generate Sample Data" to see the system in action
4. Explore enriched results with filtering and comparison features

## 📁 Project Structure

```
menu-enrichment/
├── src/                    # Core application code
│   ├── schema.py          # Data schemas and validation
│   ├── baseline.py        # Rule-based classifier (keyword matching)
│   ├── llm_enricher.py    # LLM integration with Ollama
│   ├── data_generator.py  # Synthetic messy data generation
│   └── evaluation.py      # Evaluation metrics and model comparison
├── streamlit_app/         # Web interface
│   └── app.py            # Main Streamlit application
├── data/                  # Sample and generated data
│   ├── sample_upload.csv  # Example CSV for upload
│   └── sample_messy_menu.csv # Generated messy menu items
├── tests/                 # Comprehensive test suite
│   └── test_all.py       # Unit and integration tests
├── requirements.txt       # Python dependencies
├── run_app.py            # Application launcher script
├── USAGE_GUIDE.md        # Detailed usage instructions
└── README.md             # This file
```

## 🔧 Tech Stack

- **Python**: Core programming language
- **Ollama**: Local LLM for menu enrichment (llama2, mistral, etc.)
- **Pandas & NumPy**: Data manipulation and processing
- **Scikit-learn**: Evaluation metrics (F1-score, precision, recall)
- **Streamlit**: Interactive web interface
- **Plotly**: Data visualization and charts
- **Pydantic**: Data validation and schema enforcement

## 📊 Target Schema

The system transforms messy menu items into structured format:

```json
{
  "item_name": "Chicken Shawarma with Fries",
  "category": "Main Dish",
  "cuisine": "Middle Eastern",
  "attributes": ["Spicy", "Large Portion", "Halal"]
}
```

### Supported Categories
Main Dish, Appetizer, Dessert, Beverage, Side Dish, Soup, Salad, Pizza, Sandwich, Pasta, Burger

### Supported Cuisines  
American, Italian, Chinese, Mexican, Indian, Japanese, Thai, French, Mediterranean, Middle Eastern, Greek, Korean, Vietnamese, Spanish, Lebanese, Turkish

### Supported Attributes
Vegetarian, Vegan, Gluten-Free, Dairy-Free, Spicy, Mild, Large Portion, Small Portion, Halal, Kosher, Organic, Low-Carb, Keto-Friendly, Protein-Rich, Healthy, Fried, Grilled, Baked, Steamed, Raw

## 🎯 Usage Examples

### Basic Usage
```python
from src.baseline import BaselineClassifier
from src.llm_enricher import get_enricher

# Initialize models
baseline = BaselineClassifier()
llm_enricher = get_enricher()

# Classify single item
messy_item = "chkn tikka w/ rice"
baseline_result = baseline.classify_item(messy_item)
llm_result = llm_enricher.enrich_item(messy_item)

print(f"Baseline: {baseline_result.item_name} - {baseline_result.category}")
print(f"LLM: {llm_result.item_name} - {llm_result.category}")
```

### Batch Processing
```python
from src.data_generator import DataGenerator
from src.evaluation import BenchmarkRunner

# Generate test data
generator = DataGenerator()
test_data = generator.generate_messy_data(100)

# Run evaluation
benchmark = BenchmarkRunner()
results = benchmark.run_full_benchmark(test_size=100)
```

### CSV Processing
1. Prepare CSV with `raw_name` column:
```csv
raw_name,restaurant_name,price
"chkn shawarma w/ fries","Mediterranean Palace","$12.99"
"MARGHERITA PIZA","Tony's Pizza","$15.50"
```

2. Upload via Streamlit interface or process programmatically

## 📈 Performance Metrics

The system evaluates models using:

- **Accuracy**: Overall correctness across all fields
- **F1-Score**: Harmonic mean of precision and recall
- **JSON Validity Rate**: Percentage of valid structured outputs
- **Category/Cuisine Precision**: Field-specific accuracy
- **Attribute Matching**: Jaccard similarity for attribute lists

Example benchmark results:
- Baseline F1-Score: 0.900 (rule-based keyword matching)
- LLM F1-Score: Variable (depends on model and Ollama availability)
- JSON Validity: 100% (both models produce valid structured output)

## 🧪 Testing

Run the comprehensive test suite:
```bash
python tests/test_all.py
```

Tests cover:
- ✅ Schema validation and data structures
- ✅ Baseline classifier functionality
- ✅ Data generation with typos and abbreviations
- ✅ Mock LLM enricher for offline testing
- ✅ Evaluation metrics calculation
- ✅ End-to-end pipeline integration

## 📝 Sample Data

The system includes:
- **Generated samples**: 100 synthetic messy menu items with ground truth
- **Upload template**: `data/sample_upload.csv` with proper format
- **Real-world examples**: Typos, abbreviations, formatting issues

Example transformations:
- `"chkn shawarma w/ fries"` → `"Chicken Shawarma with Fries"`
- `"MARGHERITA PIZA"` → `"Margherita Pizza"`  
- `"beef burger w cheese"` → `"Beef Burger with Cheese"`

## 🔍 Model Comparison

### Rule-based Baseline
- **Strengths**: Fast, consistent, interpretable
- **Method**: Keyword matching with priority rules
- **Performance**: High precision on common patterns

### LLM Enrichment
- **Strengths**: Context understanding, handles novel items
- **Method**: Structured prompt with validation
- **Performance**: Better generalization (when Ollama available)

## 🌟 Key Achievements

1. **Complete Pipeline**: End-to-end system from messy data to structured output
2. **Dual Approach**: Combines rule-based reliability with LLM flexibility  
3. **Interactive Demo**: User-friendly web interface for exploration
4. **Comprehensive Evaluation**: Rigorous metrics and model comparison
5. **Production Ready**: Error handling, fallbacks, and extensive testing
6. **Extensible Design**: Easy to add new categories, cuisines, or models

## 🚨 Limitations & Future Work

### Current Limitations
- Mock LLM when Ollama unavailable (affects demo authenticity)
- Limited to predefined categories and cuisines
- English-language focused

### Future Enhancements
- Multi-language support
- Dynamic category learning
- Integration with real menu databases
- Advanced attribute extraction
- Confidence scoring and uncertainty quantification

## 💡 Tips for Best Results

1. **Ollama Setup**: Install Ollama with `llama2` for authentic LLM results
2. **Data Quality**: Ensure CSV has proper `raw_name` column
3. **Batch Size**: Process 50-100 items at a time for optimal performance
4. **Filtering**: Use sidebar filters to explore specific food categories
5. **Evaluation**: Run evaluation tab to compare model performance objectively

## 🤝 Contributing

This project demonstrates advanced LLM integration patterns:
- Structured output validation with Pydantic
- Fallback mechanisms for offline operation
- Comprehensive evaluation frameworks
- Interactive data exploration interfaces

For technical details, see `USAGE_GUIDE.md`.

---

**Built with ❤️ for the FoodSense GenAI Project**

*Demonstrating the power of LLMs for structured data extraction and menu intelligence.*
