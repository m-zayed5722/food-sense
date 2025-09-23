import sys
sys.path.append('.')
from src.evaluation import BenchmarkRunner

def main():
    print("Running evaluation benchmark...")
    
    # Run benchmark
    benchmark = BenchmarkRunner()
    comparison_result = benchmark.run_full_benchmark(test_size=50)
    
    print("\nBenchmark completed successfully!")
    print(f"Overall improvement in F1-score: {comparison_result.improvement['f1_score']:.3f}")

if __name__ == "__main__":
    main()