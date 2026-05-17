"""One-off script to drop the unused user_predictions table."""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS user_predictions"))
    conn.commit()
    print("Dropped user_predictions table (or it did not exist).")
