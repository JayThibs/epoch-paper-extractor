import os
import sys
import json
from openai import OpenAI
import base64
import yaml

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

def load_questions():
    with open('config/questions.yaml', 'r') as file:
        return yaml.safe_load(file)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def check_figure_relevance(client, image_path, questions):
    base64_image = encode_image(image_path)
    
    prompt = f"""Analyze this figure from an academic ML paper. Determine if it's relevant to answering any of these questions:

{', '.join(questions)}

Respond with 'Relevant' or 'Not relevant' followed by a brief explanation."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            }
        ],
        max_tokens=100
    )
    
    return response.choices[0].message.content.strip().lower().startswith("relevant")

def extract_information(client, image_path, questions):
    base64_image = encode_image(image_path)
    
    prompt = f"""Analyze this figure from an academic ML paper and answer the following questions if possible:

{', '.join(questions)}

Provide concise answers and specify which question(s) you're answering."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def test_gpt4_vision_extraction(arxiv_id, output_folder):
    # Set up OpenAI client
    client = OpenAI()
    
    # Load questions
    questions = load_questions()
    
    # Get paths
    output_pdf_folder = os.path.join(output_folder, arxiv_id)
    images_folder = os.path.join(output_pdf_folder, "images")
    metadata_path = os.path.join(output_pdf_folder, "figure_metadata.json")
    
    # Check if extraction has been done
    if not os.path.exists(metadata_path):
        print(f"Figure extraction has not been performed for {arxiv_id}. Please run test_figure_extraction.py first.")
        return
    
    # Load existing figure metadata
    with open(metadata_path, "r") as f:
        figures = json.load(f)
    
    for figure in figures:
        image_filename = f"page_{figure['page']}.png"
        image_path = os.path.join(images_folder, image_filename)
        
        # Check relevance using GPT-4o-mini
        if check_figure_relevance(client, image_path, questions):
            # Extract information using GPT-4o
            info = extract_information(client, image_path, questions)
            print(f"Image: {image_filename}")
            print(f"Description: {info}")
            print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_vision_info_extraction.py <arxiv_id>")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'output'))
    
    test_gpt4_vision_extraction(arxiv_id, output_folder)