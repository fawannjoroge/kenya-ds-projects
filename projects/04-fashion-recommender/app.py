import pandas as pd
import joblib
import os

# ── LOAD MODELS AND ENCODERS ──────────────────────────────────
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load models — write the 3 joblib.load() lines yourself
model1 = joblib.load(os.path.join(base_dir, 'data', 'cloth_fitting_recommender.pkl'))
model2 = joblib.load(os.path.join(base_dir, 'data', 'clothing_colours_recommender.pkl'))
model3 = joblib.load(os.path.join(base_dir, 'data', 'clothing_color_wheel_recommender.pkl'))

# Load encoders — write all 6 joblib.load() lines yourself
le_skin = joblib.load(os.path.join(base_dir, 'data', 'le_skin.pkl'))
le_undertone = joblib.load(os.path.join(base_dir, 'data', 'le_undertone.pkl'))
le_body = joblib.load(os.path.join(base_dir, 'data', 'le_body.pkl'))
le_fitting = joblib.load(os.path.join(base_dir, 'data', 'le_fitting.pkl'))
le_colors = joblib.load(os.path.join(base_dir, 'data', 'le_colors.pkl'))
le_wheel = joblib.load(os.path.join(base_dir, 'data', 'le_wheel.pkl'))


# ── HELPERS ───────────────────────────────────────────────────
def print_header():
    print("\n" + "="*52)
    print("     👗 KENYAN FASHION RECOMMENDER")
    print("="*52)

def print_divider():
    print("-"*52)


# ── GET RECOMMENDATION ────────────────────────────────────────
def get_recommendation():
    print_divider()
    print("Enter your details to get personalized recommendations")
    print_divider()

    # Show valid options
    print(f"Skin Tones: {list(le_skin.classes_)}")
    skin_tone = input("\nEnter your skin tone: ").strip().title()

    print(f"\nUndertones: {list(le_undertone.classes_)}")
    undertone = input("Enter your undertone (Warm/Cool/Neutral): ").strip().title()

    print(f"\nBody Types: {list(le_body.classes_)}")
    body_type = input("Enter your body type: ").strip().title()

    # Validate inputs
    if skin_tone not in le_skin.classes_:
        print(f"❌ Invalid skin tone.")
        return
    if undertone not in le_undertone.classes_:
        print(f"❌ Invalid undertone.")
        return
    if body_type not in le_body.classes_:
        print(f"❌ Invalid body type.")
        return

    # Encode inputs
    # Write these 3 lines yourself using le_skin, le_body, le_undertone
    skin_encoded = le_skin.transform([skin_tone])[0]
    body_encoded = le_body.transform([body_type])[0]
    undertone_encoded = le_undertone.transform([undertone])[0]

    # Make predictions
    
    fitting_pred = model1.predict([[skin_encoded, body_encoded]])[0]
    colors_pred = model2.predict([[skin_encoded, body_encoded, undertone_encoded]])[0]
    wheel_pred = model3.predict([[skin_encoded, body_encoded, undertone_encoded]])[0]

    # Decode predictions back to text
   
    fitting_style = le_fitting.inverse_transform([fitting_pred])[0]
    colors = le_colors.inverse_transform([colors_pred])[0]
    wheel_region = le_wheel.inverse_transform([wheel_pred])[0]

    # Display results
    print(f"\n✨ FASHION RECOMMENDATIONS FOR YOU")
    print_divider()
    print(f"Skin Tone:      {skin_tone}")
    print(f"Undertone:      {undertone}")
    print(f"Body Type:      {body_type}")
    print_divider()
    print(f"👗 Fitting Style:     {fitting_style}")
    print(f"🎨 Clothing Colors:   {colors}")
    print(f"🌈 Color Palette:     {wheel_region}")


# ── MAIN MENU ─────────────────────────────────────────────────
def main():
    while True:
        print_header()
        print("1. Get fashion recommendation")
        print("2. View all skin tone options")
        print("3. Exit")
        print_divider()

        choice = input("Enter choice (1-3): ").strip()

        if choice == '1':
            get_recommendation()
        elif choice == '2':
            print_divider()
            print("VALID OPTIONS")
            print_divider()
            # Print all valid options for skin tone, undertone and body type
            print(f"Skin Tones: {list(le_skin.classes_)}")
            print(f"Undertones: {list(le_undertone.classes_)}")
            print(f"Body Types: {list(le_body.classes_)}")
            print(f"Fitting Styles: {list(le_fitting.classes_)}")
            print(f"Color Options: {list(le_colors.classes_)}")
            print(f"Color Palettes: {list(le_wheel.classes_)}") 

        elif choice == '3':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid choice.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()