import json
import requests
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from src.schema import MenuItem, MenuSchema
from pydantic import ValidationError


@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    model_name: str = "llama2"  # Default Ollama model
    base_url: str = "http://localhost:11434"
    timeout: int = 600  # 10 minutes timeout for large models
    max_retries: int = 3
    temperature: float = 0.1  # Low temperature for consistent structured output


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.logger = logging.getLogger(__name__)
    
    def is_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
        return []
    
    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """Generate text using Ollama"""
        model = model or self.config.model_name
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature
            }
        }
        
        for attempt in range(self.config.max_retries):
            try:
                self.logger.info(f"Sending request to {model} (timeout: {self.config.timeout}s)...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload,
                    timeout=self.config.timeout
                )
                
                elapsed_time = time.time() - start_time
                self.logger.info(f"Response received in {elapsed_time:.2f} seconds")
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '').strip()
                else:
                    self.logger.warning(f"Ollama API error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"Attempt {attempt + 1} timed out after {self.config.timeout}s: {e}")
                if attempt < self.config.max_retries - 1:
                    self.logger.info("Retrying with exponential backoff...")
                    time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None


class LLMEnricher:
    """LLM-based menu item enricher"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.client = OllamaClient(config)
        self.schema = MenuSchema()
        self.logger = logging.getLogger(__name__)
        
        # System prompt template
        self.system_prompt = """You are an expert food categorization assistant. Your task is to analyze menu item names and return structured, clean information.

CATEGORIES: Main Dish, Appetizer, Dessert, Beverage, Side Dish, Soup, Salad, Pizza, Sandwich, Pasta, Burger

CUISINES: American, Italian, Chinese, Mexican, Indian, Japanese, Thai, French, Mediterranean, Middle Eastern, Greek, Korean, Vietnamese, Spanish, Lebanese, Turkish

ATTRIBUTES: Vegetarian, Vegan, Gluten-Free, Dairy-Free, Spicy, Mild, Large Portion, Small Portion, Halal, Kosher, Organic, Low-Carb, Keto-Friendly, Protein-Rich, Healthy, Fried, Grilled, Baked, Steamed, Raw

IMPORTANT RULES:
1. Return ONLY valid JSON with no additional text
2. Clean up the item name (fix typos, proper capitalization, make it descriptive)
3. Choose exactly ONE category and ONE cuisine from the lists above
4. If the input is very generic (like "noodles"), make reasonable assumptions and create a more specific name
5. Attributes should be a list of applicable items from the list above
6. Be conservative with attributes - only include what's clearly indicated or commonly associated
7. For generic items, choose the most common interpretation

Examples:
- "noodles" → "Chicken Noodle Soup" (Main Dish, American)
- "spicy noodles" → "Spicy Stir-Fried Noodles" (Main Dish, Chinese, ["Spicy"])
- "thai noodles" → "Pad Thai Noodles" (Main Dish, Thai)

Response format:
{
  "item_name": "Clean Descriptive Item Name",
  "category": "Category Name",
  "cuisine": "Cuisine Name", 
  "attributes": ["Attribute1", "Attribute2"]
}"""
    
    def create_prompt(self, raw_item_name: str) -> str:
        """Create prompt for menu item enrichment"""
        return f"""{self.system_prompt}

Analyze this menu item: "{raw_item_name}"

Return JSON:"""
    
    def parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response and extract JSON"""
        if not response:
            return None
        
        # Try to find JSON in response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            self.logger.warning("No JSON found in response")
            return None
        
        json_str = response[json_start:json_end]
        
        try:
            data = json.loads(json_str)
            # Validate required fields
            if not all(key in data for key in ['item_name', 'category', 'cuisine']):
                self.logger.warning("Missing required fields in JSON response")
                return None
            
            # Ensure attributes is a list
            if 'attributes' not in data:
                data['attributes'] = []
            elif not isinstance(data['attributes'], list):
                data['attributes'] = []
            
            return data
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Invalid JSON in response: {e}")
            return None
    
    def validate_and_fix_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix LLM output data"""
        if not data:
            return None
        
        # Fix category
        if not self.schema.is_valid_category(data['category']):
            self.logger.warning(f"Invalid category: {data['category']}, defaulting to Main Dish")
            data['category'] = "Main Dish"
        
        # Fix cuisine
        if not self.schema.is_valid_cuisine(data['cuisine']):
            self.logger.warning(f"Invalid cuisine: {data['cuisine']}, defaulting to American")
            data['cuisine'] = "American"
        
        # Fix attributes
        data['attributes'] = self.schema.get_valid_attributes(data['attributes'])
        
        return data
    
    def enrich_item(self, raw_item_name: str) -> Optional[MenuItem]:
        """Enrich a single menu item using LLM"""
        if not self.client.is_available():
            self.logger.error("Ollama server not available")
            return None
        
        self.logger.info(f"🤔 Processing menu item: '{raw_item_name}' (this may take 1-10 minutes)...")
        
        prompt = self.create_prompt(raw_item_name)
        response = self.client.generate(prompt)
        
        if not response:
            self.logger.error(f"No response from LLM for item: {raw_item_name}")
            return None
        
        self.logger.info(f"✅ LLM response received for: '{raw_item_name}'")
        
        # Parse response
        data = self.parse_llm_response(response)
        if not data:
            self.logger.error(f"Failed to parse LLM response for: {raw_item_name}")
            return None
        
        # Validate and fix data
        data = self.validate_and_fix_data(data)
        if not data:
            return None
        
        try:
            result = MenuItem(**data)
            self.logger.info(f"🍽️ Successfully enriched: '{raw_item_name}' → '{result.item_name}'")
            return result
        except ValidationError as e:
            self.logger.error(f"Validation error creating MenuItem: {e}")
            return None
    
    def enrich_batch(self, raw_item_names: List[str], show_progress: bool = True) -> List[Optional[MenuItem]]:
        """Enrich multiple menu items"""
        results = []
        total = len(raw_item_names)
        
        for i, item_name in enumerate(raw_item_names):
            if show_progress and i % 10 == 0:
                print(f"Processing {i+1}/{total} items...")
            
            result = self.enrich_item(item_name)
            results.append(result)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        return results
    
    def get_success_rate(self, results: List[Optional[MenuItem]]) -> float:
        """Calculate success rate of enrichment"""
        successful = sum(1 for result in results if result is not None)
        return successful / len(results) if results else 0.0
    
    def enrich_with_fallback(self, raw_item_name: str, fallback_enricher=None) -> MenuItem:
        """Enrich with fallback to baseline if LLM fails"""
        result = self.enrich_item(raw_item_name)
        
        if result is None and fallback_enricher:
            self.logger.warning(f"LLM failed for '{raw_item_name}', using fallback")
            result = fallback_enricher.classify_item(raw_item_name)
        
        return result


class MockLLMEnricher:
    """Mock enricher for testing when Ollama is not available"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def enrich_item(self, raw_item_name: str) -> MenuItem:
        """Mock enrichment - returns basic categorization"""
        self.logger.info(f"Using mock enricher for: {raw_item_name}")
        
        # Simple mock logic
        name_lower = raw_item_name.lower()
        
        if "pizza" in name_lower:
            category, cuisine = "Pizza", "Italian"
        elif "burger" in name_lower:
            category, cuisine = "Burger", "American"
        elif "soup" in name_lower:
            category, cuisine = "Soup", "American"
        else:
            category, cuisine = "Main Dish", "American"
        
        attributes = []
        if "vegetarian" in name_lower or "veggie" in name_lower:
            attributes.append("Vegetarian")
        if "spicy" in name_lower or "hot" in name_lower:
            attributes.append("Spicy")
        
        return MenuItem(
            item_name=raw_item_name.title(),
            category=category,
            cuisine=cuisine,
            attributes=attributes
        )
    
    def enrich_batch(self, raw_item_names: List[str], show_progress: bool = True) -> List[MenuItem]:
        """Mock batch enrichment"""
        return [self.enrich_item(name) for name in raw_item_names]
    
    def get_success_rate(self, results: List[MenuItem]) -> float:
        """Mock success rate"""
        return 1.0  # Mock always "succeeds"


# Factory function to get appropriate enricher
def get_enricher(config: LLMConfig = None, use_mock: bool = False) -> Union[LLMEnricher, MockLLMEnricher]:
    """Get appropriate enricher based on availability"""
    if use_mock:
        return MockLLMEnricher()
    
    enricher = LLMEnricher(config)
    if not enricher.client.is_available():
        logging.warning("Ollama not available, using mock enricher")
        return MockLLMEnricher()
    
    return enricher


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test LLM enricher
    enricher = get_enricher()
    
    test_items = [
        "chiken shawarma w/ fries",
        "MARGHERITA PIZA", 
        "beef burger w cheese",
        "pad thai noodles"
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