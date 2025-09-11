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

- **Full dataset**: Download from shared [link](https://can01.safelinks.protection.outlook.com/?url=https%3A%2F%2Fvascodesign.dmanalytics2.com%2Fclick%3Fu%3Dhttps%253A%252F%252Fmcgill-my.sharepoint.com%252F%253Af%253A%252Fg%252Fpersonal%252Fruslan_goyenko_mcgill_ca%252FEuYuJbIBNzZBiFvNg5xZOQwBvxr6nOK5bZ_ROh8xFvTitg%253Fe%253D5%25253a6UJ0Ad%2526at%253D9%26i%3D1%26d%3DeY0h62ukTvWcRaeJAxGuQw%26e%3Dkevin.zhang5%2540mail.mcgill.ca%26a%3DAZkYDCYBftyC1YmXv1Vu0A%26s%3DTRo6PsK8gaQ&data=05%7C02%7Ckevin.zhang5%40mail.mcgill.ca%7Cfde291c0d0d34f4b68f808ddec315898%7Ccd31967152e74a68afa9fcf8f89f09ea%7C0%7C0%7C638926419474047679%7CUnknown%7CTWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D%7C40000%7C%7C%7C&sdata=ZuuURfTWBBpAg8WHLXNaKI0p3pBCBIj3SdZe6srY%2BtI%3D&reserved=0) (download from the OneDrive). 
**WARNING** : the data reading is not ready/tested for the text data right now. it's for the excel files. Download them and put them all in one folder and then you can get the path to that folder and put it in your .env file that you need to create in your config folder of the project.
- **Sample data**: `data/sample.csv` included for quick testing.

## 🤝 Notes

- Works on Mac, Linux, Windows (thanks to `pathlib`).
- If dataset missing, code falls back to `data/sample.csv`.
- Notebooks import data via `src/data_loader.py`.
