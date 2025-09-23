import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append('.')

from src.schema import MenuItem, MenuSchema
from src.baseline import BaselineClassifier
from src.llm_enricher import MockLLMEnricher
from src.data_generator import DataGenerator, DataCleaner
from src.evaluation import MenuItemEvaluator


class TestSchema(unittest.TestCase):
    """Test schema validation and utilities"""
    
    def setUp(self):
        self.schema = MenuSchema()
    
    def test_menu_item_creation(self):
        """Test MenuItem creation"""
        item = MenuItem(
            item_name="Chicken Tikka Masala",
            category="Main Dish",
            cuisine="Indian",
            attributes=["Spicy", "Dairy-Free"]
        )
        
        self.assertEqual(item.item_name, "Chicken Tikka Masala")
        self.assertEqual(item.category, "Main Dish")
        self.assertEqual(item.cuisine, "Indian")
        self.assertEqual(len(item.attributes), 2)
    
    def test_valid_categories(self):
        """Test category validation"""
        self.assertTrue(self.schema.is_valid_category("Main Dish"))
        self.assertTrue(self.schema.is_valid_category("Pizza"))
        self.assertFalse(self.schema.is_valid_category("Invalid Category"))
    
    def test_valid_cuisines(self):
        """Test cuisine validation"""
        self.assertTrue(self.schema.is_valid_cuisine("Italian"))
        self.assertTrue(self.schema.is_valid_cuisine("Chinese"))
        self.assertFalse(self.schema.is_valid_cuisine("Invalid Cuisine"))
    
    def test_valid_attributes(self):
        """Test attribute filtering"""
        mixed_attributes = ["Vegetarian", "Invalid", "Spicy", "Another Invalid"]
        valid_attributes = self.schema.get_valid_attributes(mixed_attributes)
        self.assertEqual(set(valid_attributes), {"Vegetarian", "Spicy"})


class TestBaselineClassifier(unittest.TestCase):
    """Test baseline classifier functionality"""
    
    def setUp(self):
        self.classifier = BaselineClassifier()
    
    def test_text_preprocessing(self):
        """Test text preprocessing"""
        text = "CHKN BURGER W/ CHEESE"
        processed = self.classifier.preprocess_text(text)
        self.assertEqual(processed, "chicken burger with cheese")
    
    def test_category_classification(self):
        """Test category classification"""
        # Test pizza
        self.assertEqual(self.classifier.classify_category("Margherita Pizza"), "Pizza")
        
        # Test burger  
        self.assertEqual(self.classifier.classify_category("Beef Burger"), "Burger")
        
        # Test soup
        self.assertEqual(self.classifier.classify_category("Chicken Soup"), "Soup")
        
        # Test default
        self.assertEqual(self.classifier.classify_category("Random Food Item"), "Main Dish")
    
    def test_cuisine_classification(self):
        """Test cuisine classification"""
        # Test Italian
        self.assertEqual(self.classifier.classify_cuisine("Spaghetti Carbonara"), "Italian")
        
        # Test Chinese
        self.assertEqual(self.classifier.classify_cuisine("Chicken Stir Fry"), "Chinese")
        
        # Test default
        self.assertEqual(self.classifier.classify_cuisine("Random Item"), "American")
    
    def test_attribute_classification(self):
        """Test attribute classification"""
        attributes = self.classifier.classify_attributes("Spicy Vegetarian Wings")
        self.assertIn("Spicy", attributes)
        self.assertIn("Vegetarian", attributes)
    
    def test_full_classification(self):
        """Test complete item classification"""
        result = self.classifier.classify_item("spicy chicken shawarma")
        
        self.assertIsInstance(result, MenuItem)
        self.assertEqual(result.category, "Main Dish")
        self.assertEqual(result.cuisine, "Middle Eastern")
        self.assertIn("Spicy", result.attributes)


class TestDataGenerator(unittest.TestCase):
    """Test data generation functionality"""
    
    def setUp(self):
        self.generator = DataGenerator(seed=42)  # Fixed seed for reproducibility
    
    def test_typo_addition(self):
        """Test typo addition"""
        text = "chicken with cheese"
        typo_text = self.generator.add_typos(text, typo_probability=1.0)  # Always add typos
        self.assertNotEqual(text, typo_text)
    
    def test_abbreviation_addition(self):
        """Test abbreviation addition"""
        text = "chicken sandwich with fries"
        abbrev_text = self.generator.add_abbreviations(text, abbrev_probability=1.0)
        self.assertIn("w/", abbrev_text)  # Should have "with" -> "w/"
    
    def test_messy_data_generation(self):
        """Test messy data generation"""
        data = self.generator.generate_messy_data(5)
        
        self.assertEqual(len(data), 5)
        
        for item in data:
            self.assertIn('raw_name', item)
            self.assertIn('ground_truth', item)
            self.assertIn('item_name', item['ground_truth'])
            self.assertIn('category', item['ground_truth'])
            self.assertIn('cuisine', item['ground_truth'])
            self.assertIn('attributes', item['ground_truth'])


