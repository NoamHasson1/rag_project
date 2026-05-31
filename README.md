# Document Ingestion and Vector Embedding Pipeline

A production-ready Python module to **extract, clean, partition, and embed** text from PDF and DOCX documents into a PostgreSQL database using Google's Gemini Embedding API. This is the foundational data ingestion layer for a Retrieval-Augmented Generation (RAG) architecture.

---

## Prerequisites & Requirements

  - **Python Version:** Python `3.10` or higher is strictly recommended.
  - **Database:** PostgreSQL instance with the `pgvector` extension installed.
  - **External Access:** Active internet connection to connect to Google's Gemini API endpoints and your remote database instance.
  - **Required Secrets:** * A valid **Google Gemini API Key** (authorized via Google AI Studio, will be described later).
  - A valid **PostgreSQL Connection URL** (will be described later).

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

Follow these steps to get the pipeline running. You will use these credentials later, so keep them (Gemini API Key and PostgreSQL Connection String).

### 1. Obtain API Keys & Connection Strings

- **Google Gemini API Key:**  
  - Go to Google AI Studio, log in with any Google account, click the blue "Get API Key" button, and copy your key.
  https://aistudio.google.com/api-keys (Keep this window open so you can easily copy the API Key later).
- **PostgreSQL Connection String:**  
  - You can use [Neon](https://neon.tech/) or any PostgreSQL provider. If you use [Neon](https://neon.tech/), create a free account, and create a new database.
  Create an account, click on "New project", give it a name in the "Project name", and choose AWS Europe Central 1 (Frankfurt).
  After that, click the "Dashboard" button on the left side in the top, click and the "Connection string" box and copy the Connection String. It looks like the example.
  - Example:  
    ```
    postgresql://<user>:<password>@<host>/neondb?sslmode=require 
    or
    postgresql://user:password@localhost:____/your_db_name
    ```

---

### 2. Clone and Enter the Project

- Open your computer's terminal (called Terminal on macOS/Linux, or Command Prompt / PowerShell on Windows) and paste these commands: 
```sh
# 1. Download the code from GitHub to your computer
git clone <repository-url>

# 2. Move your terminal focus inside the project folder
cd RAG_PROJECT
```

---

### 3. Set Up a Virtual Environment

**CRITICAL FOR macOS USERS:** Google Gemini API frameworks strictly require **Python 3.10 or higher**. Before creating the environment, verify your active terminal environment version:
```sh
python3 --version
```
If this returns Python 3.9 or lower, please update your Python runtime via Python.org or Homebrew before continuing.

- To make sure this project doesn't conflict with any other software on your machine, we create a secure, isolated sandbox folder called venv. Paste the command matching your 
system:

**macOS / Linux:**
```sh
python -m venv venv
source venv/bin/activate
```

if didn't work - 

**macOS / Linux:**
```sh
python3 -m venv venv
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
pip install -r requirements.txt
```
---

### 5. Configure Environment Variables

The pipeline loads credentials from a local `.env` file (ignored by Git). Because your database password and Gemini key are secret, we don't put them in the public code. We put them in a hidden file called .env.

CRITICAL: Make sure your terminal is still located inside the main project directory (RAG_PROJECT) before running the copy commands below.

- Create a `.env` file in the root directory: let's create te file - Run the command for your system to copy our template into a real configuration file:

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

- Can't see or open the `.env` file? Because files starting with a dot (`.`) are hidden by default on macOS and Linux, you might not see the file in your standard folder view. 

* **On macOS / Linux:** Run `open -e .env` (This opens it instantly in the built-in TextEdit app).

* **On Windows:** Run `notepad .env` (This opens it instantly in the built-in Notepad app).

*Alternatively, you can always open VS Code manually, click on the **File Explorer** tab on the left sidebar, and click directly on the `.env` file to edit it!*

Paste your keys: Open the newly created `.env` file with any basic text editor (like Notepad or VS Code) and replace the text with your actual keys:

```
GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiApiKeyHere
POSTGRES_URL=Paste_Your_Database_Url_Here
```

---

### 6. Run the Ingestion Script

You are ready! The tool will automatically log into your database, set up the required tables, read the file, and save the data. Just copy and paste one of these examples into your terminal:

**What to expect** 

- Terminal Output:

```text
=================================================
Starting pipeline for file: my_document.pdf
Selected Chunking Strategy: "strategy"
=================================================
Connecting and checking Database state...
[OK] Database connection established and schema verified.
Extracting raw text from document...
[OK] Document parsed. Total characters: ___
Chunking text based on strategy rules...
[OK] Split text into __ distinct chunk segments.
-> Generating embeddings and storing __ chunks in database...
   Progress: _/_ chunks ingested successfully.
   Progress: _/_ chunks ingested successfully.
[SUCCESS] All _ chunks saved to database table 'document_chunks'.
Pipeline execution finished flawlessly.
Database connection closed gracefully.
```
*(Note: The number will vary based on how many text chunks were generated from your document.)*

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

- **D. Process a PDF Document by splitting it into clean sentences:**

```sh
  python index_documents.py --file tests/test_1_prose.pdf --strategy "sentence-based splitting"
  ```

- **E. Process a Word Document by splitting it into clean sentences:**
  ```sh
  python index_documents.py --file tests/test_4_edge_cases.docx --strategy "sentence-based splitting"
  ```

- **F. Process a file using a fixed character window (150 characters per chunk):**
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

**Inspect the FULL table layout (Including Vectors) for a specific run** 

Let's say that you recently executed this exact command:
```sh
python index_documents.py --file tests/test_1_prose.pdf --strategy "sentence-based splitting"
```
You can fetch every single column—including the text, metadata, and the raw mathematical AI vectors—by running this query:
```sql
SELECT id, chunk_text, embedding, filename, split_strategy, created_at
FROM document_chunks 
WHERE filename LIKE 'test_1_prose.pdf' AND split_strategy = 'sentence-based splitting'
ORDER BY id ASC;
```
What will you see in the results?

- id: The auto-incrementing unique identifier for that specific text block.
- chunk_text: The cleaned, raw text snippet pulled from the PDF sentence.
- embedding: This is where the magic happens! You will see a large array of 768 decimal numbers (e.g., [0.01234, -0.05678, 0.11223...]). This is the raw directional vector generated by Google's Gemini API that represents the semantic meaning of your text inside the database.
- filename & split_strategy: Keeping track of exactly where this chunk came from and how it was processed.
---

## Troubleshooting

- If the pipeline encounters deployment or runtime friction, consult this matrix to resolve issues quickly:
1. Database Error - Ensure your `POSTGRES_URL` is correct and the database user has permission to create extensions.
2. Gemini API Error [403] API key not valid - Ensure your .env file name starts with a dot (.env), has no trailing spaces around the equals sign, and that your API key is active.
3. Vector Dimension Mismatch: psycopg2.errors.InvalidParameterValue: ERROR: vector dimensions must be 768 - This happens if you change the embedding model inside the code script to a different model version while the database table structure was initialized with a strict VECTOR(768) layout constraint.
4. * **The Error:** Running `pip install -r requirements.txt` crashes with an explicit error message stating that it cannot find or satisfy the requirement for `anyio` or other dependencies. 
1. Install a modern package version (Python `3.11` or `3.12`).
2. Kill the outdated environment wrapper completely:
     ```sh
     rm -rf venv
     ```
3. Rebuild the environment specifying your updated runtime instance:
     ```sh
     python3.11 -m venv venv
     # or python3.12 -m venv venv based on your installation
     ```
4. Activate and trigger execution setup safely:
     ```sh
     source venv/bin/activate
     python -m pip install --upgrade pip
     pip install -r requirements.txt
     ```
  
## Technical Specifications

* **AI Embedding Model:** `gemini-embedding-2`.
* **Vector Geometry Dimension:** **768** (768 Dense floating-point numerical matrix coordinates per chunk).
* **Database Storage Instance:**PostgreSQL relational database running the pgvector extension.


## CLI Reference

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
requirements.txt
README.md
tests/
    generate_test_suite.py
    run_all_tests.py
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