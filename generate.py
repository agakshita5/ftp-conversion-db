import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

plans = ["Free", "Pro", "Teams", "Enterprise"]
def generate_plan_history(signup_date, upgrade_chance=0.5):
    if random.random() > upgrade_chance:
        # Stay Free, no upgrades
        return "Free", [], "Free"

    # If upgrading, choose how far they go (from Pro to Enterprise)
    final_plan_index = random.randint(1, len(plans) - 1)
    plan_upgrade_history = []
    current_date = signup_date

    for i in range(1, final_plan_index + 1):
        current_date += timedelta(days=random.randint(10, 30))
        plan_upgrade_history.append({
            "from": plans[i - 1],
            "to": plans[i],
            "date": current_date.strftime("%Y-%m-%d")
        })

    return "Free", plan_upgrade_history, plans[final_plan_index] # 3 fields

def generate_user_data(n=1000):
    data = []
    for _ in range(n):
        signup_date = fake.date_between(start_date='-365d', end_date='today') # 4
        gender = random.choice(["Male", "Female"]) # 5
        if gender == "Male":
            first_name = fake.first_name_male()
        elif gender == "Female":
            first_name = fake.first_name_female() # 6
        last_name = fake.last_name() # 7
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}" # 8
        country = random.choice(['US', 'India', 'UK', 'Germany', 'Brazil']) # 9
        device = random.choice(['Desktop', 'Mobile', 'Tablet']) # 10
        source = random.choice(['Organic', 'Referral', 'Google Ads', 'Instagram Ads', 'Youtube Ads', 'Facebook Ads']) # 11

        # Funnel logic
        is_activated = random.random() < 0.85 # 12
        activation_date = signup_date + timedelta(days=random.randint(0, 5)) if is_activated else None # 13
        is_pro_feature_tried = is_activated and random.random() < 0.6 # 14
        is_trial_started = is_pro_feature_tried and random.random() < 0.5 # 15
        trial_start_date = activation_date + timedelta(days=random.randint(1, 7))if is_trial_started else None # 16
    
        conversion_features = [
            "Brand Kit", "Background Remover", "Video Editor", 
            "Content Scheduler", "Magic Resize", "Premium Templates"
        ]
        initial_plan, upgrade_history, final_plan = generate_plan_history(signup_date, upgrade_chance=0.5) 
        monthly_revenue = { # 17
                "Free": 0,
                "Pro": 29.99,
                "Teams": 59.99,
                "Enterprise": 149.99
            }[final_plan] 
        converted_date = None
        if upgrade_history:
            first_upgrade = upgrade_history[0]
            if first_upgrade["from"] == "Free":
                converted_date = datetime.strptime(first_upgrade["date"], "%Y-%m-%d") # 18
        is_converted = bool(upgrade_history) # 19
        trigger_feature = random.choice(conversion_features) if is_converted else None # 20
        
        data.append({
            "user_id": fake.uuid4(), # 21
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "email": email,
            "signup_date": signup_date,
            "country": country,
            "device": device,
            "source": source,
            "activated": is_activated,
            "activation_date": activation_date,
            "pro_feature_tried": is_pro_feature_tried,
            "trial_started": is_trial_started,
            "trial_start_date": trial_start_date,
            "converted": is_converted,
            "converted_date": converted_date,
            "trigger_ft": trigger_feature,
            "plan_type": initial_plan,
            "plan_upgrade_history": upgrade_history,
            "final_plan": final_plan,
            "monthly_revenue": monthly_revenue
        })

    return pd.DataFrame(data)

df = generate_user_data()

def extract_upgrade_info(row):
    upgrades = row['plan_upgrade_history']
    upgrade_count = len(upgrades)
    
    upgraded_from_free = any(u['from'] == 'Free' for u in upgrades)
    upgraded_from_pro = any(u['from'] == 'Pro' for u in upgrades)
    upgraded_from_teams = any(u['from'] == 'Teams' for u in upgrades)
    
    upgrade_path = " → ".join([f"{u['from']}→{u['to']}" for u in upgrades])
    
    direct_free_to_teams = any(u['from'] == 'Free' and u['to'] == 'Teams' for u in upgrades)
    direct_free_to_enterprise = any(u['from'] == 'Free' and u['to'] == 'Enterprise' for u in upgrades)
    direct_pro_to_enterprise = any(u['from'] == 'Pro' and u['to'] == 'Enterprise' for u in upgrades)

    return pd.Series({
        "total_upgrades": upgrade_count,
        "upgraded_from_free": upgraded_from_free,
        "upgraded_from_pro": upgraded_from_pro,
        "upgraded_from_teams": upgraded_from_teams,
        "upgrade_path": upgrade_path,
        "direct_free_to_teams": direct_free_to_teams,
        "direct_free_to_ep": direct_free_to_enterprise,
        "direct_pro_to_ep": direct_pro_to_enterprise
    })

upgrade_features = df.apply(extract_upgrade_info, axis=1)
df = pd.concat([df, upgrade_features], axis=1)

df.to_csv("/Users/agakshita/Desktop/python/tableau_db/synthetic_canva_funnel.csv", index=False)
