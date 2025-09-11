# Asset Management Hackathon Project

## 🚀 Setup
1. Clone repo:
   ```bash
   git clone https://github.com/your-org/asset-hackathon.git
   cd asset-hackathon
   ```

2. Create virtual environment:

   **Mac/Linux:**
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv; .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Configure dataset:
   - Copy `config/.env.example` → `config/.env`
   - Edit `DATA_PATH` to point to your local dataset file.

4. Run Jupyter:
   ```bash
   jupyter lab
   ```

## 📂 Data

- **Full dataset**: Download from shared link (download from the OneDrive).
- **Sample data**: `data/sample.csv` included for quick testing.

## 🤝 Notes

- Works on Mac, Linux, Windows (thanks to `pathlib`).
- If dataset missing, code falls back to `data/sample.csv`.
- Notebooks import data via `src/data_loader.py`.
