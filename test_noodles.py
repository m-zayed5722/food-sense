import sys
import os
sys.path.append('.')
from src.llm_enricher import get_enricher, LLMConfig
from src.baseline import BaselineClassifier
import json

def test_noodles_enrichment():
    """Test menu item enrichment specifically for noodles"""
    
    print("🍜 Testing Menu Item Enrichment for Noodles")
    print("=" * 50)
    
    # Configure to use real Ollama (not mock)
    config = LLMConfig(model_name="llama2", timeout=60)
    llm_enricher = get_enricher(config=config, use_mock=False)
    baseline = BaselineClassifier()
    
    # Test the specific example "noodles"
    test_item = "noodles"
    
    print(f"📝 Testing item: '{test_item}'")
    print("-" * 30)
    
    # Test LLM enrichment
    print("🤖 LLM (Ollama) Result:")
    try:
        llm_result = llm_enricher.enrich_item(test_item)
        if llm_result:
            print(f"   ✅ Name: {llm_result.item_name}")
            print(f"   ✅ Category: {llm_result.category}")
            print(f"   ✅ Cuisine: {llm_result.cuisine}")
            print(f"   ✅ Attributes: {llm_result.attributes if llm_result.attributes else 'None'}")
        else:
            print("   ❌ LLM enrichment failed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test baseline for comparison
    print("📝 Baseline (Rule-based) Result:")
    try:
        baseline_result = baseline.classify_item(test_item)
        print(f"   ✅ Name: {baseline_result.item_name}")
        print(f"   ✅ Category: {baseline_result.category}")
        print(f"   ✅ Cuisine: {baseline_result.cuisine}")
        print(f"   ✅ Attributes: {baseline_result.attributes if baseline_result.attributes else 'None'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_noodles_enrichment()