import base64
from openai import OpenAI
from PIL import Image

class ImageAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze(self, image_paths):
        valid_images = []
        for _, path in image_paths:
            try:
                with Image.open(path) as img:
                    img.verify()
                base64_image = self.encode_image(path)
                valid_images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }
                })
            except Exception as e:
                print(f"Invalid or corrupted image: {path}. Error: {str(e)}")

        if not valid_images:
            return "No valid images found for analysis."

        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with extracting concise information about AI models from images in academic papers. Provide brief, factual summaries."},
            {"role": "user", "content": [
                {"type": "text", "text": "Analyze these images from an AI model paper. Provide a brief summary (max 100 words) of any relevant information about the model's architecture, training process, performance, or other notable characteristics."},
                *valid_images
            ]}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing images: {str(e)}"

    def answer_questions(self, summary, questions):
        responses = {}
        for question in questions:
            messages = [
                {"role": "system", "content": "You are an AI assistant tasked with answering specific questions about AI models based on summarized information from images in academic papers."},
                {"role": "user", "content": f"Based on the following summary of images from an AI model paper, answer this question concisely: {question}\n\nSummary: {summary}"}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=300
            )
            responses[question] = response.choices[0].message.content
        return responses