from pathlib import Path
from dotenv import load_dotenv
import os
import pandas as pd

# Load .env if present
load_dotenv(dotenv_path=Path("config/.env"))

def load_data(default_path="data/sample.csv"):
    """
    Loads dataset from DATA_PATH in .env, 
    or falls back to sample.csv if not set.
    Works on Mac, Linux, and Windows.
    """
    # Get the project root directory (where this file is located)
    project_root = Path(__file__).parent.parent
    
    # If DATA_PATH is set, use it; otherwise use the default path relative to project root
    if os.getenv("DATA_PATH"):
        data_path = Path(os.getenv("DATA_PATH"))
    else:
        data_path = project_root / default_path
    
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    
    print(f"Loading data from: {data_path}")
    return pd.read_csv(data_path)
