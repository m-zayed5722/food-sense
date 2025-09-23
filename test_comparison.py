import sys
import os
sys.path.append('.')
from src.llm_enricher import get_enricher, LLMConfig
from src.baseline import BaselineClassifier

def test_various_noodles():
    """Test various noodle dishes to see LLM vs Baseline differences"""
    
    print("🍜 Menu Item Enrichment: LLM vs Baseline Comparison")
    print("=" * 65)
    
    # Configure LLM
    config = LLMConfig(model_name="llama2", timeout=30)
    llm_enricher = get_enricher(config=config, use_mock=False)
    baseline = BaselineClassifier()
    
    # Test various menu items
    test_items = [
        "noodles",
        "spicy noodles", 
        "thai noodles",
        "chicken noodles",
        "beef noodles",
        "ramen",
        "pad thai",
        "chkn tikka w/ rice",
        "veggie burger",
        "margherita piza"
    ]
    
    print(f"{'Item':<20} | {'LLM Category':<12} | {'LLM Cuisine':<12} | {'Baseline Category':<12} | {'Baseline Cuisine':<12}")
    print("-" * 85)
    
    for item in test_items:
        # Get LLM result
        try:
            llm_result = llm_enricher.enrich_item(item)
            if llm_result:
                llm_cat = llm_result.category
                llm_cui = llm_result.cuisine
                llm_name = llm_result.item_name
            else:
                llm_cat = "Failed"
                llm_cui = "Failed" 
                llm_name = item
        except:
            llm_cat = "Error"
            llm_cui = "Error"
            llm_name = item
        
        # Get baseline result
        try:
            baseline_result = baseline.classify_item(item)
            base_cat = baseline_result.category
            base_cui = baseline_result.cuisine
            base_name = baseline_result.item_name
        except:
            base_cat = "Error"
            base_cui = "Error"
            base_name = item
        
        print(f"{item:<20} | {llm_cat:<12} | {llm_cui:<12} | {base_cat:<12} | {base_cui:<12}")
        
        # Show the enhanced names if different
        if llm_name != base_name and len(llm_name) > len(item):
            print(f"  🤖 LLM enhanced: '{llm_name}'")
    
    print("\n" + "=" * 65)
    print("✅ Comparison completed!")
    print("\n💡 Key Differences:")
    print("- LLM can make contextual cuisine choices (e.g., noodles → Chinese)")
    print("- LLM can enhance generic names with more descriptive terms")
    print("- Baseline uses rule-based keyword matching")
    print("- Both handle typos and abbreviations")

if __name__ == "__main__":
    test_various_noodles()