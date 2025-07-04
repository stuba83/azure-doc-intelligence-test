import os
import sys
from datetime import datetime
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DocumentIntelligenceTest:
    def __init__(self):
        self.endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
        
        if not self.endpoint or not self.key:
            raise ValueError("Faltan variables de entorno. Revisa el archivo .env")
        
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint, 
            credential=AzureKeyCredential(self.key)
        )
    
    def analyze_document(self, document_path):
        """Analiza un documento y determina el formato de salida"""
        print(f"\n🔍 Analizando: {document_path}")
        
        try:
            with open(document_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    "prebuilt-layout",
                    analyze_request=f,
                    content_type="application/octet-stream"
                )
            
            print("⏳ Procesando documento...")
            result = poller.result()
            
            # Análisis del contenido
            content = result.content
            format_detected = self._detect_format(content)
            
            # Crear reporte
            report = self._create_report(document_path, content, format_detected)
            
            # Guardar resultados
            self._save_results(document_path, content, report)
            
            print(f"✅ Análisis completado: {format_detected}")
            return result
            
        except Exception as e:
            print(f"❌ Error procesando {document_path}: {e}")
            return None
    
    def _detect_format(self, content):
        """Detecta si el contenido es HTML, Markdown o texto plano"""
        content_lower = content.lower()
        
        # Detectar HTML
        html_indicators = ['<html>', '<div>', '<p>', '<table>', '<tr>', '<td>', '<span>']
        html_count = sum(1 for indicator in html_indicators if indicator in content_lower)
        
        # Detectar Markdown
        markdown_indicators = ['# ', '## ', '### ', '**', '*', '- ', '1. ', '|']
        markdown_count = sum(1 for indicator in markdown_indicators if indicator in content)
        
        if html_count > 0:
            return f"HTML (indicadores: {html_count})"
        elif markdown_count > 2:
            return f"Markdown (indicadores: {markdown_count})"
        else:
            return "Texto plano"
    
    def _create_report(self, document_path, content, format_detected):
        """Crea un reporte detallado del análisis"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
=== REPORTE DE ANÁLISIS ===
Archivo: {document_path}
Fecha: {timestamp}
Formato detectado: {format_detected}
Longitud del contenido: {len(content)} caracteres

=== PRIMERAS 500 CARACTERES ===
{content[:500]}...

=== ÚLTIMAS 500 CARACTERES ===
...{content[-500:]}
"""
        return report
    
    def _save_results(self, document_path, content, report):
        """Guarda los resultados en archivos"""
        os.makedirs("results", exist_ok=True)
        
        filename = os.path.basename(document_path).split('.')[0]
        
        # Guardar contenido completo
        with open(f"results/{filename}_content.txt", "w", encoding="utf-8") as f:
            f.write(content)
        
        # Guardar reporte
        with open(f"results/{filename}_report.txt", "w", encoding="utf-8") as f:
            f.write(report)

def main():
    """Función principal para ejecutar las pruebas"""
    tester = DocumentIntelligenceTest()
    
    # Documentos de prueba
    test_documents = [
        "test_documents/Azure AI Agents.pdf",
        "test_documents/Azure ARC SQL.pdf"
    ]
    
    results = []
    
    for doc_path in test_documents:
        if os.path.exists(doc_path):
            result = tester.analyze_document(doc_path)
            results.append((doc_path, result))
        else:
            print(f"⚠️ Documento no encontrado: {doc_path}")
    
    print(f"\n🎯 Pruebas completadas. Resultados guardados en carpeta 'results/'")

if __name__ == "__main__":
    main()