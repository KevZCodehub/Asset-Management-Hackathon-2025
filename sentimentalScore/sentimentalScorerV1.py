import pickle
import pandas as pd
import re
from transformers import AutoTokenizer, pipeline

# Load data
# CHANGE PATH TO YOUR LOCAL PATH
path = r"C:/Users/franr/source/Asset-Management-Hackathon-2025/data/text_us_2025.pkl"
with open(path, "rb") as f:
    df = pickle.load(f)

# Load FinBERT
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

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
def score_sentiment(text, max_tokens=510):
    if not text or len(text.strip()) == 0:
        return 0.0
    chunks = chunk_text_by_sentences(text, max_tokens=max_tokens)
    scores = []
    for chunk in chunks:
        result = sentiment_pipeline(chunk)[0]
        label, score = result["label"], result["score"]
        if label.lower() == "positive":
            scores.append(score)
        elif label.lower() == "negative":
            scores.append(-score)
        else:
            scores.append(0.0)
    return sum(scores) / len(scores) if scores else 0.0

# Filter out rows without gvkey first
rows_to_process = df.dropna(subset=["gvkey"])
# FOR TESTING ONLY: limit to first 100 rows
rows_to_process = df.dropna(subset=["gvkey"]).iloc[:100]

total_rows = len(rows_to_process)
print(f"Total texts to process: {total_rows}\n")

output = []
for count, (i, row) in enumerate(rows_to_process.iterrows(), start=1):
    text = row.get("rf", "")
    sentiment_score = score_sentiment(text)
    output.append({
        "date": row.get("date"),
        "gvkey": row.get("gvkey"),
        "sentiment_score": sentiment_score
    })
    print(f"Processed {count}/{total_rows} texts, {total_rows - count} remaining", end="\r")

# Save results
sentiment_df = pd.DataFrame(output)
sentiment_df.to_csv("output.csv", index=False)
print("\nSentiment scores saved to output.csv")
