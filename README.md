# Document Ingestion and Vector Embedding Pipeline

A production-ready Python module to **extract, clean, partition, and embed** text from PDF and DOCX documents into a PostgreSQL database using Google's Gemini Embedding API. This is the foundational data ingestion layer for a Retrieval-Augmented Generation (RAG) architecture.

---

## Features

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
  - Go to Google AI Studio, log in with any Google account, click the blue "Get API Key" button, and copy your key.
  https://aistudio.google.com/api-keys
- **PostgreSQL Connection String:**  
  - Use [Neon](https://neon.tech/) or any PostgreSQL provider. If you use [Neon](https://neon.tech/), create a free account, and create a new database. Copy the Connection String from your dashboard. It looks like the example.
  - Example:  
    ```
    postgresql://<user>:<password>@<host>/neondb?sslmode=require
    ```

---

### 2. Clone and Enter the Project

- Open your computer's terminal (called Terminal on macOS/Linux, or Command Prompt / PowerShell on Windows) and paste these commands: 
```sh
# 1. Download the code from GitHub to your computer
git clone <your-github-repository-url>

# 2. Move your terminal focus inside the project folder
cd RAG_PROJECT
```

---

### 3. Set Up a Virtual Environment

- To make sure this project doesn't conflict with any other software on your machine, we create a secure, isolated sandbox folder called venv. Paste the command matching your system:
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
- Visual Check: You know it worked if you now see (venv) written at the very beginning of your terminal line. 

---

### 4. Install Required Packages

- Now, install the tool's building blocks (libraries that read PDFs, connect to databases, etc.) by running this command:
```sh
pip install pypdf python-docx google-genai psycopg2-binary python-dotenv
```
---

### 5. Configure Environment Variables

The pipeline loads credentials from a local `.env` file (ignored by Git). Because your database password and Gemini key are secret, we don't put them in the public code. We put them in a hidden file called .env.

CRITICAL: Make sure your terminal is still located inside the main project directory (RAG_PROJECT) before running the copy commands below.

- Create the file: Run the command for your system to copy our template into a real configuration file:

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
Paste your keys: Open the newly created `.env` file with any basic text editor (like Notepad or VS Code) and replace the text with your actual keys:

```
GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiApiKeyHere
POSTGRES_URL=Paste_Your_Neon_Database_Url_Here
```

---

### 6. Run the Ingestion Script

You are ready! The tool will automatically log into your database, set up the required tables, read the file, and save the data. Just copy and paste one of these examples into your terminal:

**Examples:**

- **A. Test it with your own custom file:**
  1. Place your .pdf or .docx file directly inside the main project root folder (RAG_PROJECT), right next to index_documents.py (do NOT put it inside the tests/ folder). Let's say you named it my_document.pdf.
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

- **C. Process a PDF by splitting it into paragraphs:**
  ```sh
  python index_documents.py --file tests/test_2_config.pdf --strategy "paragraph-based splitting"
  ```

- **D. Process a Word Document by splitting it into clean sentences:**
  ```sh
  python index_documents.py --file tests/test_4_edge_cases.docx --strategy "sentence-based splitting"
  ```

- **E. Process a file using a fixed character window (150 characters per chunk):**
  ```sh
  python index_documents.py --file tests/test_1_prose.pdf --strategy "fixed-size with overlap" --chunk-size 150 --overlap 30
  ```

---

### 7. See the Results inside Your Database

To prove that the data actually arrived safely in your database, log into your Neon Console (or something else youv'e did), open the SQL Editor tab on the left, and run this simple query:

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

- When running index_documents.py, you can use the following parameters:

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