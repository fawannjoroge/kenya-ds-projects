import pandas as pd
import numpy as np
import os

# ── 1. LOAD DATA ──────────────────────────────────────────────
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data', 'kenya_clinic_wait_times.csv')
    df = pd.read_csv(data_path)
    return df


# ── 2. HELPERS ────────────────────────────────────────────────
def print_header():
    print("\n" + "="*50)
    print("     🏥 KENYA CLINIC WAIT TIME ADVISOR")
    print("="*50)

def print_divider():
    print("-"*50)

def get_wait_category(minutes):
    if minutes < 30:
        return "🟢 Short"
    elif minutes < 60:
        return "🟡 Moderate"
    elif minutes < 90:
        return "🟠 Long"
    else:
        return "🔴 Very Long"


# ── 3. OPTION 1 — BEST TIME TO VISIT ─────────────────────────
def best_time_to_visit(df):
    print_divider()
    print("📅 BEST TIME TO VISIT A HOSPITAL")
    print_divider()

    # Show hospitals
    hospitals = sorted(df['hospital'].unique())
    print("Available hospitals:")
    for i, h in enumerate(hospitals, 1):
        print(f"  {i}. {h}")

    print_divider()
    try:
        choice = int(input("Enter hospital number: ").strip())
        hospital = hospitals[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid choice.")
        return

    # Filter for hospital
    hosp_df = df[df['hospital'] == hospital]

    # Best days
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    daily = hosp_df.groupby('day_name')['wait_time_mins'].median().reindex(day_order)

    # Best hours
    hourly = hosp_df.groupby('hour')['wait_time_mins'].median().sort_values()

    print(f"\n📊 {hospital.upper()}")
    print_divider()

    print("⏰ WAIT TIME BY DAY:")
    for day, wait in daily.items():
        bar = '█' * int(wait / 10)
        category = get_wait_category(wait)
        print(f"  {day:<12} {bar:<20} {wait:.0f} mins {category}")

    print(f"\n✅ Best day:    {daily.idxmin()} ({daily.min():.0f} mins median wait)")
    print(f"❌ Worst day:   {daily.idxmax()} ({daily.max():.0f} mins median wait)")

    print(f"\n⏰ TOP 3 BEST HOURS TO VISIT:")
    for hour, wait in hourly.head(3).items():
        print(f"  {hour}:00 — {wait:.0f} mins median wait {get_wait_category(wait)}")

    print(f"\n⚠️  TOP 3 WORST HOURS:")
    for hour, wait in hourly.tail(3).items():
        print(f"  {hour}:00 — {wait:.0f} mins median wait {get_wait_category(wait)}")


# ── 4. OPTION 2 — DEPARTMENT GUIDE ───────────────────────────
def department_guide(df):
    print_divider()
    print("🏨 DEPARTMENT WAIT TIME GUIDE")
    print_divider()

    dept_stats = df.groupby('department')['wait_time_mins'].agg(['median', 'min', 'max'])
    dept_stats = dept_stats.sort_values('median')
    dept_stats.columns = ['median_wait', 'min_wait', 'max_wait']

    for dept, row in dept_stats.iterrows():
        category = get_wait_category(row['median_wait'])
        print(f"\n  {dept}")
        print(f"  Typical wait: {row['median_wait']:.0f} mins {category}")
        print(f"  Range:        {row['min_wait']:.0f} – {row['max_wait']:.0f} mins")

    print_divider()
    print("💡 TIP: Casualty/Emergency is fastest but")
    print("        only visit if it is a genuine emergency.")


# ── 5. OPTION 3 — QUICK RECOMMENDATION ───────────────────────
def quick_recommendation(df):
    print_divider()
    print("⚡ QUICK VISIT RECOMMENDATION")
    print_divider()

    print("What day are you planning to visit?")
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for i, day in enumerate(day_order, 1):
        print(f"  {i}. {day}")

    try:
        day_choice = int(input("\nEnter day number: ").strip())
        day = day_order[day_choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid choice.")
        return

    try:
        hour = int(input("What hour are you planning to visit? (6-19): ").strip())
        if hour < 6 or hour > 19:
            print("❌ Please enter a hour between 6 and 19.")
            return
    except ValueError:
        print("❌ Please enter a valid hour.")
        return

    # Filter for that day and hour
    subset = df[(df['day_name'] == day) & (df['hour'] == hour)]

    if len(subset) == 0:
        print("❌ Not enough data for that combination.")
        return

    median_wait = subset['wait_time_mins'].median()
    category = get_wait_category(median_wait)

    print(f"\n📊 {day} at {hour}:00")
    print_divider()
    print(f"Expected wait:  {median_wait:.0f} mins {category}")

    # Give specific advice
    if median_wait < 30:
        print("✅ Great time to visit — very short wait expected.")
    elif median_wait < 60:
        print("✅ Reasonable time to visit — moderate wait expected.")
    elif median_wait < 90:
        print("⚠️  Consider visiting earlier or later — long wait expected.")
    else:
        print("❌ Avoid this time if possible — very long wait expected.")

    # Suggest better alternative
    day_hourly = df[df['day_name'] == day].groupby('hour')['wait_time_mins'].median()
    best_hour = day_hourly.idxmin()
    best_wait = day_hourly.min()

    if best_hour != hour:
        print(f"\n💡 Better option on {day}: visit at {best_hour}:00")
        print(f"   Expected wait: {best_wait:.0f} mins {get_wait_category(best_wait)}")


# ── 6. MAIN MENU ──────────────────────────────────────────────
def main():
    print("Loading data...")
    df = load_data()
    print("✅ Data loaded.\n")

    while True:
        print_header()
        print("1. Best time to visit a specific hospital")
        print("2. Department wait time guide")
        print("3. Quick visit recommendation (day + hour)")
        print("4. Exit")
        print_divider()

        choice = input("Enter choice (1-4): ").strip()

        if choice == '1':
            best_time_to_visit(df)
        elif choice == '2':
            department_guide(df)
        elif choice == '3':
            quick_recommendation(df)
        elif choice == '4':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Enter 1, 2, 3 or 4.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()