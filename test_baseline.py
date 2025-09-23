import sys
sys.path.append('.')
from src.baseline import BaselineClassifier

def test_baseline():
    classifier = BaselineClassifier()
    
    test_items = [
        'chiken shawarma w/ fries',
        'MARGHERITA PIZA',
        'beef burger w cheese',
        'pad thai noodles',
        'vegetable stir fry',
        'buffalo wings'
    ]
    
    print('Baseline Classification Results:')
    print('=' * 60)
    
    for item in test_items:
        result = classifier.classify_item(item)
        confidence = classifier.get_classification_confidence(item)
        
        print(f'Raw: {item}')
        print(f'Cleaned: {result.item_name}')
        print(f'Category: {result.category} (confidence: {confidence["category"]:.2f})')
        print(f'Cuisine: {result.cuisine} (confidence: {confidence["cuisine"]:.2f})')
        print(f'Attributes: {result.attributes}')
        print('-' * 60)

if __name__ == "__main__":
    test_baseline()