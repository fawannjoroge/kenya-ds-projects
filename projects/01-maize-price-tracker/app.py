import pandas as pd
import matplotlib.pyplot as plt
import os

# ── 1. LOAD & CLEAN DATA ──────────────────────────────────────
def load_data():
    # Get the path to the data file relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'wfp_food_prices_ken.csv')
    
    df = pd.read_csv(data_path)
    
    # Filter for retail maize only
    maize_types = ['Maize', 'Maize (white)', 'Maize (white, dry)']
    df = df[df['commodity'].isin(maize_types) & (df['pricetype'] == 'Retail')]
    
    # Drop missing counties
    df = df.dropna(subset=['admin1'])
    
    # Remove outliers
    df = df[df['price'] >= 10]
    
    # Fix date
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Month names
    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                   7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    df['month_name'] = df['month'].map(month_names)
    
    return df


# ── 2. HELPER ─────────────────────────────────────────────────
def print_header():
    print("\n" + "="*45)
    print("      🌽 KENYA MAIZE PRICE TRACKER")
    print("="*45)

def print_divider():
    print("-"*45)


# ── 3. OPTION 1 — NATIONAL TREND ──────────────────────────────
def show_national_trend(df):
    print_divider()
    print("📈 NATIONAL PRICE TREND (2006–2025)")
    print_divider()
    
    yearly = df.groupby('year')['price'].mean()
    
    for year, price in yearly.items():
        # Create a simple text bar chart
        bar = '█' * int(price / 3)
        print(f"{year}  {bar} {price:.1f} KES/kg")
    
    print_divider()
    print(f"Lowest year:   {yearly.idxmin()} ({yearly.min():.1f} KES/kg)")
    print(f"Highest year:  {yearly.idxmax()} ({yearly.max():.1f} KES/kg)")
    print(f"Overall avg:   {yearly.mean():.1f} KES/kg")


# ── 4. OPTION 2 — COMPARE REGIONS ─────────────────────────────
def compare_regions(df):
    print_divider()
    print("🗺️  REGIONAL PRICE COMPARISON")
    print_divider()
    
    regional = df.groupby('admin1')['price'].mean().sort_values(ascending=False)
    
    for region, price in regional.items():
        bar = '█' * int(price / 3)
        print(f"{region:<15} {bar} {price:.1f} KES/kg")
    
    print_divider()
    print(f"Most expensive: {regional.idxmax()} ({regional.max():.1f} KES/kg)")
    print(f"Cheapest:       {regional.idxmin()} ({regional.min():.1f} KES/kg)")


# ── 5. OPTION 3 — BEST TIME TO SELL ───────────────────────────
def best_time_to_sell(df):
    print_divider()
    print("📅 BEST TIME TO SELL BY REGION")
    print_divider()
    
    # Show available regions
    regions = df['admin1'].unique()
    print("Available regions:")
    for r in sorted(regions):
        print(f"  • {r}")
    
    print_divider()
    region = input("Enter region name exactly as shown above: ").strip()
    
    # Validate input
    if region not in regions:
        print(f"❌ Region '{region}' not found. Please check the spelling.")
        return
    
    # Filter for that region
    region_df = df[df['admin1'] == region]
    
    # Monthly averages for that region
    monthly = region_df.groupby('month_name')['price'].mean()
    
    # Sort by price
    month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']
    monthly = monthly.reindex(month_order).dropna()
    monthly_sorted = monthly.sort_values(ascending=False)
    
    # Best and worst months
    best_months = monthly_sorted.head(3)
    worst_months = monthly_sorted.tail(3)
    
    print(f"\n📊 {region.upper()} — SELLING GUIDE")
    print_divider()
    print("✅ BEST months to sell (highest prices):")
    for month, price in best_months.items():
        print(f"   {month}: {price:.1f} KES/kg")
    
    print("\n❌ WORST months to sell (lowest prices):")
    for month, price in worst_months.items():
        print(f"   {month}: {price:.1f} KES/kg")
    
    # Calculate premium
    premium = ((best_months.mean() - worst_months.mean()) / worst_months.mean()) * 100
    
    print_divider()
    print(f"💡 Selling in your best months vs worst months")
    print(f"   gives you ~{premium:.0f}% more per kg")
    print(f"   Avg best price:  {best_months.mean():.1f} KES/kg")
    print(f"   Avg worst price: {worst_months.mean():.1f} KES/kg")


# ── 6. MAIN MENU ───────────────────────────────────────────────
def main():
    # Load data once at startup
    print("Loading data...")
    df = load_data()
    print("✅ Data loaded successfully.\n")
    
    while True:
        print_header()
        print("1. View national price trend")
        print("2. Compare regions")
        print("3. Best time to sell by region")
        print("4. Exit")
        print_divider()
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            show_national_trend(df)
        elif choice == '2':
            compare_regions(df)
        elif choice == '3':
            best_time_to_sell(df)
        elif choice == '4':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3 or 4.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()