from pathlib import Path
from .pdf_parser import IPCPDFParser
from .ipc_structurer import IPCStructurer

def run_ingestion_pipeline(pdf_path: str, output_dir: str):
    """
    Complete pipeline: PDF -> Structured JSON
    """
    print("🚀 Starting IPC PDF ingestion pipeline...")
    
    # Step 1: Parse PDF
    print("📄 Parsing PDF...")
    parser = IPCPDFParser(pdf_path)
    pages = parser.extract_sections()
    
    # Save raw text for inspection
    raw_dir = Path(output_dir) / 'raw'
    parser.save_raw_text(raw_dir)
    print(f"   Raw text saved to {raw_dir}")
    
    # Step 2: Structure sections
    print("🏗 Structuring IPC sections...")
    structurer = IPCStructurer()
    sections = structurer.parse_sections(pages)
    
    # Step 3: Save to JSON
    json_path = Path(output_dir) / 'processed' / 'ipc_sections.json'
    json_path.parent.mkdir(parents=True, exist_ok=True)
    structurer.save_to_json(json_path)
    
    # Summary
    print("\n📊 Summary:")
    print(f"   Total sections extracted: {len(sections)}")
    print(f"   Valid sections: {len(structurer.validate_sections())}")
    print(f"   JSON saved to: {json_path}")
    
    return json_path

if __name__ == "__main__":
    # Example usage
    pdf_path = "data/raw/IPC.pdf"
    output_dir = "data/"
    
    run_ingestion_pipeline(pdf_path, output_dir)