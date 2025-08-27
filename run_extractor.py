import os
from utils.extractor import DMPExtractor

extractor = DMPExtractor()
input_dir = "test_samples"
output_dir = "output"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    filepath = os.path.join(input_dir, filename)
    if filename.lower().endswith(".docx"):
        result = extractor.process_docx(filepath, output_dir)
        print(result)
    elif filename.lower().endswith(".pdf"):
        result = extractor.process_pdf(filepath, output_dir)
        print(result)