class TestDataCleaner(unittest.TestCase):
    """Test data cleaning functionality"""
    
    def test_text_cleaning(self):
        """Test basic text cleaning"""
        dirty_text = "  MESSY   TEXT  w/  EXTRA   SPACES  "
        cleaned = DataCleaner.clean_text(dirty_text)
        self.assertEqual(cleaned, "MESSY TEXT with EXTRA SPACES")
    
    def test_price_normalization(self):
        """Test price extraction and normalization"""
        self.assertEqual(DataCleaner.normalize_price("$12.99"), 12.99)
        self.assertEqual(DataCleaner.normalize_price("15.50"), 15.50)
        self.assertEqual(DataCleaner.normalize_price("Price: $8"), 8.0)
        self.assertEqual(DataCleaner.normalize_price("Invalid"), 0.0)


class TestMockLLMEnricher(unittest.TestCase):
    """Test mock LLM enricher"""
    
    def setUp(self):
        self.enricher = MockLLMEnricher()
    
    def test_mock_enrichment(self):
        """Test mock enrichment functionality"""
        result = self.enricher.enrich_item("chicken burger")
        
        self.assertIsInstance(result, MenuItem)
        self.assertEqual(result.item_name, "Chicken Burger")
        self.assertEqual(result.category, "Burger")
        self.assertEqual(result.cuisine, "American")
    
    def test_mock_batch_enrichment(self):
        """Test mock batch enrichment"""
        items = ["pizza margherita", "chicken soup", "vegetable stir fry"]
        results = self.enricher.enrich_batch(items)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, MenuItem)
    
    def test_mock_success_rate(self):
        """Test mock success rate"""
        items = ["item1", "item2", "item3"]
        results = self.enricher.enrich_batch(items)
        success_rate = self.enricher.get_success_rate(results)
        
        self.assertEqual(success_rate, 1.0)  # Mock always succeeds


class TestEvaluator(unittest.TestCase):
    """Test evaluation functionality"""
    
    def setUp(self):
        self.evaluator = MenuItemEvaluator()
    
    def test_accuracy_calculation(self):
        """Test accuracy calculation"""
        ground_truth = [
            MenuItem(item_name="Pizza Margherita", category="Pizza", cuisine="Italian", attributes=["Vegetarian"]),
            MenuItem(item_name="Chicken Burger", category="Burger", cuisine="American", attributes=[])
        ]
        
        predictions = [
            MenuItem(item_name="Pizza Margherita", category="Pizza", cuisine="Italian", attributes=["Vegetarian"]),
            MenuItem(item_name="Chicken Burger", category="Main Dish", cuisine="American", attributes=[])  # Wrong category
        ]
        
        category_accuracy = self.evaluator.calculate_accuracy(ground_truth, predictions, 'category')
        self.assertEqual(category_accuracy, 0.5)  # 1 out of 2 correct
        
        cuisine_accuracy = self.evaluator.calculate_accuracy(ground_truth, predictions, 'cuisine')
        self.assertEqual(cuisine_accuracy, 1.0)  # Both correct
    
    def test_json_validity_rate(self):
        """Test JSON validity rate calculation"""
        predictions = [
            MenuItem(item_name="Item 1", category="Main Dish", cuisine="American", attributes=[]),
            None,  # Invalid prediction
            MenuItem(item_name="Item 2", category="Main Dish", cuisine="American", attributes=[])
        ]
        
        validity_rate = self.evaluator.calculate_json_validity_rate(predictions)
        self.assertEqual(validity_rate, 2/3)  # 2 out of 3 valid


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_end_to_end_pipeline(self):
        """Test complete pipeline from data generation to evaluation"""
        # Generate test data
        generator = DataGenerator(seed=42)
        test_data = generator.generate_messy_data(5)
        
        # Initialize models
        baseline = BaselineClassifier()
        mock_llm = MockLLMEnricher()
        
        # Get predictions
        raw_names = [item['raw_name'] for item in test_data]
        baseline_results = baseline.batch_classify(raw_names)
        llm_results = mock_llm.enrich_batch(raw_names)
        
        # Verify results
        self.assertEqual(len(baseline_results), 5)
        self.assertEqual(len(llm_results), 5)
        
        for result in baseline_results + llm_results:
            self.assertIsInstance(result, MenuItem)
            self.assertIsNotNone(result.item_name)
            self.assertIsNotNone(result.category)
            self.assertIsNotNone(result.cuisine)
            self.assertIsInstance(result.attributes, list)


def run_tests():
    """Run all tests"""
    print("Running Menu Enrichment Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    
    return success


if __name__ == "__main__":
    run_tests()