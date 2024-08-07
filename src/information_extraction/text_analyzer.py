import anthropic

class TextAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def analyze(self, text):
        prompt = """
        Analyze the following text from an academic paper about an AI model. 
        Extract and summarize key information about the model's architecture, 
        training process, performance, and any other notable characteristics. 
        Provide a detailed summary that can be used to answer specific questions later.

        Text: {text}
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0,
            system="You are an AI assistant tasked with extracting and summarizing information about AI models from academic papers.",
            messages=[
                {"role": "user", "content": prompt.format(text=text)}
            ]
        )
        return response.content[0].text

    def answer_questions(self, summary, questions):
        responses = {}
        for question in questions:
            prompt = f"""
            Based on the following summary of an AI model paper, answer this question:
            {question}

            Summary: {summary}
            """
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=500,
                temperature=0,
                system="You are an AI assistant tasked with answering specific questions about AI models based on summarized information from academic papers.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            responses[question] = response.content[0].text
        return responses