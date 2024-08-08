import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from content_extraction.pdf_processor import PDFProcessor

def download_pdf(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded PDF to {save_path}")
    else:
        raise Exception(f"Failed to download PDF. Status code: {response.status_code}")

def visualize_figures(image, figures, output_folder, page_num):
    """
    Create a visualization of all figures on the page.
    """
    if CV2_AVAILABLE:
        full_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    else:
        full_img = Image.fromarray(image)

    draw = ImageDraw.Draw(full_img)

    # Use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except IOError:
        font = ImageFont.load_default()

    for i, figure in enumerate(figures):
        bbox = figure['bbox']
        caption = figure.get('caption', f'Figure {i+1}')

        # Draw bounding box on full image (without red lines)
        draw.rectangle(bbox, outline=None, width=2)

        # Draw caption on full image
        draw.text((bbox[0], bbox[1] - 20), caption[:50], font=font, fill="black")

    # Save the full page image with bounding boxes and captions
    output_path = os.path.join(output_folder, f"page_{page_num}.png")
    full_img.save(output_path)
    print(f"Saved visualization of figures on page {page_num} to {output_path}")

def test_figure_extraction(arxiv_id, raw_data_folder, output_folder):
    """
    Test figure extraction on a given arXiv ID PDF and save visualizations.
    """
    # Create folders
    pdf_folder = os.path.join(raw_data_folder, arxiv_id)
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, f"{arxiv_id}.pdf")
    
    # Download PDF if it doesn't exist
    if not os.path.exists(pdf_path):
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        download_pdf(url, pdf_path)
    
    # Create output folders
    output_pdf_folder = os.path.join(output_folder, arxiv_id)
    images_folder = os.path.join(output_pdf_folder, "images")
    os.makedirs(images_folder, exist_ok=True)
    
    processor = PDFProcessor(pdf_path)
    text, images, figures = processor.extract_content()
    
    print(f"Extracted {len(figures)} figures from the PDF.")
    
    for page_num, image in images:
        page_figures = [fig for fig in figures if fig['page'] == page_num]
        visualize_figures(image, page_figures, images_folder, page_num)
    
    # Save extracted text
    text_path = os.path.join(output_pdf_folder, "extracted_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved extracted text to {text_path}")
    
    # Save figure metadata
    import json
    metadata_path = os.path.join(output_pdf_folder, "figure_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(figures, f, indent=2)
    print(f"Saved figure metadata to {metadata_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_figure_extraction.py <arxiv_id>")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    raw_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
    output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'output'))
    
    test_figure_extraction(arxiv_id, raw_data_folder, output_folder)