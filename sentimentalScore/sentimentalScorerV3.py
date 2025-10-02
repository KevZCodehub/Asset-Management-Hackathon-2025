import pickle
import pandas as pd
import re
import time
from transformers import AutoTokenizer, pipeline

# Load data
# CHANGE PATH TO YOUR LOCAL PATH
path = r"C:/Users/franr/source/Asset-Management-Hackathon-2025/data/text_us_2005.pkl"
with open(path, "rb") as f:
    df = pickle.load(f)

# Load FinBERT
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

start_time = time.time()

# Function to split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?;])\s+(?=[A-Z•])|(?<=;)(?=•)', text)
    return [s.strip() for s in sentences if s.strip()]

# Function to chunk text by sentences without cutting them
def chunk_text_by_sentences(text, max_tokens=510):
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence_tokens = len(tokenizer(sentence, return_tensors="pt")["input_ids"][0])
        
        if sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            words = sentence.split()
            word_chunk = ""
            for word in words:
                test_chunk = word_chunk + (" " if word_chunk else "") + word
                test_len = len(tokenizer(test_chunk, return_tensors="pt")["input_ids"][0])
                if test_len <= max_tokens:
                    word_chunk = test_chunk
                else:
                    if word_chunk:
                        chunks.append(word_chunk)
                        word_chunk = word
                    else:
                        chunks.append(word)
                        word_chunk = ""
            if word_chunk:
                current_chunk = word_chunk
        else:
            if current_chunk:
                candidate = current_chunk + " " + sentence
                candidate_tokens = len(tokenizer(candidate, return_tensors="pt")["input_ids"][0])
                if candidate_tokens <= max_tokens:
                    current_chunk = candidate
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# Function to score text using sentence-aware chunks
def score_sentiment(text, max_tokens=510, batch_size=64):
    if not text or len(text.strip()) == 0:
        return 0.0

    chunks = chunk_text_by_sentences(text, max_tokens=max_tokens)
    scores = []

    # process in mini-batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        results = sentiment_pipeline(batch)  # list of dicts
        for result in results:
            label, score = result["label"], result["score"]
            if label.lower() == "positive":
                scores.append(score)
            elif label.lower() == "negative":
                scores.append(-score)
            else:  # neutral
                scores.append(0.0)

    return sum(scores) / len(scores) if scores else 0.0


# Helper to get word count
def get_word_count(text):
    if not text or len(str(text).strip()) == 0:
        return 0
    return len(str(text).split())

# Convert gvkey to string for all rows and keep rows where gvkey is not empty
rows_to_process = df.copy()
def _gvkey_to_str_keep(x):
    if pd.isna(x):
        return ""   # treat NaN as empty
    return str(x)  # always return string; preserves any leading/trailing zeros if present as strings

rows_to_process["gvkey"] = rows_to_process["gvkey"].apply(_gvkey_to_str_keep)

# Keep rows where gvkey is non-empty after stripping whitespace
rows_to_process = rows_to_process[rows_to_process["gvkey"].str.strip() != ""]

# FOR TESTING ONLY: limit to first few rows
rows_to_process = rows_to_process.iloc[0:20]

total_rows = len(rows_to_process)
print(f"Total texts to process: {total_rows}\n")

output = []
for count, (i, row) in enumerate(rows_to_process.iterrows(), start=1):
    rf_text = row.get("rf", "") or ""
    mgmt_text = row.get("mgmt", "") or ""

    rf_length = get_word_count(rf_text)
    mgmt_length = get_word_count(mgmt_text)

    rf_score = score_sentiment(rf_text)
    mgmt_score = score_sentiment(mgmt_text)

    # normalize file_type for robust matching
    ft = str(row.get("file_type", "") or "").upper()
    is10k = 1 if ("10-K" in ft or "10K" in ft) else 0
    is10q = 1 if ("10-Q" in ft or "10Q" in ft) else 0

    output.append({
        "date": row.get("date"),
        "cik": row.get("cik"),
        "gvkey": row.get("gvkey"),
        "cusip": row.get("cusip"),
        "year": row.get("year"),
          "is10k": is10k,
        "is10q": is10q,
        "rf_sentiment_score": rf_score,
        "rf_length": rf_length,
        "mgmt_sentiment_score": mgmt_score,
        "mgmt_length": mgmt_length,
    })

    elapsed = time.time() - start_time
    remaining_rows = total_rows - count
    est_remaining = (elapsed / count) * remaining_rows

    # Convert to h:m:s
    elapsed_h, rem = divmod(int(elapsed), 3600)
    elapsed_m, elapsed_s = divmod(rem, 60)

    est_h, rem = divmod(int(est_remaining), 3600)
    est_m, est_s = divmod(rem, 60)

    print(f"Processed {count}/{total_rows} rows, "
        f"elapsed: {elapsed_h}h {elapsed_m}m {elapsed_s}s, "
        f"estimated remaining: {est_h}h {est_m}m {est_s}s", end="\r")


elapsed = time.time() - start_time

# Save results
sentiment_df = pd.DataFrame(output)
sentiment_df.to_csv("output.csv", index=False)
print("\nSentiment scores saved to output.csv")
print(f"Elapsed time: {elapsed:.2f} seconds")