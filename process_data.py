import pandas as pd
import re
from collections import Counter
from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent="cuisine_mapper")

def extract_zipcode(address, city="Mountain View, CA"):
    if pd.isna(address):
        return None

    # first try to find zipcode in address
    zipcode_pattern = r'\b(\d{5})(?:-\d{4})?\b'
    match = re.search(zipcode_pattern, str(address))
    if match:
        return match.group(1)

    # if no zipcode, try geocoding the full address
    try:
        full_address = f"{address}, {city}"
        location = geolocator.geocode(full_address, timeout=10)
        time.sleep(1)  # rate limiting

        if location and location.raw.get('address'):
            postal_code = location.raw['address'].get('postcode')
            if postal_code:
                # extract just the 5 digit zipcode
                match = re.search(r'\b(\d{5})', postal_code)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"  Geocoding failed for {address}: {e}")
        return None

    return None

def process_restaurant_data(input_csv='restaurants_data.csv', output_csv='cuisine_by_zipcode.csv'):
    print(f"Reading data from {input_csv}...")
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} restaurants")

    # get zipcodes
    print("Extracting zipcodes from addresses...")
    df['Zipcode'] = df['Address'].apply(extract_zipcode)

    df_with_zip = df[df['Zipcode'].notna()].copy()
    print(f"Found {len(df_with_zip)} restaurants with valid zipcodes")
    print(f"Unique zipcodes: {df_with_zip['Zipcode'].nunique()}")

    # find most common cuisine per zipcode
    print("Finding most common cuisine per zipcode...")
    results = []

    for zipcode, group in df_with_zip.groupby('Zipcode'):
        cuisine_counts = Counter(group['Cuisine'])
        most_common_cuisine, count = cuisine_counts.most_common(1)[0]
        total_restaurants = len(group)

        results.append({
            'Zipcode': zipcode,
            'Most_Common_Cuisine': most_common_cuisine,
            'Count': count,
            'Total_Restaurants': total_restaurants,
            'Percentage': round((count / total_restaurants) * 100, 2)
        })

    if not results:
        print("ERROR: No restaurants with zipcodes found!")
        print("Could not create cuisine_by_zipcode.csv")
        return None

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Total_Restaurants', ascending=False)

    results_df.to_csv(output_csv, index=False)
    print(f"\nResults saved to {output_csv}")

    print("\n=== Summary ===")
    print(results_df.to_string(index=False))

    return results_df

if __name__ == "__main__":
    results_df = process_restaurant_data()
    if results_df is not None and len(results_df) > 0:
        print(f"\nProcessed {len(results_df)} zipcodes")
        print("Ready for visualization!")
