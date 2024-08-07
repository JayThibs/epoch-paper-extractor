import anthropic

class ReasoningCalculator:
    def __init__(self):
        self.client = anthropic.Anthropic()

    def reason_and_calculate(self, combined_responses, questions):
        final_answers = {}
        for question, responses in combined_responses.items():
            prompt = f"""
            Question: {question}
            
            Information from text: {responses['text_response']}
            
            Information from images: {responses['image_response']}
            
            Based on this information, provide a final answer to the question. If calculation is needed, show your work. If the information is inconsistent or unclear, explain why.
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0,
                system="You are an AI assistant tasked with reasoning about and calculating final answers for questions about AI models based on extracted information.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            final_answers[question] = response.content[0].text
        return final_answers