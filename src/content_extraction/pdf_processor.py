import PyMuPDF as fitz 
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import torch
import json
import PyPDF2
import pytesseract
from typing import List, Tuple

def get_device():
    if torch.backends.mps.is_available():
        return torch.device('mps')
    elif torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')

def convert_pdf_to_images(pdf_path: str, output_folder: str) -> List[str]:
    pages = convert_from_path(pdf_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    image_paths = []
    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f'page_{i+1}.png')
        page.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.model = AutoModelForCausalLM.from_pretrained("yifeihu/TFT-ID-1.0", trust_remote_code=True)
        self.processor = AutoProcessor.from_pretrained("yifeihu/TFT-ID-1.0", trust_remote_code=True)
        self.device = get_device()
        self.model.to(self.device)
        self.pdf_reader = PyPDF2.PdfReader(self.pdf_path)
        self.is_scanned = self._check_if_scanned()

    def _check_if_scanned(self) -> bool:
        # Check the first few pages for meaningful text
        for i in range(min(3, len(self.pdf_reader.pages))):
            text = self.pdf_reader.pages[i].extract_text().strip()
            if len(text) > 100:  # Arbitrary threshold
                return False
        return True

    def extract_content(self) -> Tuple[str, List[Tuple[int, np.ndarray]], List[dict]]:
        text = self._extract_text()
        images, figures = self._extract_images_and_figures()
        return text, images, figures

    def _extract_text(self) -> str:
        if not self.is_scanned:
            return "\n".join(page.extract_text() for page in self.pdf_reader.pages)
        else:
            # Use OCR for scanned PDFs
            text = ""
            temp_folder = f'temp_{os.path.splitext(os.path.basename(self.pdf_path))[0]}'
            image_paths = convert_pdf_to_images(self.pdf_path, temp_folder)
            for image_path in image_paths:
                text += pytesseract.image_to_string(Image.open(image_path)) + "\n"
            # Clean up temporary files
            for image_path in image_paths:
                os.remove(image_path)
            os.rmdir(temp_folder)
            return text

    def _extract_images_and_figures(self) -> Tuple[List[Tuple[int, np.ndarray]], List[dict]]:
        images = []
        figures = []
        temp_folder = f'temp_{os.path.splitext(os.path.basename(self.pdf_path))[0]}'
        image_paths = convert_pdf_to_images(self.pdf_path, temp_folder)
        
        for i, image_path in enumerate(image_paths):
            page = Image.open(image_path)
            np_image = np.array(page)
            np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            
            inputs = self.processor(text=["<OD>"], images=[page], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                generated_ids = self.model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    do_sample=False,
                    num_beams=3
                )
            
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = self.processor.post_process_generation(generated_text, task="<OD>", image_size=(page.width, page.height))
            
            for k, (bbox, label) in enumerate(zip(parsed_answer['<OD>']['bboxes'], parsed_answer['<OD>']['labels'])):
                if label == 'figure':
                    x1, y1, x2, y2 = map(int, bbox)
                    cropped = np_image[y1:y2, x1:x2]
                    images.append((i+1, cropped))
                    
                    caption = self._extract_caption(i, y2, page.height)
                    
                    figures.append({
                        'page': i+1,
                        'bbox': [x1, y1, x2, y2],
                        'caption': caption
                    })
        
        # Clean up temporary files
        for image_path in image_paths:
            os.remove(image_path)
        os.rmdir(temp_folder)
        
        return images, figures

    def _extract_caption(self, page_num: int, y_start: int, y_end: int) -> str:
        if not self.is_scanned:
            page_text = self.pdf_reader.pages[page_num].extract_text()
            lines = page_text.split('\n')
            
            # Estimate the line containing the figure based on y_start
            start_line = int(y_start / y_end * len(lines))
            
            # Look for lines starting with "Figure" or "Fig." after the estimated start line
            for line in lines[start_line:]:
                if line.strip().lower().startswith(('figure', 'fig.')):
                    return line.strip()
        else:
            # For scanned PDFs, use OCR on the specific area below the figure
            temp_folder = f'temp_{os.path.splitext(os.path.basename(self.pdf_path))[0]}'
            image_paths = convert_pdf_to_images(self.pdf_path, temp_folder)
            page_image = Image.open(image_paths[page_num])
            
            # Crop the image to the area below the figure
            caption_area = page_image.crop((0, y_start, page_image.width, y_end))
            
            # Use OCR to extract text from the cropped area
            caption_text = pytesseract.image_to_string(caption_area)
            
            # Clean up temporary files
            for image_path in image_paths:
                os.remove(image_path)
            os.rmdir(temp_folder)
            
            # Clean up the extracted text (remove newlines, extra spaces)
            return ' '.join(caption_text.split())
        
        # If no caption found, return an empty string
        return ""