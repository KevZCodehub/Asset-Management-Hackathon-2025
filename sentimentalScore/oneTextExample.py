import pickle
import csv
import re
from transformers import AutoTokenizer, pipeline

# This process only uses one text example from the dataset and demonstrates with more insight
# how the chunking process works and how the sentiment is calculated.

# Load data
path = r"C:/Users/franr/source/Asset-Management-Hackathon-2025/data/text_us_2025.pkl"
with open(path, "rb") as f:
    df = pickle.load(f)

# Load FinBERT
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# Get first row text
text = df.iloc[0]["rf"]

# Print full text
print("Full text of first row:\n")
print(text)
print("\n" + "="*80 + "\n")

# Function to split text into sentences
def split_into_sentences(text):
    """Split text into sentences while preserving all content."""
    # Split on sentence-ending punctuation followed by space and capital letter
    # Also handle bullet points (•) as sentence separators
    sentences = re.split(r'(?<=[.!?;])\s+(?=[A-Z•])|(?<=;)(?=•)', text)
    return [s.strip() for s in sentences if s.strip()]

# Function to chunk text by complete sentences without cutting them
def chunk_text_by_sentences(text, max_tokens=510):
    """
    Chunk text into segments that fit within max_tokens.
    - Complete sentences are NEVER split - if a sentence doesn't fit, it goes to next chunk
    - If a single sentence exceeds max_tokens on its own, only then it's split by words
    - GUARANTEES no content is lost and no mid-sentence cuts
    """
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Always check the sentence token count first
        sentence_tokens = len(tokenizer(sentence, return_tensors="pt")["input_ids"][0])
        
        if sentence_tokens > max_tokens:
            # If sentence is longer than a chunck even on its own, it must split it by words
            # First, save current chunk if it exists
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            # Split the long sentence by words
            words = sentence.split()
            word_chunk = ""  # Initialize word_chunk
            for word in words:
                test_chunk = word_chunk + (" " if word_chunk else "") + word
                test_len = len(tokenizer(test_chunk, return_tensors="pt")["input_ids"][0])
                if test_len <= max_tokens:
                    word_chunk = test_chunk
                else:
                    # Current word would exceed limit, save what we have
                    if word_chunk:
                        chunks.append(word_chunk)
                        word_chunk = word  # Start new chunk with current word
                    else:
                        # Single word exceeds limit (very rare), must include it anyway
                        chunks.append(word)
                        word_chunk = ""
            # Add remaining words from the long sentence to current_chunk
            if word_chunk:
                # Check if word_chunk itself is within limits before assigning
                word_chunk_tokens = len(tokenizer(word_chunk, return_tensors="pt")["input_ids"][0])
                if word_chunk_tokens > max_tokens:
                    # Even the word_chunk is too long, save it anyway (edge case)
                    chunks.append(word_chunk)
                    current_chunk = ""
                else:
                    current_chunk = word_chunk
        else:
            # Sentence fits within limit by itself
            if current_chunk:
                # Try adding the sentence to current chunk
                candidate = current_chunk + " " + sentence
                candidate_tokens = len(tokenizer(candidate, return_tensors="pt")["input_ids"][0])
                
                if candidate_tokens <= max_tokens:
                    # Adding sentence keeps us under limit - ADD IT
                    current_chunk = candidate
                else:
                    # Adding sentence would exceed limit - DON'T ADD IT
                    # Save current chunk and start new chunk with this sentence
                    chunks.append(current_chunk)
                    current_chunk = sentence
            else:
                # First sentence in chunk - just add it
                current_chunk = sentence
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

# Generate chunks
print("CHUNKING TEXT...")
max_tokens = 510
chunks = chunk_text_by_sentences(text, max_tokens=max_tokens)
print(f"Generated {len(chunks)} chunks\n")

