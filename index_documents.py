import os
import re
import sys
import argparse
import psycopg2
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document

# Load environment variables from the .env file
load_dotenv()

# Verify environment variables before initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
POSTGRES_URL = os.getenv("POSTGRES_URL")

if not GEMINI_API_KEY or not POSTGRES_URL:
    print("[ERROR] Missing required environment variables GEMINI_API_KEY or POSTGRES_URL in .env file.")
    sys.exit(1)

# Initialize the Gemini Client. 
# It automatically looks for the GEMINI_API_KEY variable inside your .env file.
client = genai.Client()

def clean_text(text: str) -> str:
    """
    Standardizes newlines and strips trailing whitespace from lines, 
    preserving structural paragraph breaks.
    """
    if not text:
        return ""
    
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    
    return "\n".join(lines)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file page by page.
    """
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        page_text = page.extract_text(extraction_mode="layout")
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts raw text from a DOCX file paragraph by paragraph.
    """
    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)

def extract_text(file_path: str) -> str:
    """
    Main routing function. Validates the file, determines its type,
    triggers the appropriate extraction, and returns cleaned text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif ext == '.docx':
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Only .pdf and .docx are supported.")
        
    return clean_text(raw_text)

def split_by_fixed_size(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits text into fixed-size character chunks with a specified overlap.
    """
    chunks = []
    if not text:
        return chunks
        
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Define the end boundary of the chunk
        end = start + chunk_size
        chunks.append(text[start:end])
        # Move the window forward, subtracting the overlap to maintain context
        start += (chunk_size - overlap)
        
    return chunks

def split_by_sentences(text: str) -> list[str]:
    """
    Splits text into individual sentences safely by first separating structural blocks
    via blank lines, healing internal line-wraps, and then applying lookbehind tokenization.
    """
    chunks = []
    if not text:
        return chunks
        
    blocks = re.split(r'\n\s*\n', text)
    
    for block in blocks:
        if not block.strip():
            continue
            
        unified_block = " ".join([line.strip() for line in block.split("\n") if line.strip()])
        
        sentence_endings = r'(?<!\bDr\.)(?<!\bMr\.)(?<!\bMs\.)(?<!\b[A-Z]\.)(?<=[.!?])\s+'
        sentences = re.split(sentence_endings, unified_block)
        
        for sentence in sentences:
            if sentence.strip():
                chunks.append(sentence.strip())
                
    return chunks

def split_by_paragraphs(text: str) -> list[str]:
    """
    Splits text purely based on visual empty line boundaries (blank lines),
    completely eliminating fragile character-length heuristics.
    """
    chunks = []
    if not text:
        return chunks
        
    # Split the text by any instance of double or multiple consecutive newlines
    raw_paragraphs = re.split(r'\n\s*\n', text)
    
    for para in raw_paragraphs:
        # Clean up internal layout artifacts (like mid-sentence line wraps)
        # by re-joining lines within the same block with a single space
        cleaned_para = " ".join([line.strip() for line in para.split("\n") if line.strip()])
        
        if cleaned_para:
            chunks.append(cleaned_para)
            
    return chunks

def chunk_text(text: str, strategy: str, **kwargs) -> list[str]:
    """
    Main chunking router. Receives the full text and applies the chosen strategy.
    """
    strategy = strategy.lower().strip()
    
    if strategy == "fixed-size with overlap":
        # Pull customized parameters if passed, otherwise use defaults
        size = kwargs.get("chunk_size", 500)
        overlap = kwargs.get("overlap", 50)
        return split_by_fixed_size(text, chunk_size=size, overlap=overlap)
        
    elif strategy == "sentence-based splitting":
        return split_by_sentences(text)
        
    elif strategy == "paragraph-based splitting":
        return split_by_paragraphs(text)
        
    else:
        raise ValueError(f"Unknown splitting strategy: {strategy}")
    
