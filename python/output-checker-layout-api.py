import os
import sys
from datetime import datetime
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentIntelligenceTest:
    def __init__(self):
        self.endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
        
        if not self.endpoint or not self.key:
            raise ValueError("Missing environment variables. Check the .env file")
        
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint, 
            credential=AzureKeyCredential(self.key)
        )
    
    def analyze_document(self, document_path, output_format="default"):
        """
        Analyzes a document with different output formats
        
        Args:
            document_path: Document path
            output_format: "default", "markdown", "text", "html"
        """
        print(f"\n🔍 Analyzing: {document_path}")
        print(f"📋 Requested format: {output_format}")
        
        try:
            with open(document_path, "rb") as f:
                # Configure parameters according to desired format
                analyze_params = {
                    "model_id": "prebuilt-layout",
                    "analyze_request": f,
                    "content_type": "application/octet-stream"
                }
                
                # Add specific parameters according to format
                if output_format == "markdown":
                    analyze_params["output_content_format"] = "markdown"
                elif output_format == "text":
                    analyze_params["output_content_format"] = "text"
                elif output_format == "html":
                    # Some API versions support HTML
                    analyze_params["output_content_format"] = "html"
                
                print("⏳ Sending request to Azure...")
                try:
                    poller = self.client.begin_analyze_document(**analyze_params)
                except Exception as param_error:
                    print(f"⚠️ Error with specific parameters: {param_error}")
                    print("🔄 Trying with default parameters...")
                    # Fallback to default parameters
                    poller = self.client.begin_analyze_document(
                        "prebuilt-layout",
                        analyze_request=f,
                        content_type="application/octet-stream"
                    )
            
            print("⏳ Processing document...")
            result = poller.result()
            
            # Content analysis
            content = result.content
            format_detected = self._detect_format(content)
            
            # Create report
            report = self._create_report(document_path, content, format_detected, output_format)
            
            # Save results
            self._save_results(document_path, content, report, output_format)
            
            print(f"✅ Analysis completed:")
            print(f"   Requested format: {output_format}")
            print(f"   Detected format: {format_detected}")
            return result
            
        except Exception as e:
            print(f"❌ Error processing {document_path}: {e}")
            return None
    
    def _detect_format(self, content):
        """Detects if content is HTML, Markdown or plain text"""
        content_lower = content.lower()
        
        # Detect HTML
        html_indicators = ['<html>', '<div>', '<p>', '<table>', '<tr>', '<td>', '<span>', '<h1>', '<h2>']
        html_count = sum(1 for indicator in html_indicators if indicator in content_lower)
        
        # Detect Markdown
        markdown_indicators = ['# ', '## ', '### ', '**', '*', '- ', '1. ', '|', '```']
        markdown_count = sum(1 for indicator in markdown_indicators if indicator in content)
        
        # Detect JSON
        json_indicators = ['{', '}', '":', '["', '"]']
        json_count = sum(1 for indicator in json_indicators if indicator in content)
        
        if html_count > 0:
            return f"HTML (indicators: {html_count})"
        elif markdown_count > 2:
            return f"Markdown (indicators: {markdown_count})"
        elif json_count > 3:
            return f"JSON (indicators: {json_count})"
        else:
            return "Plain text"
    
    def _create_report(self, document_path, content, format_detected, requested_format):
        """Creates a detailed analysis report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
=== ANALYSIS REPORT ===
File: {document_path}
Date: {timestamp}
Requested format: {requested_format}
Detected format: {format_detected}
Content length: {len(content)} characters

=== CONTENT ANALYSIS ===
"""
        
        # Specific analysis by format
        if "HTML" in format_detected:
            report += "✅ RESULT: Azure returned HTML\n"
            report += f"   - HTML tags found\n"
        elif "Markdown" in format_detected:
            report += "✅ RESULT: Azure returned Markdown\n"
            report += f"   - Markdown syntax found\n"
        elif "JSON" in format_detected:
            report += "✅ RESULT: Azure returned JSON\n"
            report += f"   - JSON structure found\n"
        else:
            report += "ℹ️ RESULT: Plain text or unidentified format\n"
        
        report += f"""
=== CONTENT SAMPLE ===
FIRST 500 CHARACTERS:
{content[:500]}...

LAST 500 CHARACTERS:
...{content[-500:]}

=== MANUAL VERIFICATION ===
Check the complete file to confirm the format.
"""
        return report
    
    def _save_results(self, document_path, content, report, output_format):
        """Saves results to files"""
        os.makedirs("results", exist_ok=True)
        
        filename = os.path.basename(document_path).split('.')[0]
        
        # Save complete content with format suffix
        content_file = f"results/{filename}_{output_format}_content.md"
        with open(content_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Save report
        report_file = f"results/{filename}_{output_format}_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"💾 Files saved:")
        print(f"   - {content_file}")
        print(f"   - {report_file}")

    def run_format_comparison(self, document_path):
        """Runs the same document with different formats for comparison"""
        print(f"\n🔬 FORMAT COMPARISON for: {document_path}")
        print("=" * 60)
        
        formats_to_test = ["default", "markdown", "text", "html"]
        results = {}
        
        for fmt in formats_to_test:
            print(f"\n--- Testing format: {fmt} ---")
            result = self.analyze_document(document_path, fmt)
            results[fmt] = result
            
        print(f"\n📊 COMPARISON SUMMARY:")
        print("=" * 60)
        for fmt, result in results.items():
            if result:
                format_detected = self._detect_format(result.content)
                print(f"{fmt:10} -> {format_detected}")
            else:
                print(f"{fmt:10} -> ERROR")
        
        return results

def main():
    """Main function to run the tests"""
    tester = DocumentIntelligenceTest()
    
    # Test documents
    test_documents = [
        "test_documents/Azure AI Agents.pdf",
        "test_documents/Azure ARC SQL.pdf"
    ]
    
    print("🚀 STARTING AZURE DOCUMENT INTELLIGENCE TESTS")
    print("=" * 60)
    
    # Option 1: Test one document with all formats
    available_docs = [doc for doc in test_documents if os.path.exists(doc)]
    
    if available_docs:
        print("\n🎯 MODE: Format comparison")
        first_doc = available_docs[0]
        tester.run_format_comparison(first_doc)
    else:
        print("⚠️ No test documents found in test_documents/")
        print("   Add some PDF files to continue.")
        return
    
    # Option 2: Test all documents with default format
    print(f"\n🎯 MODE: Analysis with default format")
    print("=" * 60)
    
    for doc_path in available_docs:
        tester.analyze_document(doc_path, "default")
    
    print(f"\n✅ TESTS COMPLETED")
    print("📁 Check the 'results/' folder to see all generated files")

if __name__ == "__main__":
    main()