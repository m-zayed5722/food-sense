import sys
import os
sys.path.append('.')
from src.llm_enricher import get_enricher, LLMConfig
from src.baseline import BaselineClassifier
import json

def test_menu_item_enrichment():
    """Test menu item enrichment with real examples"""
    
    print("🍜 Menu Item Categorization & Enrichment Test")
    print("=" * 60)
    
    # Test items including your example
    test_items = [
        "noodles",
        "thai noodles", 
        "chicken noodles",
        "spicy beef noodles",
        "pad thai noodles",
        "ramen noodles",
        "italian pasta noodles",
        "chkn shawarma w/ fries",
        "margherita pizza",
        "vegetarian burger"
    ]
    
    # Initialize enrichers
    print("🤖 Initializing LLM enricher...")
    llm_enricher = get_enricher(use_mock=False)  # Try to use real Ollama
    
    print("📝 Initializing baseline classifier...")
    baseline = BaselineClassifier()
    
    print("\n🧪 Testing enrichment on sample items:")
    print("-" * 60)
    
    for i, item in enumerate(test_items, 1):
        print(f"\n{i}. Testing: '{item}'")
        print("-" * 40)
        
        # Test LLM enrichment
        print("🤖 LLM Result:")
        llm_result = llm_enricher.enrich_item(item)
        if llm_result:
            print(f"   Name: {llm_result.item_name}")
            print(f"   Category: {llm_result.category}")
            print(f"   Cuisine: {llm_result.cuisine}")
            print(f"   Attributes: {llm_result.attributes}")
        else:
            print("   ❌ LLM enrichment failed")
        
        # Test baseline
        print("📝 Baseline Result:")
        baseline_result = baseline.classify_item(item)
        print(f"   Name: {baseline_result.item_name}")
        print(f"   Category: {baseline_result.category}")
        print(f"   Cuisine: {baseline_result.cuisine}")
        print(f"   Attributes: {baseline_result.attributes}")
        
        # Compare results
        if llm_result:
            print("🔍 Comparison:")
            category_match = "✅" if llm_result.category == baseline_result.category else "❌"
            cuisine_match = "✅" if llm_result.cuisine == baseline_result.cuisine else "❌"
            print(f"   Category match: {category_match}")
            print(f"   Cuisine match: {cuisine_match}")

def test_specific_noodles():
    """Specifically test noodle variations"""
    print("\n🍜 Specific Noodles Test")
    print("=" * 40)
    
    noodle_variations = [
        "noodles",
        "chicken noodles", 
        "beef noodles",
        "vegetable noodles",
        "spicy noodles",
        "thai noodles",
        "chinese noodles",
        "ramen",
        "pad thai",
        "lo mein"
    ]
    
    llm_enricher = get_enricher(use_mock=False)
    
    for noodle in noodle_variations:
        print(f"\n🍜 '{noodle}':")
        result = llm_enricher.enrich_item(noodle)
        if result:
            print(f"   → {result.item_name} | {result.category} | {result.cuisine}")
            if result.attributes:
                print(f"   → Attributes: {', '.join(result.attributes)}")
        else:
            print("   ❌ Failed to enrich")

if __name__ == "__main__":
    print("Starting Menu Item Enrichment Test...")
    
    # Check if Ollama is available
    from src.llm_enricher import OllamaClient
    client = OllamaClient()
    
    if client.is_available():
        print("✅ Ollama is available!")
        models = client.list_models()
        if models:
            print(f"📋 Available models: {', '.join(models)}")
        else:
            print("⚠️ No models found. You may need to pull a model first.")
            print("💡 Try: ollama pull llama2")
    else:
        print("❌ Ollama is not available. Using mock enricher.")
        print("💡 Make sure Ollama is running: ollama serve")
    
    print()
    
    # Run tests
    test_menu_item_enrichment()
    test_specific_noodles()
    
    print("\n✅ Test completed!")