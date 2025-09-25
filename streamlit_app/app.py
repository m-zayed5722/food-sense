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
            page_title="Food Sense - Restaurant Menu System",
            page_icon="🍽️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for enhanced styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        .feature-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
            backdrop-filter: blur(10px);
        }
        
        .feature-card h4 {
            color: #ffffff !important;
            margin-bottom: 1rem;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .feature-card ul {
            color: #f8f9ff;
        }
        
        .feature-card li {
            color: #f0f2ff;
            margin-bottom: 0.5rem;
        }
        
        .feature-card strong {
            color: #ffffff;
            font-weight: 700;
        }
        .order-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .order-display-card {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(44, 62, 80, 0.4);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 0.5rem;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card h3 {
            color: #ffffff !important;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .metric-card p {
            color: #f0f2ff !important;
            font-weight: 500;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }
        
        .metric-card strong {
            color: #ffffff !important;
        }
        .restaurant-badge {
            background: #667eea;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 0.2rem;
            display: inline-block;
        }
        .success-banner {
            background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 1rem 0;
        }
        .price-highlight {
            background: #28a745;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            .main-header {
                padding: 1rem;
                font-size: 0.9rem;
            }
            .feature-card {
                padding: 1rem;
                margin: 0.5rem 0;
            }
            .metric-card {
                padding: 0.5rem;
                margin: 0.25rem;
            }
            .restaurant-badge {
                padding: 0.2rem 0.5rem;
                font-size: 0.8rem;
                margin: 0.1rem;
            }
        }
        
        /* Enhanced Animations and Hover Effects */
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        }
        
        /* Gradient Card Hover Effects */
        div[style*="linear-gradient"]:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 50px rgba(0,0,0,0.2);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        /* Pulse animation for gradient cards */
        @keyframes pulse-glow {
            0% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); }
            50% { box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4); }
            100% { box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); }
        }
        
        /* Add subtle animation to gradient backgrounds */
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Loading spinner enhancement */
        .stSpinner > div {
            border-color: #667eea transparent #667eea transparent;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Enhanced Header with gradient background
        st.markdown("""
        <div class="main-header">
            <h1>🍽️ Food Sense - AI Restaurant Ordering</h1>
            <h3>Transform Natural Language into Perfect Orders</h3>
            <p><strong>300 Real Menu Items</strong> from <strong>20 Major Restaurant Chains</strong></p>
            <p>🤖 AI-Powered • 📱 Smart Ordering • 🏪 Multi-Restaurant Support</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.setup_sidebar()
        
        # Main content with restaurant-focused tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "🛒 Text-to-Order",
            "🏪 Restaurant Menu", 
            "📊 Data Processing", 
            "🔍 Model Comparison", 
            "📈 Evaluation", 
            "🔬 Sample Data",
            "ℹ️ About"
        ])
        
        with tab1:
            self.text_to_order_tab()
        
        with tab2:
            self.restaurant_menu_tab()
        
        with tab3:
            self.data_processing_tab()
        
        with tab4:
            self.model_comparison_tab()
        
        with tab5:
            self.evaluation_tab()
        
        with tab6:
            self.sample_data_tab()
        
        with tab7:
            self.about_tab()
    
    def setup_sidebar(self):
        """Enhanced sidebar with modern styling"""
        
        # Sidebar header
        st.sidebar.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 1rem;">
            <h3>⚙️ Control Panel</h3>
            <p>Customize your experience</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Model selection with enhanced styling
        st.sidebar.markdown("**🤖 AI Engine Settings**")
        use_llm = st.sidebar.checkbox(
            "Enable LLM Parser", 
            value=False,  # Default to rule-based since it's working perfectly
            help="Use AI language model for advanced parsing (requires Ollama setup)"
        )
        
        if use_llm:
            st.sidebar.success("🤖 AI Parser: Active")
            st.sidebar.info("⚡ Fallback: Rule-based if AI unavailable")
        else:
            st.sidebar.success("📝 Enhanced Rule-Based: Active")
            st.sidebar.info("🚀 Optimized for speed and accuracy")
        
        # Store settings in session state
        st.session_state['use_llm'] = use_llm
        
        # Performance stats
        st.sidebar.markdown("**📊 System Status**")
        st.sidebar.metric("Parser Status", "✅ Online")
        st.sidebar.metric("Menu Database", "300 items")
        st.sidebar.metric("Restaurant Coverage", "20 chains")
        
        # Restaurant filter
        st.sidebar.subheader("Restaurant Filter")
        try:
            from src.order_schema import OrderSchema
            menu_items = OrderSchema.create_sample_menu()
            
            # Get unique restaurants
            restaurants = set()
            restaurant_keywords = {
                "McDonald's": ["mcdonald", "mcchicken", "big mac", "quarter pounder", "mcflurry", "mcnugget"],
                "Starbucks": ["frappuccino", "macchiato", "americano", "latte", "venti", "grande", "caramel ribbon"],
                "Taco Bell": ["taco", "burrito", "quesadilla", "chalupa", "crunchwrap", "beefy", "nacho"],
                "KFC": ["kfc", "colonel", "popcorn chicken", "famous bowl", "zinger", "hot wings"],
                "Burger King": ["whopper", "burger king", "king", "chicken fries", "impossible whopper"],
                "Subway": ["footlong", "subway", "italian bmt", "meatball marinara", "turkey breast"],
                "Pizza Hut": ["pizza hut", "pepperoni pizza", "meat lovers", "supreme pizza", "stuffed crust"],
                "Chick-fil-A": ["chick-fil-a", "chick fil a", "chicken sandwich", "waffle fries", "nuggets"],
                "Wendy's": ["wendy", "baconator", "frosty", "spicy chicken", "dave's single"],
                "Dairy Queen": ["dairy queen", "dq", "blizzard", "dilly bar", "hot dog", "chicken strip basket"],
                "Five Guys": ["five guys", "cajun fries", "bacon cheeseburger", "little cheeseburger"],
                "Chipotle": ["chipotle", "burrito bowl", "barbacoa", "carnitas", "sofritas", "guac"],
                "Dunkin'": ["dunkin", "donut", "iced coffee", "coolatta", "munchkins", "bagel"],
                "Popeyes": ["popeyes", "louisiana", "spicy chicken", "biscuit", "red beans"],
                "Arby's": ["arby", "roast beef", "curly fries", "beef n cheddar", "turkey gyro"],
                "Sonic": ["sonic", "cherry limeade", "mozzarella sticks", "corn dog", "slush"],
                "Panda Express": ["panda express", "orange chicken", "chow mein", "fried rice", "beijing beef"],
                "Papa John's": ["papa john", "garlic sauce", "pepperoni pizza", "the works"],
                "Carl's Jr": ["carl's jr", "famous star", "western bacon", "hand-breaded"],
                "Wingstop": ["wingstop", "lemon pepper", "garlic parmesan", "atomic wings", "louisiana rub"]
            }
            
            for item in menu_items:
                name_lower = item.name.lower()
                for rest_name, keywords in restaurant_keywords.items():
                    if any(keyword in name_lower for keyword in keywords):
                        restaurants.add(rest_name)
                        break
                else:
                    restaurants.add("General")
            
            selected_restaurants = st.sidebar.multiselect(
                "Filter by Restaurant",
                options=sorted(list(restaurants)),
                default=[]
            )
            st.session_state['selected_restaurants'] = selected_restaurants
            
        except Exception as e:
            st.sidebar.error(f"Error loading restaurants: {e}")
        
        # Dataset size for generation
        st.sidebar.subheader("Data Generation")
        sample_size = st.sidebar.slider("Sample Data Size", 10, 200, 50)
        st.session_state['sample_size'] = sample_size
        
        # Filters
        st.sidebar.subheader("Content Filters")
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
    
    def restaurant_menu_tab(self):
        """Restaurant menu browsing interface"""
        st.header("🏪 Restaurant Menu Browser")
        st.markdown("Browse our menu database organized by restaurant brands with **300 real menu items from 20 major chains**")
        
        try:
            from src.order_schema import OrderSchema
            menu_items = OrderSchema.create_sample_menu()
            
            # Restaurant identification
            restaurant_keywords = {
                "McDonald's": ["mcdonald", "mcchicken", "big mac", "quarter pounder", "mcflurry", "mcnugget"],
                "Starbucks": ["frappuccino", "macchiato", "americano", "latte", "venti", "grande", "caramel ribbon"],
                "Taco Bell": ["taco", "burrito", "quesadilla", "chalupa", "crunchwrap", "beefy", "nacho"],
                "KFC": ["kfc", "colonel", "popcorn chicken", "famous bowl", "zinger", "hot wings"],
                "Burger King": ["whopper", "burger king", "king", "chicken fries", "impossible whopper"],
                "Subway": ["footlong", "subway", "italian bmt", "meatball marinara", "turkey breast"],
                "Pizza Hut": ["pizza hut", "pepperoni pizza", "meat lovers", "supreme pizza", "stuffed crust"],
                "Chick-fil-A": ["chick-fil-a", "chick fil a", "chicken sandwich", "waffle fries", "nuggets"],
                "Wendy's": ["wendy", "baconator", "frosty", "spicy chicken", "dave's single"],
                "Dairy Queen": ["dairy queen", "dq", "blizzard", "dilly bar", "hot dog", "chicken strip basket"],
                "Five Guys": ["five guys", "cajun fries", "bacon cheeseburger", "little cheeseburger"],
                "Chipotle": ["chipotle", "burrito bowl", "barbacoa", "carnitas", "sofritas", "guac"],
                "Dunkin'": ["dunkin", "donut", "iced coffee", "coolatta", "munchkins", "bagel"],
                "Popeyes": ["popeyes", "louisiana", "spicy chicken", "biscuit", "red beans"],
                "Arby's": ["arby", "roast beef", "curly fries", "beef n cheddar", "turkey gyro"],
                "Sonic": ["sonic", "cherry limeade", "mozzarella sticks", "corn dog", "slush"],
                "Panda Express": ["panda express", "orange chicken", "chow mein", "fried rice", "beijing beef"],
                "Papa John's": ["papa john", "garlic sauce", "pepperoni pizza", "the works"],
                "Carl's Jr": ["carl's jr", "famous star", "western bacon", "hand-breaded"],
                "Wingstop": ["wingstop", "lemon pepper", "garlic parmesan", "atomic wings", "louisiana rub"]
            }
            
            # Organize items by restaurant
            restaurant_groups = {}
            for item in menu_items:
                restaurant = "General"
                name_lower = item.name.lower()
                
                for rest_name, keywords in restaurant_keywords.items():
                    if any(keyword in name_lower for keyword in keywords):
                        restaurant = rest_name
                        break
                
                if restaurant not in restaurant_groups:
                    restaurant_groups[restaurant] = []
                restaurant_groups[restaurant].append(item)
            
            # Sort restaurants by number of items (descending)
            sorted_restaurants = dict(sorted(restaurant_groups.items(), 
                                           key=lambda x: len(x[1]), reverse=True))
            
            # Filter by selected restaurants
            selected_restaurants = st.session_state.get('selected_restaurants', [])
            if selected_restaurants:
                sorted_restaurants = {k: v for k, v in sorted_restaurants.items() 
                                    if k in selected_restaurants}
            
            # Display summary
            total_restaurants = len(sorted_restaurants)
            total_items = sum(len(items) for items in sorted_restaurants.values())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏪 Restaurant Brands", total_restaurants)
            with col2:
                st.metric("📋 Menu Items", total_items)
            with col3:
                avg_items = total_items / total_restaurants if total_restaurants > 0 else 0
                st.metric("📊 Avg Items/Restaurant", f"{avg_items:.1f}")
            
            # Restaurant search
            search_term = st.text_input("🔍 Search menu items", placeholder="Search for items across all restaurants...")
            
            # Display restaurants
            for restaurant, items in sorted_restaurants.items():
                # Filter items by search term
                if search_term:
                    items = [item for item in items if search_term.lower() in item.name.lower()]
                    if not items:
                        continue
                
                with st.expander(f"🏪 **{restaurant}** ({len(items)} items)", expanded=(restaurant != "General")):
                    
                    # Group by category within restaurant
                    categories = {}
                    for item in items:
                        if item.category not in categories:
                            categories[item.category] = []
                        categories[item.category].append(item)
                    
                    # Display by category
                    for category, cat_items in categories.items():
                        st.markdown(f"**{category}** ({len(cat_items)} items)")
                        
                        # Create a table for the items
                        item_data = []
                        for item in cat_items:
                            # Get size and price info
                            sizes = [str(size).title() for size in item.available_sizes]
                            prices = [f"${price:.2f}" for price in item.size_pricing.values()]
                            
                            if len(sizes) == 1:
                                size_price = f"{sizes[0]} - {prices[0]}"
                            else:
                                size_price = f"{sizes[0]} - {prices[0]} | {sizes[-1]} - {prices[-1]}"
                            
                            # Get modifications
                            mods = [str(mod) for mod in item.available_modifications[:3]]
                            modifications = ", ".join(mods) if mods else "None"
                            if len(item.available_modifications) > 3:
                                modifications += f" (+{len(item.available_modifications) - 3} more)"
                            
                            item_data.append({
                                "Item Name": item.name,
                                "Size & Price": size_price,
                                "Available Modifications": modifications
                            })
                        
                        # Display as dataframe
                        if item_data:
                            df = pd.DataFrame(item_data)
                            st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        st.markdown("")  # Add spacing
            
            # No results message
            if not sorted_restaurants or total_items == 0:
                if search_term:
                    st.info(f"No menu items found matching '{search_term}'. Try a different search term.")
                else:
                    st.info("No restaurants match your current filters. Try adjusting the filters in the sidebar.")
            
        except Exception as e:
            st.error(f"Error displaying restaurant menu: {e}")
            st.info("Please ensure the menu database is properly loaded.")
    
    def text_to_order_tab(self):
        """Enhanced Text-to-Order conversion tab with modern design"""
        
        # Hero section
        st.markdown("""
        <div class="order-card">
            <h2>🛒 AI-Powered Text-to-Order</h2>
            <p style="font-size: 1.2rem; margin-bottom: 0;">Simply describe what you're craving and watch the magic happen!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced stats cards with gradient backgrounds
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border-radius: 15px; padding: 1.5rem; margin: 0.5rem;
                        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); text-align: center;
                        transform: translateZ(0); transition: all 0.3s ease;">
                <h2 style="margin: 0; font-size: 2.5rem;">🏪</h2>
                <h3 style="margin: 0.5rem 0; font-size: 2rem; font-weight: bold;">20</h3>
                <p style="margin: 0; font-size: 1rem; opacity: 0.9;">Restaurant Chains</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; border-radius: 15px; padding: 1.5rem; margin: 0.5rem;
                        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3); text-align: center;
                        transform: translateZ(0); transition: all 0.3s ease;">
                <h2 style="margin: 0; font-size: 2.5rem;">🍽️</h2>
                <h3 style="margin: 0.5rem 0; font-size: 2rem; font-weight: bold;">300</h3>
                <p style="margin: 0; font-size: 1rem; opacity: 0.9;">Menu Items</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; border-radius: 15px; padding: 1.5rem; margin: 0.5rem;
                        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3); text-align: center;
                        transform: translateZ(0); transition: all 0.3s ease;">
                <h2 style="margin: 0; font-size: 2.5rem;">🤖</h2>
                <h3 style="margin: 0.5rem 0; font-size: 2rem; font-weight: bold;">AI</h3>
                <p style="margin: 0; font-size: 1rem; opacity: 0.9;">Enhanced Parsing</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                        color: white; border-radius: 15px; padding: 1.5rem; margin: 0.5rem;
                        box-shadow: 0 8px 32px rgba(67, 233, 123, 0.3); text-align: center;
                        transform: translateZ(0); transition: all 0.3s ease;">
                <h2 style="margin: 0; font-size: 2.5rem;">⚡</h2>
                <h3 style="margin: 0.5rem 0; font-size: 2rem; font-weight: bold;">Fast</h3>
                <p style="margin: 0; font-size: 1rem; opacity: 0.9;">Real-time Results</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Information section with better styling
        with st.expander("ℹ️ How It Works - See the Magic Behind the Scenes", expanded=False):
            st.markdown("""
            <div class="feature-card">
                <h4>🚀 Advanced Natural Language Processing</h4>
                <ul>
                    <li><strong>Restaurant Detection:</strong> Automatically identifies your preferred restaurant</li>
                    <li><strong>Smart Item Matching:</strong> Finds exact menu items from your description</li>
                    <li><strong>Size & Quantity Intelligence:</strong> Understands "large", "medium", "two", etc.</li>
                    <li><strong>Modification Processing:</strong> Handles "no mayo", "extra cheese", "on the side"</li>
                    <li><strong>Real-time Pricing:</strong> Calculates total cost with tax and modifications</li>
                </ul>
            </div>
            
            <div class="feature-card">
                <h4>🤖 Dual Processing Engine</h4>
                <ul>
                    <li><strong>Rule-Based Parser:</strong> Lightning-fast keyword matching ⚡</li>
                    <li><strong>LLM Parser:</strong> Deep understanding of complex requests 🧠</li>
                    <li><strong>Restaurant Filtering:</strong> Only shows items from detected restaurant 🏪</li>
                    <li><strong>Confidence Scoring:</strong> Ensures accurate matches 🎯</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Restaurant showcase
        with st.expander("🏪 Supported Restaurant Chains", expanded=False):
            st.markdown("""
            <div style="text-align: center; margin: 1rem 0;">
                <span class="restaurant-badge">🍔 McDonald's</span>
                <span class="restaurant-badge">☕ Starbucks</span>
                <span class="restaurant-badge">🌮 Taco Bell</span>
                <span class="restaurant-badge">🍗 KFC</span>
                <span class="restaurant-badge">🍔 Burger King</span>
                <span class="restaurant-badge">🥤 Sonic</span>
                <span class="restaurant-badge">🥛 Dairy Queen</span>
                <span class="restaurant-badge">🥙 Subway</span>
                <span class="restaurant-badge">🍕 Pizza Hut</span>
                <span class="restaurant-badge">🍟 Five Guys</span>
                <span class="restaurant-badge">🌯 Chipotle</span>
                <span class="restaurant-badge">🍳 Wendy's</span>
                <span class="restaurant-badge">🥯 Dunkin'</span>
                <span class="restaurant-badge">🌶️ Carl's Jr</span>
                <span class="restaurant-badge">🍜 Panda Express</span>
                <span class="restaurant-badge">🍕 Papa John's</span>
                <span class="restaurant-badge">🐔 Chick-fil-A</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Show detailed menu
            self.display_restaurant_menu_compact()
        
        # Enhanced Input section with gradient background
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 20px; padding: 2rem; margin: 2rem 0;
                    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2); text-align: center;">
            <h2 style="margin: 0 0 1rem 0; font-size: 2rem; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                💬 Tell Us What You're Craving
            </h2>
            <p style="margin: 0; font-size: 1.2rem; opacity: 0.95; line-height: 1.6;">
                Use natural language - just like you'd tell a friend!<br>
                <span style="font-size: 1rem; opacity: 0.8;">Our AI understands context, quantities, sizes, and modifications.</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Example prompts
        st.markdown("**� Try these examples:**")
        examples_col1, examples_col2 = st.columns(2)
        
        with examples_col1:
            if st.button("🍔 McDonald's Combo", use_container_width=True):
                st.session_state.order_input = "craving a McChicken with large fries and medium sprite, mayo and ketchup included"
            if st.button("☕ Starbucks Coffee", use_container_width=True):
                st.session_state.order_input = "grande latte with extra shot and oat milk"
                
        with examples_col2:
            if st.button("🌮 Taco Bell Meal", use_container_width=True):
                st.session_state.order_input = "two crunchwrap supremes with extra sour cream and a large baja blast"
            if st.button("🍗 KFC Bucket", use_container_width=True):
                st.session_state.order_input = "family bucket with mashed potatoes and gravy, extra crispy"
        
        # Order input with enhanced styling
        order_text = st.text_area(
            "🗣️ What are you craving?",
            placeholder="Example: craving mcchicken with large fries and medium sprite, mayo and ketchup included",
            height=120,
            help="💡 Be as specific as you want! Include quantities (two, three), sizes (large, medium), and modifications (no mayo, extra cheese, on the side)",
            key="order_input"
        )
        
        # Enhanced processing options
        st.markdown("**⚙️ Processing Options:**")
        col1, col2 = st.columns(2)
        with col1:
            use_both_parsers = st.checkbox("🔄 Enable Parser Comparison", value=False, 
                                         help="Compare rule-based vs LLM approaches (requires LLM setup)")
        with col2:
            show_comparison = st.checkbox("📊 Show Detailed Analysis", value=True,
                                        help="Display processing metrics and confidence scores")
        
        # Enhanced process button
        st.markdown("<br>", unsafe_allow_html=True)
        process_clicked = st.button("🚀 Transform to Order", type="primary", use_container_width=True)
        
        if process_clicked:
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
                    
                    # Enhanced results display
                    st.markdown("""
                    <div class="success-banner">
                        <h3>🎉 Order Successfully Processed!</h3>
                        <p>Your natural language request has been transformed into a complete order</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Determine preferred order (LLM first, then baseline)
                    preferred_order = result.llm_order or result.baseline_order
                    parser_type = "LLM" if result.llm_order else "Enhanced Rule-Based"
                    
                    if preferred_order:
                        # Enhanced checkout display
                        st.markdown(f"""
                        <div class="feature-card">
                            <h3>🛒 Your Complete Order ({parser_type} Parser)</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        checkout_display = self.order_processor.get_checkout_display(
                            preferred_order, parser_type
                        )
                        
                        # Display in beautifully styled container
                        st.markdown(f"""
                        <div class="order-display-card">
                            <pre style="margin: 0; font-family: 'Courier New', monospace; color: white; line-height: 1.6;">{checkout_display}</pre>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Enhanced metrics display
                        st.markdown("**📊 Order Summary:**")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                                <h3>{preferred_order.item_count}</h3>
                                <p>Total Items</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);">
                                <h3>${preferred_order.subtotal:.2f}</h3>
                                <p>Subtotal</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col3:
                            st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);">
                                <h3>${preferred_order.tax_amount:.2f}</h3>
                                <p>Tax (8%)</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col4:
                            st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); box-shadow: 0 8px 25px rgba(67, 233, 123, 0.4); transform: scale(1.05);">
                                <h3 class="price-highlight">${preferred_order.total_amount:.2f}</h3>
                                <p><strong>TOTAL</strong></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Enhanced action section
                        st.markdown("<br>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.markdown("""
                            <div class="success-banner">
                                <h4>✅ Order Ready for Checkout!</h4>
                                <p>Your order has been processed and priced accurately</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("🔄 Try Another", use_container_width=True):
                                st.rerun()
                        
                        with col3:
                            if st.button("📤 Export Order", use_container_width=True):
                                order_json = {
                                    'order_text': order_text,
                                    'parser_used': parser_type,
                                    'total_amount': float(preferred_order.total_amount),
                                    'items': [{'name': item.name, 'quantity': item.quantity} for item in preferred_order.items]
                                }
                                st.download_button(
                                    "💾 Download JSON",
                                    data=json.dumps(order_json, indent=2),
                                    file_name=f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    mime="application/json"
                                )
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
    
    def display_restaurant_menu_compact(self):
        """Display menu items organized by restaurant brands in compact format"""
        try:
            from src.order_schema import OrderSchema
            menu_items = OrderSchema.create_sample_menu()
            
            # Group items by restaurant
            restaurant_groups = {}
            
            # Restaurant identification keywords
            restaurant_keywords = {
                "McDonald's": ["mcdonald", "mcchicken", "big mac", "quarter pounder", "mcflurry", "mcnugget"],
                "Starbucks": ["frappuccino", "macchiato", "americano", "latte", "venti", "grande", "caramel ribbon"],
                "Taco Bell": ["taco", "burrito", "quesadilla", "chalupa", "crunchwrap", "beefy", "nacho"],
                "KFC": ["kfc", "colonel", "popcorn chicken", "famous bowl", "zinger", "hot wings"],
                "Burger King": ["whopper", "burger king", "king", "chicken fries", "impossible whopper"],
                "Subway": ["footlong", "subway", "italian bmt", "meatball marinara", "turkey breast"],
                "Pizza Hut": ["pizza hut", "pepperoni pizza", "meat lovers", "supreme pizza", "stuffed crust"],
                "Chick-fil-A": ["chick-fil-a", "chick fil a", "chicken sandwich", "waffle fries", "nuggets"],
                "Wendy's": ["wendy", "baconator", "frosty", "spicy chicken", "dave's single"],
                "Dairy Queen": ["dairy queen", "dq", "blizzard", "dilly bar", "hot dog", "chicken strip basket"],
                "Five Guys": ["five guys", "cajun fries", "bacon cheeseburger", "little cheeseburger"],
                "Chipotle": ["chipotle", "burrito bowl", "barbacoa", "carnitas", "sofritas", "guac"],
                "Dunkin'": ["dunkin", "donut", "iced coffee", "coolatta", "munchkins", "bagel"],
                "Popeyes": ["popeyes", "louisiana", "spicy chicken", "biscuit", "red beans"],
                "Arby's": ["arby", "roast beef", "curly fries", "beef n cheddar", "turkey gyro"],
                "Sonic": ["sonic", "cherry limeade", "mozzarella sticks", "corn dog", "slush"],
                "Panda Express": ["panda express", "orange chicken", "chow mein", "fried rice", "beijing beef"],
                "Papa John's": ["papa john", "garlic sauce", "pepperoni pizza", "the works"],
                "Carl's Jr": ["carl's jr", "famous star", "western bacon", "hand-breaded"],
                "Wingstop": ["wingstop", "lemon pepper", "garlic parmesan", "atomic wings", "louisiana rub"]
            }
            
            # Organize items by restaurant
            for item in menu_items:
                restaurant = "General"
                name_lower = item.name.lower()
                
                # Check each restaurant's keywords
                for rest_name, keywords in restaurant_keywords.items():
                    if any(keyword in name_lower for keyword in keywords):
                        restaurant = rest_name
                        break
                
                if restaurant not in restaurant_groups:
                    restaurant_groups[restaurant] = []
                restaurant_groups[restaurant].append(item)
            
            # Sort restaurants by number of items (descending)
            sorted_restaurants = dict(sorted(restaurant_groups.items(), 
                                           key=lambda x: len(x[1]), reverse=True))
            
            # Display by restaurant (compact format)
            for restaurant, items in sorted_restaurants.items():
                if restaurant == "General" and len(sorted_restaurants) > 1:
                    continue  # Skip General if we have specific restaurants
                
                st.markdown(f"**🏪 {restaurant}** ({len(items)} items)")
                
                # Group by category within restaurant
                categories = {}
                for item in items:
                    if item.category not in categories:
                        categories[item.category] = []
                    categories[item.category].append(item)
                
                for category, cat_items in categories.items():
                    st.markdown(f"  *{category}:*")
                    for item in cat_items[:5]:  # Show first 5 items per category
                        sizes = ", ".join([str(size).title() for size in item.available_sizes[:3]])
                        price_range = f"${min(item.size_pricing.values()):.2f}"
                        if len(item.size_pricing) > 1:
                            price_range += f" - ${max(item.size_pricing.values()):.2f}"
                        st.markdown(f"    • {item.name} ({sizes}) - {price_range}")
                    
                    if len(cat_items) > 5:
                        st.markdown(f"    ... and {len(cat_items) - 5} more items")
                
                st.markdown("")  # Add spacing
            
            # Summary
            total_items = sum(len(items) for items in restaurant_groups.values())
            st.markdown(f"**Total: {len(restaurant_groups)} restaurants, {total_items} menu items**")
            
        except Exception as e:
            st.error(f"Error displaying menu: {e}")
            # Fallback to original method
            menu_info = self.order_processor.get_menu_info()
            st.text(menu_info)
    
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
    
    def about_tab(self):
        """Enhanced about page with modern design"""
        
        # Hero section
        st.markdown("""
        <div class="main-header">
            <h2>ℹ️ About Food Sense</h2>
            <p>Next-Generation AI Restaurant Ordering System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🚀 Revolutionary Features</h4>
                <ul>
                    <li><strong>🏪 Multi-Restaurant Support:</strong> 20 major chains integrated</li>
                    <li><strong>🤖 AI-Powered Parsing:</strong> Natural language understanding</li>
                    <li><strong>⚡ Real-time Processing:</strong> Instant order conversion</li>
                    <li><strong>🎯 Smart Recognition:</strong> Restaurant auto-detection</li>
                    <li><strong>💰 Dynamic Pricing:</strong> Automatic cost calculation</li>
                    <li><strong>📱 Responsive Design:</strong> Works on all devices</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>📊 Technical Excellence</h4>
                <ul>
                    <li><strong>🗄️ Comprehensive Database:</strong> 300 real menu items</li>
                    <li><strong>🔍 Advanced Filtering:</strong> Restaurant-specific search</li>
                    <li><strong>📈 Performance Metrics:</strong> Real-time analytics</li>
                    <li><strong>🛡️ Error Handling:</strong> Robust fallback systems</li>
                    <li><strong>📋 Export Options:</strong> JSON order download</li>
                    <li><strong>🔄 Live Updates:</strong> Dynamic content refresh</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Restaurant showcase
        st.markdown("""
        <div class="feature-card">
            <h4>🏪 Supported Restaurant Ecosystem</h4>
            <div style="text-align: center; margin: 1rem 0;">
                <span class="restaurant-badge">🍔 McDonald's</span>
                <span class="restaurant-badge">☕ Starbucks</span>
                <span class="restaurant-badge">🌮 Taco Bell</span>
                <span class="restaurant-badge">🍗 KFC</span>
                <span class="restaurant-badge">🍔 Burger King</span>
                <span class="restaurant-badge">🥙 Subway</span>
                <span class="restaurant-badge">🍕 Pizza Hut</span>
                <span class="restaurant-badge">🐔 Chick-fil-A</span>
                <span class="restaurant-badge">🥤 Wendy's</span>
                <span class="restaurant-badge">🥛 Dairy Queen</span>
                <span class="restaurant-badge">🍟 Five Guys</span>
                <span class="restaurant-badge">🌯 Chipotle</span>
                <span class="restaurant-badge">🥯 Dunkin'</span>
                <span class="restaurant-badge">🌶️ Carl's Jr</span>
                <span class="restaurant-badge">🍜 Panda Express</span>
                <span class="restaurant-badge">🍕 Papa John's</span>
                <span class="restaurant-badge">🥤 Sonic</span>
                <span class="restaurant-badge">🍗 Popeyes</span>
                <span class="restaurant-badge">🥓 Arby's</span>
                <span class="restaurant-badge">🍗 Wingstop</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Technical stack
        st.markdown("""
        <div class="feature-card">
            <h4>🔧 Technology Stack</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div>
                    <strong>🐍 Backend:</strong><br>
                    Python, Pandas, NumPy, Scikit-learn
                </div>
                <div>
                    <strong>🤖 AI/ML:</strong><br>
                    Ollama, Natural Language Processing
                </div>
                <div>
                    <strong>🖥️ Frontend:</strong><br>
                    Streamlit, Plotly, Custom CSS
                </div>
                <div>
                    <strong>📊 Data:</strong><br>
                    JSON, CSV, Real-time Processing
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Usage guide
        st.markdown("""
        <div class="feature-card">
            <h4>🚀 Quick Start Guide</h4>
            <ol>
                <li><strong>🛒 Text-to-Order:</strong> Try "craving mcchicken with large fries and medium sprite"</li>
                <li><strong>🏪 Restaurant Menu:</strong> Browse items organized by restaurant chains</li>
                <li><strong>📊 Data Processing:</strong> Upload CSV files with menu items for enrichment</li>
                <li><strong>🔍 Model Comparison:</strong> Compare rule-based vs AI parsing approaches</li>
                <li><strong>📈 Evaluation:</strong> Run comprehensive performance metrics</li>
                <li><strong>🔬 Sample Data:</strong> Generate test data to explore features</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent updates
        st.markdown("""
        <div class="success-banner">
            <h4>📈 Latest Enhancements</h4>
            <p><strong>✅ Enhanced Parser:</strong> Fixed critical ordering bugs with restaurant detection</p>
            <p><strong>✅ Modern UI:</strong> Redesigned interface with improved visual hierarchy</p>
            <p><strong>✅ Real Database:</strong> 300 authentic menu items from 20 major chains</p>
        </div>
        """, unsafe_allow_html=True)
def main():
    """Main function to run the Streamlit app"""
    app = MenuEnrichmentApp()
    app.run()


if __name__ == "__main__":
    main()