from openai import OpenAI

class ImageAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def analyze(self, image_paths):
        messages = [
            {"role": "system", "content": "You are an AI assistant tasked with extracting and summarizing information about AI models from images in academic papers."},
            {"role": "user", "content": [
                {"type": "text", "text": "Analyze these images from an AI model paper. Provide a detailed summary of any relevant information about the model's architecture, training process, performance, or other notable characteristics."},
                *[{"type": "image_url", "image_url": {"url": f"file://{path}"}} for _, path in image_paths]
            ]}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content

    def answer_questions(self, summary, questions):
        responses = {}
        for question in questions:
            messages = [
                {"role": "system", "content": "You are an AI assistant tasked with answering specific questions about AI models based on summarized information from images in academic papers."},
                {"role": "user", "content": f"Based on the following summary of images from an AI model paper, answer this question: {question}\n\nSummary: {summary}"}
            ]
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=300
            )
            responses[question] = response.choices[0].message.content
        return responses