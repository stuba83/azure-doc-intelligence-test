# Azure Document Intelligence Test

## Configuración inicial

1. **Editar .env con tus credenciales:**
   ```
   DOCUMENT_INTELLIGENCE_ENDPOINT=https://tu-recurso.cognitiveservices.azure.com/
   DOCUMENT_INTELLIGENCE_KEY=tu-clave-aqui
   ```

2. **Añadir documentos de prueba en test_documents/:**
   - sample.pdf
   - document_with_tables.pdf
   - complex_document.pdf

## Ejecutar pruebas

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
- Abrir rest_api/test_api.http en VS Code
- Usar la extensión REST Client
- Ejecutar cada request paso a paso

## Resultados

Los resultados se guardarán en la carpeta `results/` con:
- `*_content.txt`: Contenido completo extraído
- `*_report.txt`: Reporte de análisis con formato detectado
