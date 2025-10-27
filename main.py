import argparse
import os
import sys

def run_scraping(city):
    print("\n" + "="*60)
    print("STEP 1: Scraping restaurant data from Google Maps")
    print("="*60)
    print(f"City: {city}")
    print("\nNOTE: This step requires manual execution of cuisine.py")
    print("Please run: python cuisine.py")
    print("(The script uses Selenium and needs manual setup)")
    print("="*60)

def run_processing():
    print("\n" + "="*60)
    print("STEP 2: Processing restaurant data")
    print("="*60)

    if not os.path.exists('restaurants_data.csv'):
        print("ERROR: restaurants_data.csv not found!")
        print("Please run cuisine.py first to scrape restaurant data.")
        return False

    from process_data import process_restaurant_data
    try:
        process_restaurant_data()
        print("Data processing complete!")
        return True
    except Exception as e:
        print(f"ERROR during processing: {e}")
        return False

def run_visualization():
    print("\n" + "="*60)
    print("STEP 3: Creating map visualization")
    print("="*60)

    if not os.path.exists('cuisine_by_zipcode.csv'):
        print("ERROR: cuisine_by_zipcode.csv not found!")
        print("Please run processing step first.")
        return False

    from visualize_map import create_map
    try:
        create_map()
        print("Visualization complete!")
        return True
    except Exception as e:
        print(f"ERROR during visualization: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Cuisine Map Pipeline - Scrape, process, and visualize restaurant cuisines by zipcode'
    )
    parser.add_argument(
        '--city',
        type=str,
        default='Mountain View, CA',
        help='City to analyze (default: Mountain View, CA)'
    )
    parser.add_argument(
        '--skip-scraping',
        action='store_true',
        help='Skip the scraping step (use existing data)'
    )
    parser.add_argument(
        '--process-only',
        action='store_true',
        help='Only run the data processing step'
    )
    parser.add_argument(
        '--visualize-only',
        action='store_true',
        help='Only run the visualization step'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("CUISINE MAP PIPELINE")
    print("="*60)

    if args.process_only:
        success = run_processing()
        sys.exit(0 if success else 1)

    if args.visualize_only:
        success = run_visualization()
        sys.exit(0 if success else 1)

    if not args.skip_scraping:
        run_scraping(args.city)
        print("\nAfter running cuisine.py, re-run this script with --skip-scraping")
        sys.exit(0)

    if not run_processing():
        sys.exit(1)

    if not run_visualization():
        sys.exit(1)

    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - restaurants_data.csv (raw data)")
    print("  - cuisine_by_zipcode.csv (processed data)")
    print("  - zipcode_coordinates.csv (coordinates)")
    print("  - cuisine_map.html (interactive map)")
    print("\nOpen cuisine_map.html in your browser to view the map!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