# Debug: Check for duplicate chunks and oversized chunks
unique_chunks = set()
oversized_count = 0
for i, chunk in enumerate(chunks):
    if chunk in unique_chunks:
        print(f"WARNING: Duplicate chunk found at index {i}")
    unique_chunks.add(chunk)
    
    chunk_tokens = len(tokenizer(chunk, return_tensors="pt")["input_ids"][0])
    if chunk_tokens > max_tokens:
        oversized_count += 1
        print(f"⚠️  Chunk {i+1} has {chunk_tokens} tokens (exceeds {max_tokens})")

if oversized_count > 0:
    print(f"\n⚠️  Total oversized chunks: {oversized_count}")
else:
    print(f"✓ All chunks are within {max_tokens} token limit\n")

# Prepare results for CSV
results = []
total_tokens = 0
weighted_sentiment_sum = 0.0

# Process each chunk and collect results
for idx, chunk_text in enumerate(chunks, 1):
    result = sentiment_pipeline(chunk_text)[0]
    label, score = result["label"], result["score"]

    if label.lower() == "positive":
        mapped_score = score
    elif label.lower() == "negative":
        mapped_score = -score
    else:
        mapped_score = 0.0

    token_count = len(tokenizer(chunk_text, return_tensors="pt")["input_ids"][0])
    
    # SAFETY CHECK: Ensure chunk is within limit
    if token_count > max_tokens:
        print(f"⚠️  WARNING: Chunk {idx} has {token_count} tokens (exceeds {max_tokens})!")
    
    # Add to weighted calculation
    total_tokens += token_count
    weighted_sentiment_sum += mapped_score * token_count
    
    print(f"\n--- Chunk {idx} ({token_count} tokens) ---")
    print(f"Text: {chunk_text}\n")
    print(f"Sentiment: {label} | Raw score: {score:.4f} | Mapped score: {mapped_score:.4f}")
    
    # Store result
    results.append({
        "chunk_id": idx,
        "token_count": token_count,
        "chunk_text": chunk_text,
        "sentiment_label": label,
        "raw_score": score,
        "mapped_score": mapped_score
    })

# Calculate weighted average sentiment
weighted_avg_sentiment = weighted_sentiment_sum / total_tokens if total_tokens > 0 else 0.0

# Add summary row
results.append({
    "chunk_id": "WEIGHTED_AVERAGE",
    "token_count": total_tokens,
    "chunk_text": f"Weighted average of all {len(chunks)} chunks",
    "sentiment_label": "SUMMARY",
    "raw_score": "",
    "mapped_score": weighted_avg_sentiment
})

# Write results to CSV
output_path = "output.csv"
with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["chunk_id", "token_count", "chunk_text", "sentiment_label", "raw_score", "mapped_score"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(results)

# Verification statistics
total_chars_in_chunks = sum(len(c) for c in chunks)
# Account for spaces between chunks that were in the original
spaces_between_chunks = len(chunks) - 1
reconstructed_length = total_chars_in_chunks + spaces_between_chunks

print("\n" + "="*80)
print("SUMMARY STATISTICS")
print("="*80)
print(f"Results saved to {output_path}")
print(f"Total chunks processed: {len(chunks)}")
print(f"Total tokens processed: {total_tokens}")
print(f"Weighted average sentiment: {weighted_avg_sentiment:.4f}")
print(f"\nCONTENT VERIFICATION:")
print(f"  • Original text length: {len(text)} characters")
print(f"  • Total in all chunks: {total_chars_in_chunks} characters")
print(f"  • Reconstructed (with spaces): {reconstructed_length} characters")
print(f"  • Content preserved: {'YES' if abs(len(text) - reconstructed_length) <= 1 else 'NO - SOME CONTENT LOST!'}")
print(f"  • Character difference: {len(text) - reconstructed_length}")

# Additional verification: reconstruct text and compare
reconstructed_text = " ".join(chunks)
if reconstructed_text == text:
    print(f"  • Perfect match: YES - All content preserved exactly!")
else:
    print(f"  • Perfect match: NO - {len(text) - len(reconstructed_text)} chars differ")
    
print("\n" + "="*80)