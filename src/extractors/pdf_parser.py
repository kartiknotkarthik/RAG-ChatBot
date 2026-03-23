import pypdf
import os
import json

def extract_pdf_text(file_path):
    print(f"Extracting text from {file_path}...")
    reader = pypdf.PdfReader(file_path)
    text = ""
    for i, page in enumerate(reader.pages):
        # Only parse first 100 pages for demo/speed if needed, but let's try all
        if i % 50 == 0: print(f"Processing page {i}...")
        text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

if __name__ == "__main__":
    pdf_dir = 'data/raw/pdfs'
    processed_dir = 'data/processed/pdfs'
    os.makedirs(processed_dir, exist_ok=True)
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            text = extract_pdf_text(os.path.join(pdf_dir, filename))
            # Save full text and also chunks
            full_text_path = os.path.join(processed_dir, filename.replace('.pdf', '.txt'))
            with open(full_text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            chunks = chunk_text(text)
            chunks_path = os.path.join(processed_dir, filename.replace('.pdf', '_chunks.json'))
            with open(chunks_path, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=4)
            print(f"Saved text and {len(chunks)} chunks for {filename}")
