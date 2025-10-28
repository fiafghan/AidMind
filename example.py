"""
AidMind Example Usage
=====================

This script demonstrates various ways to use AidMind for humanitarian needs assessment.
"""

from aidmind import analyze_needs
import pandas as pd


def example_basic():
    """Example 1: Basic usage with minimal parameters"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    output_path = analyze_needs(
        dataset_path="afghanistan_needs_200.csv",
        country_name="Afghanistan"
    )
    
    print(f"\n✅ Map generated: {output_path}")
    
    # Load and display results
    csv_path = output_path.replace("needs_map", "needs_scores").replace(".html", ".csv")
    df = pd.read_csv(csv_path)
    print(f"\n📊 Results preview:")
    print(df.head(10))
    print(f"\nNeed levels distribution:")
    print(df["need_level"].value_counts())


def example_custom_column():
    """Example 2: Specify custom admin column name"""
    print("\n" + "=" * 60)
    print("Example 2: Custom Admin Column")
    print("=" * 60)
    
    output_path = analyze_needs(
        dataset_path="afghanistan_needs_200.csv",
        country_name="Afghanistan",
        admin_col="province",  # Explicitly specify column name
    )
    
    print(f"\n✅ Map generated: {output_path}")


def example_fixed_thresholds():
    """Example 3: Use fixed thresholds for cross-country comparison"""
    print("\n" + "=" * 60)
    print("Example 3: Fixed Thresholds")
    print("=" * 60)
    
    # Use consistent cutoffs across countries
    output_path = analyze_needs(
        dataset_path="afghanistan_needs_200.csv",
        country_name="Afghanistan",
        fixed_thresholds=(0.25, 0.50, 0.75),  # Fixed quartiles
        output_html_path="output/afghanistan_fixed.html"
    )
    
    print(f"\n✅ Map with fixed thresholds: {output_path}")


def example_error_handling():
    """Example 4: Proper error handling"""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    try:
        output_path = analyze_needs(
            dataset_path="nonexistent_file.csv",
            country_name="Afghanistan"
        )
    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
    except ValueError as e:
        print(f"❌ Data error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("\n🚀 AidMind Examples\n")
    
    # Run examples
    example_basic()
    example_custom_column()
    example_fixed_thresholds()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
