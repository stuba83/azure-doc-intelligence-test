# Azure Document Intelligence Test

## Initial Setup

1. **Edit .env with your credentials:**
   ```
   DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   DOCUMENT_INTELLIGENCE_KEY=your-key-here
   ```

2. **Add test documents in test_documents/:**
   - sample.pdf
   - document_with_tables.pdf
   - complex_document.pdf

## Run Tests

### Python
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python python/test_layout_api.py
```

### C#
```bash
dotnet restore csharp/
dotnet run --project csharp/
```

### REST API
- Open rest_api/test_api.http in VS Code
- Use the REST Client extension
- Execute each request step by step

## Results

Results will be saved in the `results/` folder with:
- `*_content.txt`: Complete extracted content
- `*_report.txt`: Analysis report with detected format