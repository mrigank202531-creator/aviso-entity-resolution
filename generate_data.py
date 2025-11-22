import pandas as pd
from faker import Faker
import random

fake = Faker()

def generate_data(num_records=100):
    print("Generating synthetic CRM data...")
    # 1. Generate CLEAN CRM Data
    crm_data = []
    for _ in range(num_records):
        crm_data.append({
            "crm_id": fake.uuid4(),
            "name": fake.name(),
            "company": fake.company(),
            "email": fake.company_email(),
            "role": fake.job()
        })
    df_crm = pd.DataFrame(crm_data)
    
    # 2. Generate MESSY Lead Data
    messy_data = []
    for idx, row in df_crm.sample(frac=0.5).iterrows():
        # Introduce noise
        messy_name = row['name'].lower() if random.random() > 0.5 else row['name']
        messy_company = row['company'].split(' ')[0]
        
        messy_data.append({
            "raw_text": f"{messy_name} working at {messy_company}",
            "true_id": row['crm_id']
        })
    
    df_messy = pd.DataFrame(messy_data)
    
    # Save to CSV
    df_crm.to_csv("crm_database.csv", index=False)
    df_messy.to_csv("messy_leads.csv", index=False)
    print(f"✅ Success: Generated {len(df_crm)} CRM records.")

if __name__ == "__main__":
    generate_data()