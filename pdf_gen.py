import subprocess
import os
import shutil

def convert_to_pdf(input_docx, output_dir):
    """
    Converts DOCX to PDF using headless LibreOffice.
    Returns path to the generated PDF.
    """
    # Ensure output dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Run soffice
    # macOS typical path or reliance on PATH
    # The command 'soffice' was verified to be in PATH via brew link
    
    cmd = [
        "soffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_docx
    ]
    
    print(f"Running conversion: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"PDF Conversion failed: {result.stderr}")
        
    # Filename inference: soffice uses same basename
    basename = os.path.splitext(os.path.basename(input_docx))[0]
    pdf_path = os.path.join(output_dir, basename + ".pdf")
    
    if not os.path.exists(pdf_path):
         raise Exception("PDF file not found after conversion")
         
    return pdf_path
