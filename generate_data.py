import sys
sys.path.append('.')
from src.data_generator import DataGenerator

def main():
    generator = DataGenerator()
    sample_data = generator.generate_messy_data(100)
    generator.save_to_csv(sample_data, 'data/sample_messy_menu.csv')
    print('Generated 100 messy menu items')
    
    print("\nSample generated items:")
    for i, item in enumerate(sample_data[:5]):
        print(f'{i+1}. Raw: {item["raw_name"]}')
        print(f'   Ground Truth: {item["ground_truth"]["item_name"]}')
        print(f'   Category: {item["ground_truth"]["category"]}')
        print(f'   Cuisine: {item["ground_truth"]["cuisine"]}')
        print('-' * 60)

if __name__ == "__main__":
    main()