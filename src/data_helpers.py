import datetime
import pandas as pd
import numpy as np

# make sure to use North America Company Name Merge by DataDate-GVKEY-IID.csv
# WARNING: This creates about 2k rows of duplicates
def merge_company_names_etc(raw, mappings):
    mappings['datadate'] = pd.to_datetime(mappings['datadate'])

    raw['date'] = pd.to_datetime(raw['ret_eom'])

    merged = pd.merge(raw, mappings[['gvkey', 'datadate', 'iid', 'tic', 'conm', 'cusip','cik']], 
                    left_on=['gvkey', 'date', 'iid'], 
                    right_on=['gvkey', 'datadate', 'iid'], 
                    how='left')
    
    # checking duplicates for your info
    # Check for duplicates in the merged DataFrame
    original_row_count = raw.shape[0]
    merged_row_count = merged.shape[0]

    if original_row_count == merged_row_count:
        print("No duplicates were created during the merge.")
    else:
        print(f"Duplicates detected: Original rows = {original_row_count}, Merged rows = {merged_row_count}, Difference = {merged_row_count - original_row_count}")

    return merged