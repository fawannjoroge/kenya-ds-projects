#import libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed so we get the same data every time we run
np.random.seed(42)
random.seed(42)

# ── CONFIGURATION ─────────────────────────────────────────────

HOSPITALS = {
    'Kenyatta National Hospital': 'Nairobi',
    'Pumwani Maternity Hospital': 'Nairobi',
    'Mama Lucy Kibaki Hospital': 'Nairobi',
    'Moi Teaching & Referral Hospital': 'Eldoret',
    'Coast General Hospital': 'Mombasa'
}

DEPARTMENTS = [
    'Outpatient',
    'Maternity',
    'Casualty/Emergency',
    'Pediatrics',
    'General Surgery'
]

# Real Kenyan patterns:
# Mondays are busiest — people hold off over weekend
# Fridays are second busiest
# Wednesday is quietest
DAY_WEIGHTS = {
    0: 2.0,   # Monday — very busy
    1: 1.4,   # Tuesday
    2: 1.0,   # Wednesday — quietest
    3: 1.2,   # Thursday
    4: 1.6,   # Friday — busy before weekend
    5: 0.6,   # Saturday — reduced services
    6: 0.3,   # Sunday — emergency only
}

# Peak hours: 8-10am (morning rush), 1-2pm (lunch rush)
# Quiet hours: early morning, late afternoon
HOUR_WEIGHTS = {
    6:  0.3,
    7:  0.8,
    8:  2.0,   # morning rush
    9:  2.5,   # peak
    10: 2.2,
    11: 1.8,
    12: 1.5,
    13: 1.8,   # lunch rush
    14: 1.6,
    15: 1.3,
    16: 1.0,
    17: 0.7,
    18: 0.4,
    19: 0.3,
}

# Wait times by department (minutes) — based on real patterns
# (min_wait, max_wait, avg_wait)
DEPT_WAIT_TIMES = {
    'Outpatient':           (20, 240, 90),
    'Maternity':            (10, 180, 60),
    'Casualty/Emergency':   (5,  120, 35),
    'Pediatrics':           (15, 200, 75),
    'General Surgery':      (30, 300, 120),
}


# ── DATA GENERATION ───────────────────────────────────────────

def generate_wait_time(department, day_of_week, hour):
    min_w, max_w, avg_w = DEPT_WAIT_TIMES[department]
    
    # Base wait time using normal distribution around average
    base = np.random.normal(avg_w, avg_w * 0.3)
    
    # Multiply by day and hour pressure
    day_factor = DAY_WEIGHTS[day_of_week]
    hour_factor = HOUR_WEIGHTS.get(hour, 0.5)
    
    wait = base * day_factor * hour_factor * 0.6
    
    # Clip to realistic bounds
    return int(np.clip(wait, min_w, max_w))


def generate_dataset(n_records=5000):
    records = []
    
    # Generate records across 2 years
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    
    for _ in range(n_records):
        # Random date
        random_days = random.randint(0, date_range)
        visit_date = start_date + timedelta(days=random_days)
        
        # Random hour (6am to 7pm)
        hour = random.choices(
            list(HOUR_WEIGHTS.keys()),
            weights=list(HOUR_WEIGHTS.values())
        )[0]
        
        # Random hospital and department
        hospital = random.choice(list(HOSPITALS.keys()))
        department = random.choice(DEPARTMENTS)
        
        # Generate wait time based on patterns
        day_of_week = visit_date.weekday()
        wait_time = generate_wait_time(department, day_of_week, hour)
        
        # Patient satisfaction (inversely related to wait time)
        if wait_time < 30:
            satisfaction = random.randint(4, 5)
        elif wait_time < 60:
            satisfaction = random.randint(3, 5)
        elif wait_time < 120:
            satisfaction = random.randint(2, 4)
        else:
            satisfaction = random.randint(1, 3)
        
        records.append({
            'date': visit_date.strftime('%Y-%m-%d'),
            'hour': hour,
            'day_of_week': day_of_week,
            'day_name': visit_date.strftime('%A'),
            'month': visit_date.month,
            'hospital': hospital,
            'county': HOSPITALS[hospital],
            'department': department,
            'wait_time_mins': wait_time,
            'satisfaction_score': satisfaction,
            'is_weekend': 1 if day_of_week >= 5 else 0
        })
    
    return pd.DataFrame(records)


# ── RUN ───────────────────────────────────────────────────────

print("Generating dataset...")
df = generate_dataset(5000)

# Save to data folder
df.to_csv('data/kenya_clinic_wait_times.csv', index=False)

print(f"✅ Dataset generated successfully")
print(f"   Records: {len(df):,}")
print(f"   Columns: {list(df.columns)}")
print(f"\nFirst 5 rows:")
print(df.head())