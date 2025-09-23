import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from typing import List, Dict, Any, Optional
import io
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')

# Add directories to Python path
sys.path.insert(0, parent_dir)
sys.path.insert(0, src_dir)

# Change to parent directory to ensure relative imports work
os.chdir(parent_dir)

from src.schema import MenuItem, MenuSchema
from src.baseline import BaselineClassifier
from src.llm_enricher import get_enricher
from src.data_generator import DataGenerator
from src.evaluation import MenuItemEvaluator, BenchmarkRunner
from src.order_processor import OrderProcessor


class MenuEnrichmentApp:
    """Streamlit application for menu item enrichment"""
    
    def __init__(self):
        self.schema = MenuSchema()
        self.baseline_classifier = BaselineClassifier()
        self.llm_enricher = get_enricher()
        self.evaluator = MenuItemEvaluator()
        self.data_generator = DataGenerator()
        self.order_processor = OrderProcessor(use_llm=False)  # Disable LLM by default
    
    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title="Menu Item Enrichment with LLMs",
            page_icon="🍽️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header
        st.title("🍽️ Menu Item Categorization & Enrichment with LLMs")
        st.markdown("Upload messy menu data and see it transformed with AI-powered enrichment")
        
        # Sidebar
        self.setup_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Data Processing", 
            "🔍 Model Comparison", 
            "📈 Evaluation", 
            "� Text-to-Order",
            "�🔬 Sample Data",
            "ℹ️ About"
        ])
        
        with tab1:
            self.data_processing_tab()
        
        with tab2:
            self.model_comparison_tab()
        
        with tab3:
            self.evaluation_tab()
        
        with tab4:
            self.text_to_order_tab()
        
        with tab5:
            self.sample_data_tab()
        
        with tab6:
            self.about_tab()
    
    def setup_sidebar(self):
        """Setup sidebar with configuration options"""
        st.sidebar.header("⚙️ Configuration")
        
        # Model selection
        st.sidebar.subheader("Model Settings")
        use_llm = st.sidebar.checkbox("Use LLM Enricher", value=True, 
                                     help="Use LLM for enrichment (falls back to mock if Ollama unavailable)")
        
        if use_llm:
            st.sidebar.info("🤖 LLM enricher enabled")
        else:
            st.sidebar.info("📝 Using baseline classifier only")
        
        # Store settings in session state
        st.session_state['use_llm'] = use_llm
        
        # Dataset size for generation
        st.sidebar.subheader("Data Generation")
        sample_size = st.sidebar.slider("Sample Data Size", 10, 200, 50)
        st.session_state['sample_size'] = sample_size
        
        # Filters
        st.sidebar.subheader("Filters")
        selected_categories = st.sidebar.multiselect(
            "Filter by Category", 
            options=self.schema.CATEGORIES,
            default=[]
        )
        st.session_state['selected_categories'] = selected_categories
        
        selected_cuisines = st.sidebar.multiselect(
            "Filter by Cuisine",
            options=self.schema.CUISINES,
            default=[]
        )
        st.session_state['selected_cuisines'] = selected_cuisines
        
        selected_attributes = st.sidebar.multiselect(
            "Filter by Attributes",
            options=self.schema.ATTRIBUTES,
            default=[]
        )
        st.session_state['selected_attributes'] = selected_attributes
    
    def data_processing_tab(self):
        """Main data processing interface"""
        st.header("📊 Data Processing & Enrichment")
        
        # Upload section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Upload Menu Data")
            uploaded_file = st.file_uploader(
                "Choose a CSV file with menu items",
                type=['csv'],
                help="CSV should have a 'raw_name' column with menu item names"
            )
        
        with col2:
            st.subheader("Quick Actions")
            if st.button("Generate Sample Data"):
                self.generate_sample_data()
            
            if st.button("Clear Results"):
                if 'enriched_data' in st.session_state:
                    del st.session_state['enriched_data']
                st.success("Results cleared!")
        
        # Process uploaded file
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if 'raw_name' not in df.columns:
                    st.error("CSV must contain a 'raw_name' column")
                    return
                
                st.success(f"Loaded {len(df)} menu items")
                self.process_menu_data(df)
                
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
        
        # Display results
        if 'enriched_data' in st.session_state:
            self.display_enrichment_results()
    
    def process_menu_data(self, df: pd.DataFrame):
        """Process menu data with enrichment"""
        with st.spinner("Enriching menu items..."):
            raw_names = df['raw_name'].tolist()
            
            # Get enrichments
            if st.session_state.get('use_llm', True):
                llm_results = self.llm_enricher.enrich_batch(raw_names, show_progress=False)
            else:
                llm_results = [None] * len(raw_names)
            
            baseline_results = self.baseline_classifier.batch_classify(raw_names)
            
            # Combine results
            enriched_data = []
            for i, raw_name in enumerate(raw_names):
                row = {
                    'raw_name': raw_name,
                    'llm_enriched': llm_results[i] if llm_results[i] else None,
                    'baseline_enriched': baseline_results[i]
                }
                enriched_data.append(row)
            
            st.session_state['enriched_data'] = enriched_data
            st.success(f"Enriched {len(enriched_data)} menu items!")
    
    def display_enrichment_results(self):
        """Display enrichment results with filtering"""
        st.subheader("Enrichment Results")
        
        enriched_data = st.session_state['enriched_data']
        
        # Apply filters
        filtered_data = self.apply_filters(enriched_data)
        
        if not filtered_data:
            st.warning("No items match the current filters")
            return
        
        # Results display options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            view_mode = st.selectbox(
                "View Mode",
                ["Before/After Comparison", "LLM Only", "Baseline Only", "Side by Side"]
            )
        
        with col2:
            show_confidence = st.checkbox("Show Confidence", value=False)
        
        with col3:
            download_results = st.button("Download Results")
        
        # Display based on view mode
        if view_mode == "Before/After Comparison":
            self.display_before_after(filtered_data, show_confidence)
        elif view_mode == "LLM Only":
            self.display_single_model(filtered_data, "llm", show_confidence)
        elif view_mode == "Baseline Only":
            self.display_single_model(filtered_data, "baseline", show_confidence)
        elif view_mode == "Side by Side":
            self.display_side_by_side(filtered_data, show_confidence)
        
        # Download functionality
        if download_results:
            self.download_results(filtered_data)
    
    def apply_filters(self, enriched_data: List[Dict]) -> List[Dict]:
        """Apply category, cuisine, and attribute filters"""
        filtered = enriched_data
        
        # Category filter
        if st.session_state.get('selected_categories'):
            filtered = [
                item for item in filtered
                if (item.get('llm_enriched') and 
                    item['llm_enriched'].category in st.session_state['selected_categories']) or
                   (item.get('baseline_enriched') and 
                    item['baseline_enriched'].category in st.session_state['selected_categories'])
            ]
        
        # Cuisine filter
        if st.session_state.get('selected_cuisines'):
            filtered = [
                item for item in filtered
                if (item.get('llm_enriched') and 
                    item['llm_enriched'].cuisine in st.session_state['selected_cuisines']) or
                   (item.get('baseline_enriched') and 
                    item['baseline_enriched'].cuisine in st.session_state['selected_cuisines'])
            ]
        
        # Attribute filter
        if st.session_state.get('selected_attributes'):
            filtered = [
                item for item in filtered
                if (item.get('llm_enriched') and 
                    any(attr in item['llm_enriched'].attributes 
                        for attr in st.session_state['selected_attributes'])) or
                   (item.get('baseline_enriched') and 
                    any(attr in item['baseline_enriched'].attributes 
                        for attr in st.session_state['selected_attributes']))
            ]
        
        return filtered
    
    def display_before_after(self, filtered_data: List[Dict], show_confidence: bool):
        """Display before/after comparison"""
        for i, item in enumerate(filtered_data[:10]):  # Limit to 10 for display
            with st.expander(f"Item {i+1}: {item['raw_name']}", expanded=(i < 3)):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Original:**")
                    st.code(item['raw_name'])
                
                with col2:
                    st.write("**Enriched:**")
                    if item.get('llm_enriched'):
                        result = item['llm_enriched']
                        st.write(f"🤖 **LLM Result:**")
                        st.write(f"Name: {result.item_name}")
                        st.write(f"Category: {result.category}")
                        st.write(f"Cuisine: {result.cuisine}")
                        st.write(f"Attributes: {', '.join(result.attributes) if result.attributes else 'None'}")
                    
                    if item.get('baseline_enriched'):
                        result = item['baseline_enriched']
                        st.write(f"📝 **Baseline Result:**")
                        st.write(f"Name: {result.item_name}")
                        st.write(f"Category: {result.category}")
                        st.write(f"Cuisine: {result.cuisine}")
                        st.write(f"Attributes: {', '.join(result.attributes) if result.attributes else 'None'}")
    
    def display_single_model(self, filtered_data: List[Dict], model_type: str, show_confidence: bool):
        """Display results from a single model"""
        results_key = f"{model_type}_enriched"
        model_name = "LLM" if model_type == "llm" else "Baseline"
        
        # Create DataFrame for display
        display_data = []
        for item in filtered_data:
            if item.get(results_key):
                result = item[results_key]
                display_data.append({
                    'Raw Name': item['raw_name'],
                    'Enriched Name': result.item_name,
                    'Category': result.category,
                    'Cuisine': result.cuisine,
                    'Attributes': ', '.join(result.attributes) if result.attributes else 'None'
                })
        
        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"No {model_name} results available")
    
    def display_side_by_side(self, filtered_data: List[Dict], show_confidence: bool):
        """Display LLM and baseline results side by side"""
        display_data = []
        
        for item in filtered_data:
            row = {'Raw Name': item['raw_name']}
            
            # LLM results
            if item.get('llm_enriched'):
                llm = item['llm_enriched']
                row.update({
                    'LLM Name': llm.item_name,
                    'LLM Category': llm.category,
                    'LLM Cuisine': llm.cuisine,
                    'LLM Attributes': ', '.join(llm.attributes) if llm.attributes else 'None'
                })
            else:
                row.update({
                    'LLM Name': 'N/A',
                    'LLM Category': 'N/A', 
                    'LLM Cuisine': 'N/A',
                    'LLM Attributes': 'N/A'
                })
            
            # Baseline results
            if item.get('baseline_enriched'):
                baseline = item['baseline_enriched']
                row.update({
                    'Baseline Name': baseline.item_name,
                    'Baseline Category': baseline.category,
                    'Baseline Cuisine': baseline.cuisine,
                    'Baseline Attributes': ', '.join(baseline.attributes) if baseline.attributes else 'None'
                })
            else:
                row.update({
                    'Baseline Name': 'N/A',
                    'Baseline Category': 'N/A',
                    'Baseline Cuisine': 'N/A', 
                    'Baseline Attributes': 'N/A'
                })
            
            display_data.append(row)
        
        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
    
    def download_results(self, filtered_data: List[Dict]):
        """Generate download link for results"""
        # Create DataFrame
        download_data = []
        for item in filtered_data:
            row = {
                'raw_name': item['raw_name'],
            }
            
            # Add LLM results if available
            if item.get('llm_enriched'):
                llm = item['llm_enriched']
                row.update({
                    'llm_name': llm.item_name,
                    'llm_category': llm.category,
                    'llm_cuisine': llm.cuisine,
                    'llm_attributes': '|'.join(llm.attributes)
                })
            
            # Add baseline results if available  
            if item.get('baseline_enriched'):
                baseline = item['baseline_enriched']
                row.update({
                    'baseline_name': baseline.item_name,
                    'baseline_category': baseline.category,
                    'baseline_cuisine': baseline.cuisine,
                    'baseline_attributes': '|'.join(baseline.attributes)
                })
            
            download_data.append(row)
        
        df = pd.DataFrame(download_data)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"enriched_menu_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def generate_sample_data(self):
        """Generate sample data for demonstration"""
        sample_size = st.session_state.get('sample_size', 50)
        
        with st.spinner(f"Generating {sample_size} sample menu items..."):
            sample_data = self.data_generator.generate_messy_data(sample_size)
            
            # Create DataFrame
            df = pd.DataFrame([{'raw_name': item['raw_name']} for item in sample_data])
            
            # Process the data
            self.process_menu_data(df)
    
    def model_comparison_tab(self):
        """Model comparison interface"""
        st.header("🔍 Model Comparison")
        
        if 'enriched_data' not in st.session_state:
            st.info("Process some menu data first to see model comparison")
            return
        
        enriched_data = st.session_state['enriched_data']
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_items = len(enriched_data)
            st.metric("Total Items", total_items)
        
        with col2:
            llm_success = sum(1 for item in enriched_data if item.get('llm_enriched'))
            llm_success_rate = llm_success / total_items if total_items > 0 else 0
            st.metric("LLM Success Rate", f"{llm_success_rate:.1%}")
        
        with col3:
            baseline_success = sum(1 for item in enriched_data if item.get('baseline_enriched'))
            baseline_success_rate = baseline_success / total_items if total_items > 0 else 0
            st.metric("Baseline Success Rate", f"{baseline_success_rate:.1%}")
        
        # Category distribution comparison
        st.subheader("Category Distribution Comparison")
        self.plot_category_comparison(enriched_data)
        
        # Cuisine distribution comparison
        st.subheader("Cuisine Distribution Comparison")
        self.plot_cuisine_comparison(enriched_data)
    
    def plot_category_comparison(self, enriched_data: List[Dict]):
        """Plot category distribution comparison"""
        llm_categories = [item['llm_enriched'].category for item in enriched_data 
                         if item.get('llm_enriched')]
        baseline_categories = [item['baseline_enriched'].category for item in enriched_data 
                              if item.get('baseline_enriched')]
        
        # Create comparison DataFrame
        llm_counts = pd.Series(llm_categories).value_counts()
        baseline_counts = pd.Series(baseline_categories).value_counts()
        
        # Combine into DataFrame
        all_categories = set(llm_counts.index.tolist() + baseline_counts.index.tolist())
        comparison_data = []
        
        for category in all_categories:
            comparison_data.append({
                'Category': category,
                'LLM': llm_counts.get(category, 0),
                'Baseline': baseline_counts.get(category, 0)
            })
        
        df = pd.DataFrame(comparison_data)
        
        # Plot
        fig = px.bar(df, x='Category', y=['LLM', 'Baseline'], 
                     title='Category Distribution: LLM vs Baseline',
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_cuisine_comparison(self, enriched_data: List[Dict]):
        """Plot cuisine distribution comparison"""
        llm_cuisines = [item['llm_enriched'].cuisine for item in enriched_data 
                       if item.get('llm_enriched')]
        baseline_cuisines = [item['baseline_enriched'].cuisine for item in enriched_data 
                            if item.get('baseline_enriched')]
        
        # Create comparison DataFrame
        llm_counts = pd.Series(llm_cuisines).value_counts()
        baseline_counts = pd.Series(baseline_cuisines).value_counts()
        
        # Combine into DataFrame
        all_cuisines = set(llm_counts.index.tolist() + baseline_counts.index.tolist())
        comparison_data = []
        
        for cuisine in all_cuisines:
            comparison_data.append({
                'Cuisine': cuisine,
                'LLM': llm_counts.get(cuisine, 0),
                'Baseline': baseline_counts.get(cuisine, 0)
            })
        
        df = pd.DataFrame(comparison_data)
        
        # Plot
        fig = px.bar(df, x='Cuisine', y=['LLM', 'Baseline'],
                     title='Cuisine Distribution: LLM vs Baseline', 
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    def evaluation_tab(self):
        """Evaluation interface"""
        st.header("📈 Model Evaluation")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            evaluation_size = st.number_input("Evaluation Dataset Size", 
                                            min_value=10, max_value=200, value=50)
        
        with col2:
            if st.button("Run Evaluation"):
                self.run_evaluation(evaluation_size)
        
        if 'evaluation_results' in st.session_state:
            self.display_evaluation_results()
    
    def run_evaluation(self, size: int):
        """Run comprehensive evaluation"""
        with st.spinner(f"Running evaluation with {size} test items..."):
            benchmark = BenchmarkRunner()
            comparison_result = benchmark.run_full_benchmark(test_size=size, save_results=False)
            st.session_state['evaluation_results'] = comparison_result
            st.success("Evaluation completed!")
    
    def display_evaluation_results(self):
        """Display evaluation results"""
        results = st.session_state['evaluation_results']
        
        st.subheader("Overall Performance Metrics")
        
        # Display comparison table
        st.dataframe(results.detailed_comparison.round(3))
        
        # Key insights
        st.subheader("Key Insights")
        
        improvements = results.improvement
        
        if improvements['accuracy'] > 0:
            st.success(f"✅ LLM improved accuracy by {improvements['accuracy']:.3f}")
        else:
            st.warning(f"⚠️ LLM accuracy decreased by {abs(improvements['accuracy']):.3f}")
        
        if improvements['f1_score'] > 0:
            st.success(f"✅ LLM improved F1-score by {improvements['f1_score']:.3f}")
        else:
            st.warning(f"⚠️ LLM F1-score decreased by {abs(improvements['f1_score']):.3f}")
        
        if improvements['json_validity_rate'] > 0:
            st.success(f"✅ LLM improved JSON validity by {improvements['json_validity_rate']:.3f}")
        else:
            st.warning(f"⚠️ LLM JSON validity decreased by {abs(improvements['json_validity_rate']):.3f}")
        
        # Performance visualization
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        baseline_scores = [results.baseline_result.accuracy, results.baseline_result.precision,
                          results.baseline_result.recall, results.baseline_result.f1_score]
        llm_scores = [results.llm_result.accuracy, results.llm_result.precision, 
                     results.llm_result.recall, results.llm_result.f1_score]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Baseline', x=metrics, y=baseline_scores))
        fig.add_trace(go.Bar(name='LLM', x=metrics, y=llm_scores))
        
        fig.update_layout(title='Model Performance Comparison', barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    def sample_data_tab(self):
        """Sample data generation and preview"""
        st.header("🔬 Sample Data Generation")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Generate Test Data")
            sample_size = st.number_input("Number of samples", min_value=10, max_value=500, value=50)
            
            if st.button("Generate Samples"):
                with st.spinner("Generating sample data..."):
                    sample_data = self.data_generator.generate_messy_data(sample_size)
                    st.session_state['sample_data'] = sample_data
                    st.success(f"Generated {len(sample_data)} samples!")
        
        with col2:
            st.subheader("Data Statistics")
            if 'sample_data' in st.session_state:
                sample_data = st.session_state['sample_data']
                st.metric("Total Samples", len(sample_data))
                
                # Category distribution
                categories = [item['ground_truth']['category'] for item in sample_data]
                unique_categories = len(set(categories))
                st.metric("Unique Categories", unique_categories)
                
                # Cuisine distribution
                cuisines = [item['ground_truth']['cuisine'] for item in sample_data]
                unique_cuisines = len(set(cuisines))
                st.metric("Unique Cuisines", unique_cuisines)
        
        # Display sample data
        if 'sample_data' in st.session_state:
            st.subheader("Sample Data Preview")
            sample_data = st.session_state['sample_data']
            
            # Create preview DataFrame
            preview_data = []
            for item in sample_data[:20]:  # Show first 20
                preview_data.append({
                    'Raw Name': item['raw_name'],
                    'Ground Truth Name': item['ground_truth']['item_name'],
                    'Category': item['ground_truth']['category'],
                    'Cuisine': item['ground_truth']['cuisine'],
                    'Attributes': ', '.join(item['ground_truth']['attributes'])
                })
            
            df = pd.DataFrame(preview_data)
            st.dataframe(df, use_container_width=True)
            
            # Download option
            if st.button("Download Sample Data"):
                # Create full DataFrame
                full_data = []
                for item in sample_data:
                    full_data.append({
                        'raw_name': item['raw_name'],
                        'ground_truth_name': item['ground_truth']['item_name'],
                        'ground_truth_category': item['ground_truth']['category'],
                        'ground_truth_cuisine': item['ground_truth']['cuisine'],
                        'ground_truth_attributes': '|'.join(item['ground_truth']['attributes'])
                    })
                
                df_full = pd.DataFrame(full_data)
                csv_buffer = io.StringIO()
                df_full.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Sample CSV",
                    data=csv_data,
                    file_name=f"sample_menu_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    def text_to_order_tab(self):
        """Text-to-Order conversion tab"""
        st.header("🛒 Text-to-Order Conversion")
        st.markdown("Convert natural language cravings into structured checkout orders!")
        
        # Information section
        with st.expander("ℹ️ How It Works", expanded=False):
            st.markdown("""
            **Transform your cravings into orders:**
            - Type what you want in plain English: *"craving mcchicken with large fries and medium sprite, mayo and ketchup included"*
            - Our dual processing system uses both rule-based and LLM approaches
            - Get a complete checkout with items, quantities, sizes, modifications, and pricing
            
            **Features:**
            - 🤖 **LLM Parser**: AI-powered understanding of complex requests
            - 📝 **Rule-based Parser**: Fast keyword matching for common patterns  
            - 💰 **Smart Pricing**: Automatic price calculation with size and modification adjustments
            - 🔍 **Dual Comparison**: See how both approaches handle your order
            """)
        
        # Menu display section
        with st.expander("📋 Available Menu Items", expanded=False):
            menu_info = self.order_processor.get_menu_info()
            st.text(menu_info)
        
        # Input section
        st.subheader("💬 Enter Your Order")
        
        # Order input
        order_text = st.text_area(
            "What are you craving?",
            placeholder="Example: craving mcchicken with large fries and medium sprite, mayo and ketchup included",
            height=100,
            help="Describe what you want in natural language. Include quantities, sizes, and modifications."
        )
        
        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            use_both_parsers = st.checkbox("Enable LLM Comparison", value=False, 
                                         help="Compare rule-based and LLM approaches (LLM currently disabled)")
        with col2:
            show_comparison = st.checkbox("Show Detailed Analysis", value=True,
                                        help="Display detailed parsing analysis and metrics")
        
        # Process order button
        if st.button("🚀 Process Order", type="primary", use_container_width=True):
            if not order_text.strip():
                st.error("Please enter your order text first!")
                return
            
            with st.spinner("🤔 Processing your order... This may take 1-10 minutes with LLM..."):
                try:
                    # Process the order
                    result = self.order_processor.process_order_text(
                        order_text.strip(), 
                        use_both_parsers=use_both_parsers
                    )
                    
                    # Display results
                    if show_comparison and use_both_parsers:
                        # Show comparison view
                        st.subheader("🔄 Parser Comparison")
                        comparison_display = self.order_processor.create_order_comparison_display(result)
                        st.text(comparison_display)
                        
                        # Metrics
                        comparison_metrics = self.order_processor.compare_parsing_results(result)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Baseline Items", comparison_metrics['baseline_items'])
                        with col2:
                            st.metric("LLM Items", comparison_metrics['llm_items'])
                        with col3:
                            st.metric("Baseline Time", f"{comparison_metrics['baseline_time']:.2f}s")
                        with col4:
                            st.metric("LLM Time", f"{comparison_metrics['llm_time']:.2f}s")
                    
                    # Show preferred checkout
                    st.subheader("🛒 Your Order Checkout")
                    
                    # Determine preferred order (LLM first, then baseline)
                    preferred_order = result.llm_order or result.baseline_order
                    parser_type = "LLM" if result.llm_order else "Baseline"
                    
                    if preferred_order:
                        checkout_display = self.order_processor.get_checkout_display(
                            preferred_order, parser_type
                        )
                        
                        # Display in a nice container
                        st.code(checkout_display, language=None)
                        
                        # Order summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Items", preferred_order.item_count)
                        with col2:
                            st.metric("Subtotal", f"${preferred_order.subtotal:.2f}")
                        with col3:
                            st.metric("Tax", f"${preferred_order.tax_amount:.2f}")
                        with col4:
                            st.metric("TOTAL", f"${preferred_order.total_amount:.2f}")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.success("✅ Order Ready for Checkout!")
                        with col2:
                            if st.button("🔄 Modify Order"):
                                st.info("Modify the text above and process again")
                        with col3:
                            if st.button("📱 Place Order"):
                                st.balloons()
                                st.success("🎉 Order placed successfully!")
                    
                    else:
                        st.error("❌ Could not process your order. Please try rephrasing your request.")
                        
                        # Show processing notes if available
                        if result.processing_notes:
                            with st.expander("🔍 Processing Details"):
                                for note in result.processing_notes:
                                    st.text(f"• {note}")
                
                except Exception as e:
                    st.error(f"❌ Error processing order: {str(e)}")
                    st.info("💡 Try simplifying your request or check if the items are on our menu")
        
        # Example orders section
        st.subheader("💡 Try These Examples")
        examples = [
            "craving mcchicken with large fries and medium sprite, mayo and ketchup included",
            "I want two big macs with extra cheese and a large coke",
            "can I get a small sprite and chicken nuggets with bbq sauce please",
            "one apple pie and medium fries no salt",
            "double mcchicken with no mayo, extra pickles and large fries"
        ]
        
        cols = st.columns(len(examples))
        for i, example in enumerate(examples):
            with cols[i]:
                if st.button(f"Try Example {i+1}", key=f"example_{i}"):
                    st.session_state.example_text = example
                    st.rerun()
        
        # Auto-fill example if button was clicked
        if hasattr(st.session_state, 'example_text'):
            st.text_area(
                "Selected Example:",
                value=st.session_state.example_text,
                height=60,
                disabled=True
            )
            if st.button("Use This Example"):
                # This would set the main text area, but Streamlit doesn't support this directly
                st.info("Copy the example text above and paste it into the main order field")
            
    def about_tab(self):
        """About page with project information"""
        st.header("ℹ️ About This Application")
        
        st.markdown("""
        ### Menu Item Categorization & Enrichment with LLMs
        
        This application demonstrates AI-powered menu item categorization and enrichment using Large Language Models (LLMs).
        
        #### 🎯 Key Features
        - **Data Processing**: Upload messy menu data and see it transformed
        - **Model Comparison**: Compare rule-based baseline vs LLM enrichment
        - **Evaluation Framework**: Comprehensive metrics (F1-score, JSON validity rate)
        - **Interactive Filtering**: Filter results by category, cuisine, and attributes
        - **Sample Data Generation**: Generate synthetic messy menu data for testing
        
        #### 🔧 Tech Stack
        - **Python**: Core programming language
        - **Ollama**: Local LLM for menu enrichment (with fallback to mock)
        - **Streamlit**: Web interface framework
        - **Pandas & NumPy**: Data manipulation
        - **Scikit-learn**: Evaluation metrics
        - **Plotly**: Interactive visualizations
        
        #### 📊 Target Schema
        ```json
        {
          "item_name": "Chicken Shawarma with Fries",
          "category": "Main Dish", 
          "cuisine": "Middle Eastern",
          "attributes": ["Spicy", "Large Portion", "Halal"]
        }
        ```
        
        #### 🚀 How to Use
        1. **Upload Data**: Use the "Data Processing" tab to upload a CSV with menu items
        2. **View Results**: See enriched results with before/after comparison
        3. **Compare Models**: Use the "Model Comparison" tab to see differences
        4. **Run Evaluation**: Use the "Evaluation" tab for comprehensive metrics
        5. **Generate Samples**: Use the "Sample Data" tab to create test data
        
        #### 💡 Tips
        - CSV files should have a 'raw_name' column with menu item names
        - Use filters in the sidebar to focus on specific categories or cuisines
        - Try the sample data generator to see the system in action
        - Download enriched results for further analysis
        
        #### ⚠️ Note
        This demo uses a mock LLM enricher when Ollama is not available. For best results, 
        ensure Ollama is running with a compatible model (e.g., llama2, mistral).
        """)


def main():
    """Main function to run the Streamlit app"""
    app = MenuEnrichmentApp()
    app.run()


if __name__ == "__main__":
    main()