import pandas as pd
import folium
import pgeocode

def get_zipcode_coords(zipcode, country='US'):
    nomi = pgeocode.Nominatim(country)
    location = nomi.query_postal_code(zipcode)

    if pd.notna(location.latitude) and pd.notna(location.longitude):
        return location.latitude, location.longitude
    return None, None

def create_map(input_csv='cuisine_by_zipcode.csv', output_html='cuisine_map.html'):
    print(f"Reading data from {input_csv}...")
    df = pd.read_csv(input_csv)
    print(f"Loaded data for {len(df)} zipcodes")

    # get lat/long for zipcodes
    print("Getting coordinates for zipcodes...")
    coords = []
    for i, row in df.iterrows():
        lat, lon = get_zipcode_coords(row['Zipcode'])
        coords.append({'lat': lat, 'lon': lon})
        if lat is not None:
            print(f"  {row['Zipcode']}: ({lat:.4f}, {lon:.4f})")

    df['Latitude'] = [c['lat'] for c in coords]
    df['Longitude'] = [c['lon'] for c in coords]

    df_mapped = df[df['Latitude'].notna()].copy()
    print(f"\nSuccessfully mapped {len(df_mapped)} out of {len(df)} zipcodes")

    if len(df_mapped) == 0:
        print("ERROR: No zipcodes could be mapped to coordinates!")
        return

    center_lat = df_mapped['Latitude'].mean()
    center_lon = df_mapped['Longitude'].mean()

    print(f"\nCreating map centered at ({center_lat:.4f}, {center_lon:.4f})...")
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap'
    )

    cuisine_colors = {}
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
              'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
              'darkpurple', 'pink', 'lightblue', 'lightgreen', 'gray']

    for i, row in df_mapped.iterrows():
        cuisine = row['Most_Common_Cuisine']

        if cuisine not in cuisine_colors:
            color_idx = len(cuisine_colors) % len(colors)
            cuisine_colors[cuisine] = colors[color_idx]

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">Zipcode: {row['Zipcode']}</h4>
            <hr style="margin: 5px 0;">
            <p style="margin: 5px 0;"><strong>Most Common Cuisine:</strong><br>
            <span style="font-size: 16px; color: {cuisine_colors[cuisine]};">
            {cuisine}</span></p>
            <p style="margin: 5px 0;"><strong>Count:</strong> {row['Count']} out of {row['Total_Restaurants']} ({row['Percentage']}%)</p>
        </div>
        """

        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8 + (row['Total_Restaurants'] / 2),
            popup=folium.Popup(popup_html, max_width=300),
            color=cuisine_colors[cuisine],
            fill=True,
            fillColor=cuisine_colors[cuisine],
            fillOpacity=0.7,
            weight=2
        ).add_to(m)

    # add legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                border:2px solid grey; z-index:9999;
                background-color:white;
                padding: 10px;
                font-size:14px;
                ">
    <h4 style="margin-top:0;">Cuisine Types</h4>
    '''

    for cuisine, color in sorted(cuisine_colors.items()):
        legend_html += f'''
        <p style="margin: 5px 0;">
            <i class="fa fa-circle" style="color:{color}"></i> {cuisine}
        </p>
        '''

    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(output_html)
    print(f"\nMap saved to {output_html}")
    print(f"Open {output_html} in a web browser to view the map!")

    # save coord data
    coords_csv = 'zipcode_coordinates.csv'
    df_mapped.to_csv(coords_csv, index=False)
    print(f"Coordinate data saved to {coords_csv}")

    return m

if __name__ == "__main__":
    # Create the map
    create_map()
