# Menu Item Categorization & Enrichment with LLMs - Usage Guide

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11 or later
- Ollama installed (optional, system works with mock enricher)

### Installation

1. **Clone/Download the project**
```bash
cd "c:\Users\mzaye\OneDrive\Documents\Projects\Uber_GenAI\menu-enrichment"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python run_app.py
# or
streamlit run streamlit_app/app.py
```

4. **Open your browser**
Navigate to: http://localhost:8501

## 📊 Using the Application

### Tab 1: Data Processing
1. **Upload CSV**: Click "Choose a CSV file" and select a file with menu items
   - Required column: `raw_name` (containing messy menu item names)
   - Optional columns: `restaurant_name`, `price`

2. **Quick Actions**: 
   - "Generate Sample Data": Creates synthetic messy menu data
   - "Clear Results": Removes previous results

3. **View Results**: Choose from different view modes:
   - Before/After Comparison
   - LLM Only
   - Baseline Only 
   - Side by Side

4. **Filtering**: Use the sidebar to filter by:
   - Categories (Main Dish, Pizza, Appetizer, etc.)
   - Cuisines (Italian, Chinese, American, etc.)
   - Attributes (Vegetarian, Spicy, Gluten-Free, etc.)

5. **Download**: Click "Download Results" to save enriched data as CSV

### Tab 2: Model Comparison
- View success rates for both models
- Compare category and cuisine distributions
- Interactive charts showing model differences

### Tab 3: Evaluation
- Run comprehensive evaluation with custom dataset size
- View detailed performance metrics (F1-score, accuracy, etc.)
- Performance visualization charts

### Tab 4: Sample Data
- Generate test datasets of various sizes
- Preview generated data with ground truth
- Download sample data for testing

### Tab 5: About
- Project overview and documentation
- Feature descriptions and tips

## 🔧 Configuration Options

### Sidebar Settings
- **Model Settings**: Toggle LLM enricher on/off
- **Data Generation**: Adjust sample data size (10-200 items)
- **Filters**: Select specific categories, cuisines, or attributes to display

## 📁 File Structure

```
menu-enrichment/
├── src/                    # Core application code
│   ├── schema.py          # Data schemas and validation
│   ├── baseline.py        # Rule-based classifier
│   ├── llm_enricher.py    # LLM integration with Ollama
│   ├── data_generator.py  # Synthetic data generation
│   └── evaluation.py      # Evaluation metrics and comparison
├── streamlit_app/         # Web interface
│   └── app.py            # Main Streamlit application
├── data/                  # Sample and generated data
│   ├── sample_upload.csv  # Example upload file
│   └── sample_messy_menu.csv # Generated sample data
├── tests/                 # Unit tests
│   └── test_all.py       # Comprehensive test suite
├── requirements.txt       # Python dependencies
├── run_app.py            # Application launcher script
└── README.md             # Project documentation
```

## 🧪 Testing

Run the test suite:
```bash
python tests/test_all.py
```

Tests cover:
- Schema validation
- Baseline classifier functionality
- Data generation and cleaning
- Mock LLM enricher
- Evaluation metrics
- End-to-end pipeline

## 📤 Sample Data Format

### Input CSV Format
```csv
raw_name,restaurant_name,price
"chkn shawarma w/ fries","Mediterranean Palace","$12.99"
"MARGHERITA PIZA","Tony's Pizza","$15.50"
"beef burger w cheese","Burger Joint","$11.99"
```

### Output Format
```csv
raw_name,llm_name,llm_category,llm_cuisine,llm_attributes,baseline_name,baseline_category,baseline_cuisine,baseline_attributes
"chkn shawarma w/ fries","Chicken Shawarma With Fries","Main Dish","Middle Eastern","Spicy|Halal","Chicken Shawarma With Fries","Main Dish","Middle Eastern","Spicy"
```

## 🎯 Expected Results Schema

```json
{
  "item_name": "Chicken Shawarma with Fries",
  "category": "Main Dish",
  "cuisine": "Middle Eastern", 
  "attributes": ["Spicy", "Large Portion", "Halal"]
}
```

### Available Categories
Main Dish, Appetizer, Dessert, Beverage, Side Dish, Soup, Salad, Pizza, Sandwich, Pasta, Burger

### Available Cuisines  
American, Italian, Chinese, Mexican, Indian, Japanese, Thai, French, Mediterranean, Middle Eastern, Greek, Korean, Vietnamese, Spanish, Lebanese, Turkish

### Available Attributes
Vegetarian, Vegan, Gluten-Free, Dairy-Free, Spicy, Mild, Large Portion, Small Portion, Halal, Kosher, Organic, Low-Carb, Keto-Friendly, Protein-Rich, Healthy, Fried, Grilled, Baked, Steamed, Raw

## 🔍 Tips for Best Results

1. **Data Quality**: Ensure your CSV has a `raw_name` column with menu item names

2. **Ollama Setup**: For best LLM results, install Ollama with llama2 or mistral model:
   ```bash
   ollama pull llama2
   ollama serve
   ```

3. **Filtering**: Use sidebar filters to focus on specific types of menu items

4. **Batch Processing**: For large datasets, process in smaller batches (50-100 items)

5. **Evaluation**: Use the evaluation tab to compare model performance objectively

6. **Sample Data**: Use the sample data generator to explore system capabilities

## ❗ Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you're in the project directory
   - Verify Python environment is activated
   - Install all requirements: `pip install -r requirements.txt`

2. **Ollama connection errors**
   - System automatically uses mock enricher if Ollama unavailable
   - For real LLM results, ensure Ollama is running: `ollama serve`

3. **CSV upload issues**
   - Ensure CSV has `raw_name` column
   - Check file encoding (UTF-8 recommended)
   - Verify CSV format is valid

4. **Performance issues**
   - Reduce dataset size for evaluation
   - Use filters to limit displayed results
   - Process data in smaller batches

### Getting Help

- Check the "About" tab in the application for detailed information
- Run tests to verify system functionality: `python tests/test_all.py`
- Review the README.md for technical details

## 🚀 Advanced Usage

### Custom Model Integration
To integrate additional LLM models, modify `src/llm_enricher.py`:
1. Add model configuration to `LLMConfig`
2. Update `OllamaClient` with new model endpoints
3. Adjust prompts for optimal model performance

### Custom Categories/Cuisines
Modify `src/schema.py` to add new categories, cuisines, or attributes:
1. Update the respective lists in `MenuSchema` class
2. Update baseline rules in `src/baseline.py`
3. Retrain or adjust LLM prompts accordingly

### Evaluation Metrics
Add custom metrics in `src/evaluation.py`:
1. Implement new metric functions
2. Update `EvaluationResult` dataclass
3. Modify evaluation reports and visualizations