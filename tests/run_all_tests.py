import os
import subprocess

# 1. Defined strategies based on CLI requirements
strategies = [
    "fixed-size with overlap",
    "sentence-based splitting",
    "paragraph-based splitting"
]

# 2. Collect test files (Added protection against hidden macOS metadata files)
test_files = [
    os.path.join("tests", f) 
    for f in os.listdir("tests") 
    if f.endswith(('.pdf', '.docx')) and not f.startswith('.')
]

print(f"Found {len(test_files)} test files. Starting matrix run (Total {len(test_files) * len(strategies)} executions)...\n")

# 3. Iterate over the matrix
for file_path in test_files:
    for strategy in strategies:
        print(f"Testing: {file_path} | Strategy: {strategy}...")
        
        # Build the dynamic CLI command
        cmd = [
            "python", "index_documents.py",
            "--file", file_path,
            "--strategy", strategy
        ]
        
        # Inject specific parameters for the sliding window strategy
        if strategy == "fixed-size with overlap":
            cmd.extend(["--chunk-size", "150", "--overlap", "30"])
            
        # Execute the main pipeline script safely
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Assert that the script finished with exit code 0 (No crashes)
        assert result.returncode == 0, f"Failed on {file_path} with {strategy}.\nError output: {result.stderr}"
        
        print(f"Success! Data ingested successfully.\n")

print("ALL COMBINATIONS PROCESSED SUCCESSFULLY WITHOUT CRASHES!")