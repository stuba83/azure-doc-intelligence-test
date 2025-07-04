using Azure;
using Azure.AI.DocumentIntelligence;
using DotNetEnv;
using System;
using System.IO;
using System.Threading.Tasks;

class Program
{
    private static DocumentIntelligenceClient? client;
    private static string? endpoint;
    private static string? key;

    static async Task Main(string[] args)
    {
        // Cargar variables de entorno
        Env.Load();
        
        endpoint = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_ENDPOINT");
        key = Environment.GetEnvironmentVariable("DOCUMENT_INTELLIGENCE_KEY");

        if (string.IsNullOrEmpty(endpoint) || string.IsNullOrEmpty(key))
        {
            Console.WriteLine("‚ùå Error: Faltan variables de entorno");
            return;
        }

        client = new DocumentIntelligenceClient(new Uri(endpoint), new AzureKeyCredential(key));

        string[] testDocuments = {
            "test_documents/sample.pdf",
            "test_documents/document_with_tables.pdf",
            "test_documents/complex_document.pdf"
        };

        foreach (string docPath in testDocuments)
        {
            if (File.Exists(docPath))
            {
                await TestLayoutAPI(docPath);
            }
            else
            {
                Console.WriteLine($"‚ö†Ô∏è Documento no encontrado: {docPath}");
            }
        }

        Console.WriteLine("\nÌæØ Pruebas completadas");
    }

    static async Task TestLayoutAPI(string documentPath)
    {
        Console.WriteLine($"\nÌ¥ç Analizando: {documentPath}");
        
        try
        {
            using var stream = File.OpenRead(documentPath);
            
            Console.WriteLine("‚è≥ Procesando documento...");
            var operation = await client!.AnalyzeDocumentAsync(
                WaitUntil.Completed, 
                "prebuilt-layout", 
                stream
            );
            
            var result = operation.Value;
            string content = result.Content;
            
            // Detectar formato
            string formatDetected = DetectFormat(content);
            
            // Crear reporte
            string report = CreateReport(documentPath, content, formatDetected);
            
            // Guardar resultados
            await SaveResults(documentPath, content, report);
            
            Console.WriteLine($"‚úÖ An√°lisis completado: {formatDetected}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"‚ùå Error: {ex.Message}");
        }
    }

    static string DetectFormat(string content)
    {
        string contentLower = content.ToLower();
        
        // Detectar HTML
        string[] htmlIndicators = {"<html>", "<div>", "<p>", "<table>", "<tr>", "<td>", "<span>"};
        int htmlCount = 0;
        foreach (var indicator in htmlIndicators)
        {
            if (contentLower.Contains(indicator)) htmlCount++;
        }
        
        // Detectar Markdown
        string[] markdownIndicators = {"# ", "## ", "### ", "**", "*", "- ", "1. ", "|"};
        int markdownCount = 0;
        foreach (var indicator in markdownIndicators)
        {
            if (content.Contains(indicator)) markdownCount++;
        }
        
        if (htmlCount > 0)
            return $"HTML (indicadores: {htmlCount})";
        else if (markdownCount > 2)
            return $"Markdown (indicadores: {markdownCount})";
        else
            return "Texto plano";
    }

    static string CreateReport(string documentPath, string content, string formatDetected)
    {
        string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        
        return $@"
=== REPORTE DE AN√ÅLISIS ===
Archivo: {documentPath}
Fecha: {timestamp}
Formato detectado: {formatDetected}
Longitud del contenido: {content.Length} caracteres

=== PRIMERAS 500 CARACTERES ===
{content.Substring(0, Math.Min(500, content.Length))}...

=== √öLTIMAS 500 CARACTERES ===
...{content.Substring(Math.Max(0, content.Length - 500))}
";
    }

    static async Task SaveResults(string documentPath, string content, string report)
    {
        Directory.CreateDirectory("results");
        
        string filename = Path.GetFileNameWithoutExtension(documentPath);
        
        // Guardar contenido completo
        await File.WriteAllTextAsync($"results/{filename}_content.txt", content);
        
        // Guardar reporte
        await File.WriteAllTextAsync($"results/{filename}_report.txt", report);
    }
}
