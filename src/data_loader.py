from pathlib import Path
from dotenv import load_dotenv
import os
import pandas as pd
from typing import Optional

# Load .env if present
load_dotenv(dotenv_path=Path("config/.env"))

def load_data(default_path="data/sample.csv", filename: Optional[str] = None, fmt: Optional[str] = None, **read_kwargs):
    """
    Load dataset with flexible resolution and format support.

    Resolution priority:
    1) DATA_PATH from environment (.env) → absolute or relative to project root
    2) filename joined with DATA_DIR from environment (.env) or project_root/data
    3) default_path relative to project root

    Parameters
    - default_path: str path used if no env vars and no filename are provided
    - filename: str name within DATA_DIR to quickly switch datasets
    - fmt: optional explicit format ('csv'|'parquet'); inferred from extension if omitted
    - **read_kwargs: forwarded to pandas reader (e.g., usecols=..., dtype=..., nrows=...)
    """
    # Determine project root (repo root) cross-platform
    project_root = Path(__file__).parent.parent

    # Environment-provided paths/dirs
    env_data_path = os.getenv("DATA_PATH")
    env_data_dir = os.getenv("DATA_DIR")

    # Resolve base data directory:
    # - If DATA_DIR is absolute, use it as-is
    # - If DATA_DIR is relative, resolve relative to project_root
    # - Otherwise default to project_root / "data"
    if env_data_dir:
        data_dir_path = Path(env_data_dir)
        if not data_dir_path.is_absolute():
            data_dir_path = (project_root / data_dir_path).resolve()
    else:
        data_dir_path = (project_root / "data").resolve()

    # Resolve final data path by priority
    if env_data_path:
        candidate = Path(env_data_path)
        if not candidate.is_absolute():
            data_path = (project_root / candidate).resolve()
        else:
            data_path = candidate
    elif filename:
        data_path = (data_dir_path / filename).resolve()
    else:
        data_path = (project_root / default_path).resolve()

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # Infer format from suffix if not explicitly provided
    inferred_fmt = (fmt or data_path.suffix.lstrip(".")).lower()
    print(f"Loading data from: {data_path}")

    if inferred_fmt in ("csv", "txt"):
        return pd.read_csv(data_path, **read_kwargs)
    if inferred_fmt in ("parquet", "pq"):
        return pd.read_parquet(data_path, **read_kwargs)
    # Fallback: attempt CSV
    return pd.read_csv(data_path, **read_kwargs)
