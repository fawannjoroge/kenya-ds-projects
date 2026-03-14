import pandas as pd
import os

# ── LOAD DATA ─────────────────────────────────────────────────
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'kenya_solar_data.csv')
    df = pd.read_csv(data_path)

    # Recreate scores
    df['avg_score'] = (df['avg_radiation'] - df['avg_radiation'].min()) / \
                      (df['avg_radiation'].max() - df['avg_radiation'].min())
    df['variation'] = df['max_radiation'] - df['min_radiation']
    df['consistency_score'] = 1 - ((df['variation'] - df['variation'].min()) / \
                                   (df['variation'].max() - df['variation'].min()))
    df['peak_score'] = (df['max_radiation'] - df['max_radiation'].min()) / \
                       (df['max_radiation'].max() - df['max_radiation'].min())
    df['solar_score'] = (df['avg_score'] * 0.60 +
                         df['consistency_score'] * 0.30 +
                         df['peak_score'] * 0.10) * 100

    def assign_tier(score):
        if score >= 70:
            return 'Tier 1 — High Priority'
        elif score >= 50:
            return 'Tier 2 — Medium Priority'
        else:
            return 'Tier 3 — Low Priority'

    df['priority_tier'] = df['solar_score'].apply(assign_tier)
    return df


# ── HELPERS ───────────────────────────────────────────────────
def print_header():
    print("\n" + "="*52)
    print("     ☀️  KENYA SOLAR POTENTIAL ADVISOR")
    print("="*52)

def print_divider():
    print("-"*52)

def solar_rating(score):
    if score >= 70:
        return "🔴 Excellent"
    elif score >= 50:
        return "🟡 Good"
    else:
        return "🔵 Moderate"


# ── OPTION 1 — COUNTY LOOKUP ──────────────────────────────────
def county_lookup(df):
    print_divider()
    print("🔍 COUNTY SOLAR POTENTIAL LOOKUP")
    print_divider()

    county = input("Enter county name: ").strip().title()

    # Fuzzy match — handle slight misspellings
    matches = df[df['county'].str.contains(county, case=False, na=False)]

    if len(matches) == 0:
        print(f"❌ County '{county}' not found.")
        print("Available counties:")
        for c in sorted(df['county'].values):
            print(f"  • {c}")
        return

    row = matches.iloc[0]

    print(f"\n📊 {row['county'].upper()} — SOLAR REPORT")
    print_divider()
    print(f"Region:             {row['region']}")
    print(f"Solar Score:        {row['solar_score']:.1f}/100 {solar_rating(row['solar_score'])}")
    print(f"Priority Tier:      {row['priority_tier']}")
    print(f"Avg Radiation:      {row['avg_radiation']:.2f} MJ/m²/day")
    print(f"Peak Radiation:     {row['max_radiation']:.2f} MJ/m²/day")
    print(f"Min Radiation:      {row['min_radiation']:.2f} MJ/m²/day")

    # Rank
    rank = df['solar_score'].rank(ascending=False).loc[matches.index[0]]
    print(f"National Rank:      #{int(rank)} out of 47 counties")

    print_divider()
    if row['solar_score'] >= 70:
        print("✅ RECOMMENDATION: High priority for solar deployment.")
        print("   Excellent radiation levels and consistency.")
        print("   Suitable for both household and commercial solar.")
    elif row['solar_score'] >= 50:
        print("✅ RECOMMENDATION: Good candidate for solar deployment.")
        print("   Solid radiation levels with reasonable consistency.")
        print("   Suitable for household solar installations.")
    else:
        print("⚠️  RECOMMENDATION: Lower priority for solar deployment.")
        print("   Consider other energy solutions or hybrid systems.")
        print("   Solar still viable but ROI will be lower.")