def get_embedding(text: str, model: str = "gemini-embedding-2") -> list[float]:
    """
    Generates a 768-dimensional vector embedding for a text chunk using Gemini API.
    """
    if not text or not text.strip():
        return []
        
    try:
        response = client.models.embed_content(
            model=model,
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        # Returns the actual array of numbers (floats)
        return response.embeddings[0].values
    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {e}")
    
def init_database():
    """
    Connects to PostgreSQL, enables the pgvector extension, and verifies/creates 
    the document_chunks table with the required assignment schema.
    """
    if not POSTGRES_URL:
        raise ValueError("Missing POSTGRES_URL environment variable in .env file.")
        
    try:
        # Establish connection to Neon PostgreSQL
        conn = psycopg2.connect(POSTGRES_URL)
        conn.autocommit = True # Enable autocommit so changes are saved immediately
        
        with conn.cursor() as cur:
            # 1. Enable the pgvector extension inside the database natively
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # 2. Create the table matching the structural columns required by the assignment
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    chunk_text TEXT NOT NULL,
                    embedding VECTOR(768) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    split_strategy VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        return conn
    except Exception as e:
        raise RuntimeError(f"Database Initialization Error: {e}")

def save_chunks_to_db(conn, chunks: list[str], filename: str, strategy: str):
    """
    Processes all chunks, generates vector embeddings, and stores them in bulk to PostgreSQL.
    """
    print(f"-> Generating embeddings and storing {len(chunks)} chunks in database...")
    
    try:
        with conn.cursor() as cur:
            for idx, chunk in enumerate(chunks, 1):
                if not chunk.strip():
                    continue
                
                # Fetch embedding vector from Gemini
                vector = get_embedding(chunk)
                
                # Insert chunk row
                cur.execute("""
                    INSERT INTO document_chunks (chunk_text, embedding, filename, split_strategy)
                    VALUES (%s, %s, %s, %s);
                """, (chunk, str(vector), filename, strategy))
                
                # Print progress update every 5 chunks
                if idx % 5 == 0 or idx == len(chunks):
                    print(f"   Progress: {idx}/{len(chunks)} chunks ingested successfully.")
                    
        print(f"[SUCCESS] All {len(chunks)} chunks saved to database table 'document_chunks'.")
    except Exception as e:
        print(f"[INGESTION ERROR] An error occurred during database injection: {e}")
        conn.rollback()
    

def main():
    parser = argparse.ArgumentParser(
        description="RAG Ingestion Engine: Index PDF/DOCX documents with structural chunking and vector embeddings."
    )
    # Required parameters
    parser.add_argument(
        "--file", "-f", required=True, type=str, 
        help="Path to the source document (.pdf or .docx)"
    )
    parser.add_argument(
        "--strategy", "-s", required=True, type=str,
        choices=["fixed-size with overlap", "sentence-based splitting", "paragraph-based splitting"],
        help="The specific text chunking strategy to use."
    )
    
    # Optional parameters with smart defaults
    parser.add_argument(
        "--chunk-size", type=int, default=500,
        help="Chunk size in characters (only used for fixed-size strategy). Default is 500."
    )
    parser.add_argument(
        "--overlap", type=int, default=50,
        help="Overlap size in characters (only used for fixed-size strategy). Default is 50."
    )
    
    args = parser.parse_args()
    file_path = args.file
    strategy_name = args.strategy
    original_filename = os.path.basename(file_path)

    print("=" * 60)
    print(f"Starting pipeline for file: {original_filename}")
    print(f"Selected Chunking Strategy: {strategy_name}")
    print("=" * 60)

    db_conn = None
    try:
        # Step 1: Initialize Database connection and verify extension/table
        print("Connecting and checking Database state...")
        db_conn = init_database()
        print("[OK] Database connection established and schema verified.")

        # Step 2: Extract text cleanly from file
        print("Extracting raw text from document...")
        cleaned_document_text = extract_text(file_path)
        print(f"[OK] Document parsed. Total characters: {len(cleaned_document_text)}")

        # Step 3: Perform Chunking based on the strategy
        print("Chunking text based on strategy rules...")
        text_chunks = chunk_text(
            cleaned_document_text, 
            strategy_name, 
            chunk_size=args.chunk_size, 
            overlap=args.overlap
        )
        print(f"[OK] Split text into {len(text_chunks)} distinct chunk segments.")

        if not text_chunks:
            print("[WARN] No meaningful text segments could be created. Process aborting.")
            return

        # Step 4: Embed and Save all chunks to the Database
        save_chunks_to_db(db_conn, text_chunks, original_filename, strategy_name)
        print("\nPipeline execution finished flawlessly.")

    except Exception as e:
        print(f"\n[CRITICAL PIPELINE FAILURE] Run stopped due to error: {e}")
    finally:
        if db_conn:
            db_conn.close()
            print("Database connection closed gracefully.")

# This is the entry point that allows executing the script from the terminal
if __name__ == "__main__":
    main()