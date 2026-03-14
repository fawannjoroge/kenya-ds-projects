import requests
import pandas as pd
import time
import json
from data.kenya_counties import KENYA_COUNTIES

def fetch_solar_data(latitude, longitude, county_name):
    """
    Fetch solar irradiance data from Open-Meteo API
    for a given latitude and longitude
    """
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "daily": "shortwave_radiation_sum",
        "timezone": "Africa/Nairobi"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Extract daily radiation values
            daily_radiation = data['daily']['shortwave_radiation_sum']
            
            # Calculate annual statistics
            avg_radiation = sum(r for r in daily_radiation if r is not None) / len([r for r in daily_radiation if r is not None])
            max_radiation = max(r for r in daily_radiation if r is not None)
            min_radiation = min(r for r in daily_radiation if r is not None)
            
            print(f"✅ {county_name}: {avg_radiation:.2f} MJ/m²/day")
            
            return {
                "avg_radiation": round(avg_radiation, 3),
                "max_radiation": round(max_radiation, 3),
                "min_radiation": round(min_radiation, 3),
                "data_points": len([r for r in daily_radiation if r is not None])
            }
        else:
            print(f"❌ {county_name}: API error {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏱️  {county_name}: Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🔌 {county_name}: Connection error")
        return None
    except Exception as e:
        print(f"❌ {county_name}: Unexpected error — {e}")
        return None


def fetch_all_counties():
    """Fetch solar data for all 47 Kenyan counties"""
    
    results = []
    total = len(KENYA_COUNTIES)
    
    print(f"Fetching solar data for {total} Kenyan counties...")
    print("This will take about 2-3 minutes — the API has rate limits\n")
    
    for i, county in enumerate(KENYA_COUNTIES, 1):
        print(f"[{i}/{total}] Fetching {county['county']}...")
        
        solar_data = fetch_solar_data(
            county['latitude'],
            county['longitude'],
            county['county']
        )
        
        if solar_data:
            results.append({
                "county": county['county'],
                "region": county['region'],
                "latitude": county['latitude'],
                "longitude": county['longitude'],
                **solar_data  # unpack the solar statistics
            })
        
        # Wait 1 second between requests — be respectful of the API
        time.sleep(1)
    
    return pd.DataFrame(results)


# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    df = fetch_all_counties()
    
    # Save to CSV
    df.to_csv('data/kenya_solar_data.csv', index=False)
    
    print(f"\n✅ Done! Fetched data for {len(df)} counties")
    print(f"Saved to data/kenya_solar_data.csv")
    print(f"\nFirst 5 rows:")
    print(df.head())