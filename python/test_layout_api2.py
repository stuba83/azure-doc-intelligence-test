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
    
    def analyze_document(self, document_path, output_format="default"):
        """
        Analiza un documento con diferentes formatos de salida
        
        Args:
            document_path: Ruta del documento
            output_format: "default", "markdown", "text", "html"
        """
        print(f"\n🔍 Analizando: {document_path}")
        print(f"📋 Formato solicitado: {output_format}")
        
        try:
            with open(document_path, "rb") as f:
                # Configurar parámetros según formato deseado
                analyze_params = {
                    "model_id": "prebuilt-layout",
                    "analyze_request": f,
                    "content_type": "application/octet-stream"
                }
                
                # Agregar parámetros específicos según formato
                if output_format == "markdown":
                    analyze_params["output_content_format"] = "markdown"
                elif output_format == "text":
                    analyze_params["output_content_format"] = "text"
                elif output_format == "html":
                    # Algunas versiones del API soportan HTML
                    analyze_params["output_content_format"] = "html"
                
                print("⏳ Enviando solicitud a Azure...")
                try:
                    poller = self.client.begin_analyze_document(**analyze_params)
                except Exception as param_error:
                    print(f"⚠️ Error con parámetros específicos: {param_error}")
                    print("🔄 Intentando con parámetros por defecto...")
                    # Fallback a parámetros por defecto
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
            report = self._create_report(document_path, content, format_detected, output_format)
            
            # Guardar resultados
            self._save_results(document_path, content, report, output_format)
            
            print(f"✅ Análisis completado:")
            print(f"   Formato solicitado: {output_format}")
            print(f"   Formato detectado: {format_detected}")
            return result
            
        except Exception as e:
            print(f"❌ Error procesando {document_path}: {e}")
            return None
    
    def _detect_format(self, content):
        """Detecta si el contenido es HTML, Markdown o texto plano"""
        content_lower = content.lower()
        
        # Detectar HTML
        html_indicators = ['<html>', '<div>', '<p>', '<table>', '<tr>', '<td>', '<span>', '<h1>', '<h2>']
        html_count = sum(1 for indicator in html_indicators if indicator in content_lower)
        
        # Detectar Markdown
        markdown_indicators = ['# ', '## ', '### ', '**', '*', '- ', '1. ', '|', '```']
        markdown_count = sum(1 for indicator in markdown_indicators if indicator in content)
        
        # Detectar JSON
        json_indicators = ['{', '}', '":', '["', '"]']
        json_count = sum(1 for indicator in json_indicators if indicator in content)
        
        if html_count > 0:
            return f"HTML (indicadores: {html_count})"
        elif markdown_count > 2:
            return f"Markdown (indicadores: {markdown_count})"
        elif json_count > 3:
            return f"JSON (indicadores: {json_count})"
        else:
            return "Texto plano"
    
    def _create_report(self, document_path, content, format_detected, requested_format):
        """Crea un reporte detallado del análisis"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
=== REPORTE DE ANÁLISIS ===
Archivo: {document_path}
Fecha: {timestamp}
Formato solicitado: {requested_format}
Formato detectado: {format_detected}
Longitud del contenido: {len(content)} caracteres

=== ANÁLISIS DE CONTENIDO ===
"""
        
        # Análisis específico por formato
        if "HTML" in format_detected:
            report += "✅ RESULTADO: Azure devolvió HTML\n"
            report += f"   - Etiquetas HTML encontradas\n"
        elif "Markdown" in format_detected:
            report += "✅ RESULTADO: Azure devolvió Markdown\n"
            report += f"   - Sintaxis Markdown encontrada\n"
        elif "JSON" in format_detected:
            report += "✅ RESULTADO: Azure devolvió JSON\n"
            report += f"   - Estructura JSON encontrada\n"
        else:
            report += "ℹ️ RESULTADO: Texto plano o formato no identificado\n"
        
        report += f"""
=== MUESTRA DEL CONTENIDO ===
PRIMERAS 500 CARACTERES:
{content[:500]}...

ÚLTIMAS 500 CARACTERES:
...{content[-500:]}

=== VERIFICACIÓN MANUAL ===
Revisa el archivo completo para confirmar el formato.
"""
        return report
    
    def _save_results(self, document_path, content, report, output_format):
        """Guarda los resultados en archivos"""
        os.makedirs("results", exist_ok=True)
        
        filename = os.path.basename(document_path).split('.')[0]
        
        # Guardar contenido completo con sufijo del formato
        content_file = f"results/{filename}_{output_format}_content.md"
        with open(content_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Guardar reporte
        report_file = f"results/{filename}_{output_format}_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"💾 Archivos guardados:")
        print(f"   - {content_file}")
        print(f"   - {report_file}")

    def run_format_comparison(self, document_path):
        """Ejecuta el mismo documento con diferentes formatos para comparar"""
        print(f"\n🔬 COMPARACIÓN DE FORMATOS para: {document_path}")
        print("=" * 60)
        
        formats_to_test = ["default", "markdown", "text", "html"]
        results = {}
        
        for fmt in formats_to_test:
            print(f"\n--- Probando formato: {fmt} ---")
            result = self.analyze_document(document_path, fmt)
            results[fmt] = result
            
        print(f"\n📊 RESUMEN DE COMPARACIÓN:")
        print("=" * 60)
        for fmt, result in results.items():
            if result:
                format_detected = self._detect_format(result.content)
                print(f"{fmt:10} -> {format_detected}")
            else:
                print(f"{fmt:10} -> ERROR")
        
        return results

def main():
    """Función principal para ejecutar las pruebas"""
    tester = DocumentIntelligenceTest()
    
    # Documentos de prueba
    test_documents = [
        "test_documents/Azure AI Agents.pdf",
        "test_documents/Azure ARC SQL.pdf"
    ]
    
    print("🚀 INICIANDO PRUEBAS DE AZURE DOCUMENT INTELLIGENCE")
    print("=" * 60)
    
    # Opción 1: Probar un documento con todos los formatos
    available_docs = [doc for doc in test_documents if os.path.exists(doc)]
    
    if available_docs:
        print("\n🎯 MODO: Comparación de formatos")
        first_doc = available_docs[0]
        tester.run_format_comparison(first_doc)
    else:
        print("⚠️ No se encontraron documentos de prueba en test_documents/")
        print("   Agrega algunos archivos PDF para continuar.")
        return
    
    # Opción 2: Probar todos los documentos con formato por defecto
    print(f"\n🎯 MODO: Análisis con formato por defecto")
    print("=" * 60)
    
    for doc_path in available_docs:
        tester.analyze_document(doc_path, "default")
    
    print(f"\n✅ PRUEBAS COMPLETADAS")
    print("📁 Revisa la carpeta 'results/' para ver todos los archivos generados")

if __name__ == "__main__":
    main()