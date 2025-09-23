import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from src.schema import MenuItem, MenuSchema
from src.baseline import BaselineClassifier
from src.llm_enricher import get_enricher, LLMEnricher, MockLLMEnricher
from src.data_generator import DataGenerator
import warnings
warnings.filterwarnings('ignore')


@dataclass
class EvaluationResult:
    """Results from model evaluation"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    json_validity_rate: float
    total_items: int
    successful_predictions: int
    category_scores: Dict[str, Dict[str, float]]
    cuisine_scores: Dict[str, Dict[str, float]]
    confusion_matrix: Optional[np.ndarray] = None


@dataclass
class ComparisonResult:
    """Comparison results between models"""
    baseline_result: EvaluationResult
    llm_result: EvaluationResult
    improvement: Dict[str, float]
    detailed_comparison: pd.DataFrame


class MenuItemEvaluator:
    """Evaluator for menu item classification models"""
    
    def __init__(self):
        self.schema = MenuSchema()
    
    def calculate_accuracy(self, ground_truth: List[MenuItem], predictions: List[Optional[MenuItem]], 
                          field: str) -> float:
        """Calculate accuracy for a specific field"""
        if not predictions or not ground_truth:
            return 0.0
        
        correct = 0
        total = 0
        
        for gt, pred in zip(ground_truth, predictions):
            if pred is not None:  # Only count successful predictions
                gt_value = getattr(gt, field)
                pred_value = getattr(pred, field)
                
                if field == 'attributes':
                    # For attributes, calculate Jaccard similarity
                    if not gt_value and not pred_value:
                        correct += 1
                    elif gt_value or pred_value:
                        gt_set = set(gt_value) if gt_value else set()
                        pred_set = set(pred_value) if pred_value else set()
                        if gt_set == pred_set:
                            correct += 1
                else:
                    if gt_value == pred_value:
                        correct += 1
                total += 1
        
        return correct / total if total > 0 else 0.0
    
    def calculate_f1_scores(self, ground_truth: List[MenuItem], predictions: List[Optional[MenuItem]], 
                           field: str) -> Dict[str, float]:
        """Calculate F1 scores for each class in a field"""
        if not predictions or not ground_truth:
            return {}
        
        # Extract values for successful predictions
        gt_values = []
        pred_values = []
        
        for gt, pred in zip(ground_truth, predictions):
            if pred is not None:
                if field == 'attributes':
                    # For attributes, we'll flatten and treat each as binary
                    gt_attrs = set(getattr(gt, field, []))
                    pred_attrs = set(getattr(pred, field, []))
                    
                    # Get all possible attributes
                    all_attrs = gt_attrs.union(pred_attrs)
                    for attr in all_attrs:
                        gt_values.append(attr if attr in gt_attrs else 'NOT_' + attr)
                        pred_values.append(attr if attr in pred_attrs else 'NOT_' + attr)
                else:
                    gt_values.append(getattr(gt, field))
                    pred_values.append(getattr(pred, field))
        
        if not gt_values:
            return {}
        
        # Calculate precision, recall, F1
        try:
            precision, recall, f1, support = precision_recall_fscore_support(
                gt_values, pred_values, average=None, zero_division=0
            )
            
            # Get unique labels
            unique_labels = sorted(list(set(gt_values + pred_values)))
            
            scores = {}
            for i, label in enumerate(unique_labels):
                if i < len(f1):
                    scores[label] = {
                        'precision': float(precision[i]) if i < len(precision) else 0.0,
                        'recall': float(recall[i]) if i < len(recall) else 0.0,
                        'f1': float(f1[i]) if i < len(f1) else 0.0,
                        'support': int(support[i]) if i < len(support) else 0
                    }
            
            return scores
        except Exception as e:
            print(f"Error calculating F1 scores for {field}: {e}")
            return {}
    
    def calculate_json_validity_rate(self, predictions: List[Optional[MenuItem]]) -> float:
        """Calculate the rate of valid JSON/structured outputs"""
        if not predictions:
            return 0.0
        
        valid_count = sum(1 for pred in predictions if pred is not None)
        return valid_count / len(predictions)
    
    def evaluate_model(self, model, test_data: List[Dict[str, Any]], 
                      model_name: str = "Unknown") -> EvaluationResult:
        """Evaluate a model against test data"""
        print(f"Evaluating {model_name}...")
        
        # Extract raw names and ground truth
        raw_names = [item['raw_name'] for item in test_data]
        ground_truth = [MenuItem(**item['ground_truth']) for item in test_data]
        
        # Get predictions
        if hasattr(model, 'enrich_batch'):
            predictions = model.enrich_batch(raw_names, show_progress=False)
        elif hasattr(model, 'batch_classify'):
            predictions = model.batch_classify(raw_names)
        else:
            # Single item classification
            predictions = [model.classify_item(name) if hasattr(model, 'classify_item') 
                         else model.enrich_item(name) for name in raw_names]
        
        # Calculate metrics
        json_validity_rate = self.calculate_json_validity_rate(predictions)
        successful_predictions = sum(1 for pred in predictions if pred is not None)
        
        # Calculate accuracy for each field
        category_accuracy = self.calculate_accuracy(ground_truth, predictions, 'category')
        cuisine_accuracy = self.calculate_accuracy(ground_truth, predictions, 'cuisine')
        attributes_accuracy = self.calculate_accuracy(ground_truth, predictions, 'attributes')
        
        # Overall accuracy (average of all fields)
        overall_accuracy = (category_accuracy + cuisine_accuracy + attributes_accuracy) / 3
        
        # Calculate F1 scores
        category_scores = self.calculate_f1_scores(ground_truth, predictions, 'category')
        cuisine_scores = self.calculate_f1_scores(ground_truth, predictions, 'cuisine')
        
        # Calculate overall precision, recall, F1
        overall_precision = np.mean([scores['precision'] for scores in category_scores.values()] +
                                  [scores['precision'] for scores in cuisine_scores.values()])
        overall_recall = np.mean([scores['recall'] for scores in category_scores.values()] +
                               [scores['recall'] for scores in cuisine_scores.values()])
        overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall) \
                    if (overall_precision + overall_recall) > 0 else 0
        
        return EvaluationResult(
            model_name=model_name,
            accuracy=overall_accuracy,
            precision=overall_precision,
            recall=overall_recall,
            f1_score=overall_f1,
            json_validity_rate=json_validity_rate,
            total_items=len(test_data),
            successful_predictions=successful_predictions,
            category_scores=category_scores,
            cuisine_scores=cuisine_scores
        )
    
    def compare_models(self, baseline_model, llm_model, test_data: List[Dict[str, Any]]) -> ComparisonResult:
        """Compare baseline and LLM models"""
        print("Running model comparison...")
        
        baseline_result = self.evaluate_model(baseline_model, test_data, "Baseline (Rule-based)")
        llm_result = self.evaluate_model(llm_model, test_data, "LLM (Ollama)")
        
        # Calculate improvements
        improvement = {
            'accuracy': llm_result.accuracy - baseline_result.accuracy,
            'precision': llm_result.precision - baseline_result.precision,
            'recall': llm_result.recall - baseline_result.recall,
            'f1_score': llm_result.f1_score - baseline_result.f1_score,
            'json_validity_rate': llm_result.json_validity_rate - baseline_result.json_validity_rate
        }
        
        # Create detailed comparison DataFrame
        comparison_data = {
            'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'JSON Validity Rate', 'Successful Predictions'],
            'Baseline': [
                baseline_result.accuracy,
                baseline_result.precision, 
                baseline_result.recall,
                baseline_result.f1_score,
                baseline_result.json_validity_rate,
                baseline_result.successful_predictions
            ],
            'LLM': [
                llm_result.accuracy,
                llm_result.precision,
                llm_result.recall, 
                llm_result.f1_score,
                llm_result.json_validity_rate,
                llm_result.successful_predictions
            ],
            'Improvement': [
                improvement['accuracy'],
                improvement['precision'],
                improvement['recall'],
                improvement['f1_score'], 
                improvement['json_validity_rate'],
                llm_result.successful_predictions - baseline_result.successful_predictions
            ]
        }
        
        detailed_comparison = pd.DataFrame(comparison_data)
        
        return ComparisonResult(
            baseline_result=baseline_result,
            llm_result=llm_result,
            improvement=improvement,
            detailed_comparison=detailed_comparison
        )
    
    def print_evaluation_report(self, result: EvaluationResult):
        """Print detailed evaluation report"""
        print(f"\n{'='*60}")
        print(f"EVALUATION REPORT: {result.model_name}")
        print(f"{'='*60}")
        
        print(f"Overall Metrics:")
        print(f"  Accuracy: {result.accuracy:.3f}")
        print(f"  Precision: {result.precision:.3f}")
        print(f"  Recall: {result.recall:.3f}")
        print(f"  F1-Score: {result.f1_score:.3f}")
        print(f"  JSON Validity Rate: {result.json_validity_rate:.3f}")
        print(f"  Successful Predictions: {result.successful_predictions}/{result.total_items}")
        
        # Category performance
        if result.category_scores:
            print(f"\nCategory Performance:")
            for category, scores in result.category_scores.items():
                print(f"  {category}: F1={scores['f1']:.3f}, Precision={scores['precision']:.3f}, Recall={scores['recall']:.3f}")
        
        # Cuisine performance  
        if result.cuisine_scores:
            print(f"\nCuisine Performance:")
            for cuisine, scores in result.cuisine_scores.items():
                print(f"  {cuisine}: F1={scores['f1']:.3f}, Precision={scores['precision']:.3f}, Recall={scores['recall']:.3f}")
    
    def print_comparison_report(self, comparison: ComparisonResult):
        """Print model comparison report"""
        print(f"\n{'='*80}")
        print(f"MODEL COMPARISON REPORT")
        print(f"{'='*80}")
        
        print(comparison.detailed_comparison.round(3))
        
        print(f"\nKey Insights:")
        
        if comparison.improvement['accuracy'] > 0:
            print(f"✓ LLM improved accuracy by {comparison.improvement['accuracy']:.3f}")
        else:
            print(f"✗ LLM accuracy decreased by {abs(comparison.improvement['accuracy']):.3f}")
        
        if comparison.improvement['f1_score'] > 0:
            print(f"✓ LLM improved F1-score by {comparison.improvement['f1_score']:.3f}")
        else:
            print(f"✗ LLM F1-score decreased by {abs(comparison.improvement['f1_score']):.3f}")
        
        if comparison.improvement['json_validity_rate'] > 0:
            print(f"✓ LLM improved JSON validity by {comparison.improvement['json_validity_rate']:.3f}")
        else:
            print(f"✗ LLM JSON validity decreased by {abs(comparison.improvement['json_validity_rate']):.3f}")


class BenchmarkRunner:
    """Run comprehensive benchmarks"""
    
    def __init__(self):
        self.evaluator = MenuItemEvaluator()
        self.data_generator = DataGenerator()
    
    def generate_test_data(self, size: int = 100) -> List[Dict[str, Any]]:
        """Generate test data for evaluation"""
        print(f"Generating {size} test items...")
        return self.data_generator.generate_messy_data(size)
    
    def run_full_benchmark(self, test_size: int = 100, save_results: bool = True):
        """Run complete benchmark comparing all models"""
        print("Starting comprehensive benchmark...")
        
        # Generate test data
        test_data = self.generate_test_data(test_size)
        
        # Initialize models
        baseline_model = BaselineClassifier()
        llm_model = get_enricher()  # Will use mock if Ollama not available
        
        # Run comparison
        comparison = self.evaluator.compare_models(baseline_model, llm_model, test_data)
        
        # Print reports
        self.evaluator.print_evaluation_report(comparison.baseline_result)
        self.evaluator.print_evaluation_report(comparison.llm_result)
        self.evaluator.print_comparison_report(comparison)
        
        if save_results:
            # Save results to files
            comparison.detailed_comparison.to_csv('data/evaluation_results.csv', index=False)
            print(f"\nResults saved to data/evaluation_results.csv")
        
        return comparison
    
    def run_ablation_study(self, test_data: List[Dict[str, Any]] = None):
        """Run ablation study on different model components"""
        if test_data is None:
            test_data = self.generate_test_data(50)
        
        print("Running ablation study...")
        
        # Test baseline with different confidence thresholds or rule variations
        # This is a placeholder for more detailed ablation studies
        baseline_model = BaselineClassifier()
        result = self.evaluator.evaluate_model(baseline_model, test_data, "Baseline")
        
        self.evaluator.print_evaluation_report(result)
        
        return result


# Example usage and testing
if __name__ == "__main__":
    # Run benchmark
    benchmark = BenchmarkRunner()
    comparison_result = benchmark.run_full_benchmark(test_size=50)
    
    print("\nBenchmark completed successfully!")