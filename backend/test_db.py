import pandas as pd
from database import engine

def check_columns():
    try:
        # Fetch just one row to see the columns
        df = pd.read_sql("SELECT * FROM matches LIMIT 1", engine)
        
        # Check if new columns exist
        new_cols = ['hst', 'ast', 'hc', 'ac']
        found = [col for col in new_cols if col in df.columns]
        
        if len(found) == 4:
            print("✅ SUCCESS! The new columns (hst, ast, hc, ac) are in the database.")
            print(f"Columns found: {df.columns.tolist()}")
        else:
            print(f"❌ FAIL. Only found these: {found}")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    check_columns()