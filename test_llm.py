import sys
import logging
sys.path.append('.')
from src.llm_enricher import get_enricher

def test_llm_enricher():
    logging.basicConfig(level=logging.INFO)
    
    # Test LLM enricher (will use mock if Ollama not available)
    enricher = get_enricher()
    
    test_items = [
        "chiken shawarma w/ fries",
        "MARGHERITA PIZA", 
        "beef burger w cheese",
        "pad thai noodles",
        "vegetable stir fry",
        "buffalo wings"
    ]
    
    print("LLM Enrichment Results:")
    print("=" * 60)
    
    for item in test_items:
        result = enricher.enrich_item(item)
        if result:
            print(f"Raw: {item}")
            print(f"Enriched: {result.item_name}")
            print(f"Category: {result.category}")
            print(f"Cuisine: {result.cuisine}")
            print(f"Attributes: {result.attributes}")
            print("-" * 60)
        else:
            print(f"Failed to enrich: {item}")
            print("-" * 60)

if __name__ == "__main__":
    test_llm_enricher()