# Document Ingestion and Vector Embedding Pipeline

A production-ready Python module to **extract, clean, partition, and embed** text from PDF and DOCX documents into a PostgreSQL database using Google's Gemini Embedding API. This is the foundational data ingestion layer for a Retrieval-Augmented Generation (RAG) architecture.

---

## 🚀 Features

- **Robust Text Extraction:**  
  - Seamlessly extracts raw text from both .pdf and .docx file formats, converting them into a standardized text string ready for the unified cleaning, chunking, and embedding pipeline.

- **Advanced Text Cleaning:**  
  - Standardizes carriage returns  
  - Strips structural whitespaces  
  - Removes layout artifacts while preserving intentional blank lines

- **Multi-Strategy Text Chunking:**  
  - **Paragraph-Based Splitting:** Clean partitioning using visual empty boundaries  
  - **Sentence-Based Splitting:** Regex-driven, avoids breaking on abbreviations (e.g., Dr., U.S.A.)  
  - **Fixed-Size with Overlap:** Sliding window with character limits and overlap

- **Vector Storage Infrastructure:**  
  - Automated integration with PostgreSQL via the `pgvector` extension

---

## ⚡ Quick Start Guide

Follow these steps to get the pipeline running in **less than 2 minutes**. You will use these credentials later, so keep them (Gemini API Key and PostgreSQL Connection String).

### 1. Obtain API Keys & Connection Strings

- **Google Gemini API Key:**  
  - Go to Google AI Studio, click "Get API Key", and generate a free key.
  https://aistudio.google.com/api-keys
- **PostgreSQL Connection String:**  
  - Use [Neon](https://neon.tech/) or any PostgreSQL provider.  
  - Example:  
    ```
    postgresql://<user>:<password>@<host>/neondb?sslmode=require
    ```

---

### 2. Clone and Enter the Project

- from the terminal 
```sh
git clone <this-github-repository-url>
cd RAG_PROJECT
```

---

### 3. Set Up a Virtual Environment

**macOS / Linux:**
```sh
python -m venv venv
source venv/bin/activate
```

**Windows (CMD):**
```sh
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```sh
python -m venv venv
venv\Scripts\Activate.ps1
```

---

### 4. Install Required Packages

```sh
pip install pypdf python-docx google-genai psycopg2-binary python-dotenv
```

---

### 5. Configure Environment Variables

The pipeline loads credentials from a local `.env` file (ignored by Git).

**Create your `.env` file:**

**macOS / Linux:**
```sh
cp .env.example .env
```

**Windows (CMD):**
```sh
copy .env.example .env
```

**Windows (PowerShell):**
```sh
Copy-Item .env.example .env
```

Open `.env` in a text editor and paste your credentials from the begining:
```
GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiApiKeyHere
POSTGRES_URL=postgresql://neondb_owner:your_password@your-endpoint.neon.tech/neondb?sslmode=require
```

---

### 6. Run the Ingestion Script

The database tables and `pgvector` extension are initialized automatically.

**Examples:**

- **A. Running on Your Own Custom File (Recommended for Grading):**
  1. Place your `.pdf` or `.docx` file inside the project directory at the root (e.g., `my_document.pdf`).
  2. Run the script pointing to your file with your preferred strategy:
     ```sh
     python index_documents.py --file my_document.pdf --strategy "sentence-based splitting"
     ```

- **B. Running with Overlap on Your Own DOCX File:**
  1. Place your `.docx` file inside the project directory (e.g., `my_notes.docx`).
  2. Run the script using the fixed-size with overlap strategy:
     ```sh
     python index_documents.py --file my_notes.docx --strategy "fixed-size with overlap" --chunk-size 200 --overlap 40
     ```

- **C. Paragraph Chunking (PDF):**
  ```sh
  python index_documents.py --file tests/test_2_config.pdf --strategy "paragraph-based splitting"
  ```

- **D. Sentence Chunking (DOCX):**
  ```sh
  python index_documents.py --file tests/test_4_edge_cases.docx --strategy "sentence-based splitting"
  ```

- **E. Fixed-Size Sliding Window (PDF):**
  ```sh
  python index_documents.py --file tests/test_1_prose.pdf --strategy "fixed-size with overlap" --chunk-size 150 --overlap 30
  ```

---

### 7. Verify Ingested Data

**Check chunk counts per file:**
```sql
SELECT filename, split_strategy, COUNT(*) as total_chunks
FROM document_chunks
GROUP BY filename, split_strategy
ORDER BY filename ASC;
```

**Inspect sentence boundaries:**
```sql
SELECT id, filename, split_strategy, chunk_text 
FROM document_chunks 
WHERE filename = 'test_4_edge_cases.docx'
ORDER BY id ASC;
```

---

## 🛠️ CLI Reference

| Parameter         | Required | Description                                                                                 |
|-------------------|----------|---------------------------------------------------------------------------------------------|
| `--file`, `-f`    | Yes      | Path to your `.pdf` or `.docx` file                                                         |
| `--strategy`, `-s`| Yes      | Chunking logic: `"fixed-size with overlap"`, `"sentence-based splitting"`, or `"paragraph-based splitting"` |
| `--chunk-size`    | No       | Character limit per chunk (fixed-size only, default: 500)                                   |
| `--overlap`       | No       | Overlap size in characters (fixed-size only, default: 50)                                   |

---

## 📁 Project Structure

```
.env (Secrets)
.env.example
.gitignore
index_documents.py
README.md
tests/
    generate_test_suite.py
    test_1_prose.docx
    test_1_prose.pdf
    test_2_config.docx
    test_2_config.pdf
    test_3_bullets.docx
    test_3_bullets.pdf
    test_4_edge_cases.docx
    test_4_edge_cases.pdf
    test_5_mixed_report.docx
    test_5_mixed_report.pdf
```

- All test documents and test-related files are now located in the `tests/` directory.
```