# ── OPTION 2 — TOP COUNTIES ───────────────────────────────────
def top_counties(df):
    print_divider()
    print("🏆 TOP COUNTIES FOR SOLAR DEPLOYMENT")
    print_divider()

    try:
        n = int(input("How many top counties to show? (1-47): ").strip())
        if n < 1 or n > 47:
            print("❌ Please enter a number between 1 and 47.")
            return
    except ValueError:
        print("❌ Invalid number.")
        return

    top = df.nlargest(n, 'solar_score')[['county', 'region', 'solar_score', 'priority_tier']]

    print(f"\n☀️  TOP {n} COUNTIES BY SOLAR SCORE")
    print_divider()
    for i, (_, row) in enumerate(top.iterrows(), 1):
        rating = solar_rating(row['solar_score'])
        print(f"{i:>2}. {row['county']:<20} {row['solar_score']:.1f}/100 "
              f"{rating} — {row['region']}")


# ── OPTION 3 — REGION COMPARISON ─────────────────────────────
def region_comparison(df):
    print_divider()
    print("🗺️  SOLAR POTENTIAL BY REGION")
    print_divider()

    regional = df.groupby('region').agg(
        avg_score=('solar_score', 'mean'),
        best_county=('county', lambda x: x.loc[df.loc[x.index, 'solar_score'].idxmax()]),
        county_count=('county', 'count')
    ).round(1).sort_values('avg_score', ascending=False)

    for region, row in regional.iterrows():
        bar = '█' * int(row['avg_score'] / 5)
        print(f"\n{region}")
        print(f"  Avg Score:    {bar} {row['avg_score']:.1f}/100")
        print(f"  Best County:  {row['best_county']}")
        print(f"  Counties:     {int(row['county_count'])}")


# ── OPTION 4 — NGO DEPLOYMENT PLAN ───────────────────────────
def ngo_deployment_plan(df):
    print_divider()
    print("📋 NGO SOLAR DEPLOYMENT PLAN")
    print_divider()

    try:
        budget_units = int(input("How many solar units do you plan to deploy? ").strip())
    except ValueError:
        print("❌ Invalid number.")
        return

    tier1 = df[df['priority_tier'] == 'Tier 1 — High Priority'].sort_values('solar_score', ascending=False)
    tier2 = df[df['priority_tier'] == 'Tier 2 — Medium Priority'].sort_values('solar_score', ascending=False)

    # Allocate 70% to Tier 1, 30% to Tier 2
    tier1_units = int(budget_units * 0.70)
    tier2_units = budget_units - tier1_units

    per_tier1_county = tier1_units // len(tier1)
    per_tier2_county = tier2_units // len(tier2)

    print(f"\n☀️  DEPLOYMENT PLAN FOR {budget_units:,} SOLAR UNITS")
    print_divider()
    print(f"Tier 1 counties get 70% → {tier1_units:,} units")
    print(f"  {per_tier1_county:,} units per county\n")

    for _, row in tier1.iterrows():
        print(f"  ✅ {row['county']:<20} {per_tier1_county:,} units "
              f"(Score: {row['solar_score']:.1f})")

    print(f"\nTier 2 counties get 30% → {tier2_units:,} units")
    print(f"  {per_tier2_county:,} units per county\n")

    for _, row in tier2.iterrows():
        print(f"  🟡 {row['county']:<20} {per_tier2_county:,} units "
              f"(Score: {row['solar_score']:.1f})")

    print_divider()
    print(f"Total counties covered: {len(tier1) + len(tier2)}")
    print(f"Total units deployed:   {budget_units:,}")


# ── MAIN MENU ─────────────────────────────────────────────────
def main():
    print("Loading solar data...")
    df = load_data()
    print("✅ Data loaded.\n")

    while True:
        print_header()
        print("1. Look up a specific county")
        print("2. View top counties for solar deployment")
        print("3. Compare regions")
        print("4. Generate NGO deployment plan")
        print("5. Exit")
        print_divider()

        choice = input("Enter choice (1-5): ").strip()

        if choice == '1':
            county_lookup(df)
        elif choice == '2':
            top_counties(df)
        elif choice == '3':
            region_comparison(df)
        elif choice == '4':
            ngo_deployment_plan(df)
        elif choice == '5':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Enter 1, 2, 3, 4 or 5.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()