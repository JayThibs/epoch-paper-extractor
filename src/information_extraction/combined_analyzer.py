class CombinedAnalyzer:
    def __init__(self, text_analyzer, image_analyzer):
        self.text_analyzer = text_analyzer
        self.image_analyzer = image_analyzer

    def analyze(self, text, image_paths):
        text_summary = self.text_analyzer.analyze(text)
        image_summary = self.image_analyzer.analyze(image_paths)
        return text_summary, image_summary

    def answer_questions(self, text_summary, image_summary, questions):
        text_responses = self.text_analyzer.answer_questions(text_summary, questions)
        image_responses = self.image_analyzer.answer_questions(image_summary, questions)
        
        combined_responses = {}
        for question in questions:
            combined_responses[question] = {
                'text_response': text_responses[question],
                'image_response': image_responses[question]
            }
        return combined_responses