import anthropic

class TextAnalyzer:
    def __init__(self, anthropic_api_key):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

    def analyze(self, text):
        prompt = """
        Analyze the following text from an academic paper about an AI model. 
        Extract key information about the model's architecture, training process, performance, and other notable characteristics.
        Provide a concise summary (max 100 words) that can be used to answer specific questions later.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=200,
            temperature=0,
            system="You are an AI assistant tasked with extracting concise information about AI models from academic papers. Provide brief, factual summaries.",
            messages=[
                {"role": "user", "content": prompt.format(text=text)}
            ]
        )
        return response.content[0].text

    def answer_questions(self, summary, questions):
        responses = {}
        for question in questions:
            prompt = f"""
            Based on the following summary of an AI model paper, answer this question concisely:
            {question}

            Provide a brief answer (1-2 sentences) and highlight the most relevant piece of text from the summary in quotes.

            Summary: {summary}
            """
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=100,
                temperature=0,
                system="You are an AI assistant tasked with providing brief, factual answers about AI models based on summarized information from academic papers.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            responses[question] = response.content[0].text
        return responses