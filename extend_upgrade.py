import pandas as pd
import ast

# Load your main CSV
df = pd.read_csv("/Users/agakshita/Desktop/python/tableau_db/synthetic_canva_funnel.csv")

# Parse the plan history column
def expand_plan_history(row):
    try:
        steps = ast.literal_eval(row['plan_upgrade_history'])
        return pd.DataFrame([{
            'user_id': row.user_id,  
            'step_num': i + 1,
            'from_plan': step['from'],
            'to_plan': step['to'],
            'upgrade_date': step['date']
        } for i, step in enumerate(steps)])
    except:
        return pd.DataFrame()

all_steps = pd.concat([expand_plan_history(row) for _, row in df.iterrows()], ignore_index=True)

all_steps['upgrade_date'] = pd.to_datetime(all_steps['upgrade_date'])
all_steps['next_upgrade_date'] = all_steps.groupby('user_id')['upgrade_date'].shift(-1)
all_steps['days_to_next'] = (all_steps['next_upgrade_date'] - all_steps['upgrade_date']).dt.days

all_steps.to_csv("upgrade_steps_expanded.csv", index=False)
