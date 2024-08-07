import anthropic
from openai import OpenAI
import base64
import requests
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

class PromptingSystem:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.anthropic_client = anthropic.Anthropic()
        self.conversation_history = []

    def extract_information(self, text: str, images: List[str] = None) -> Dict[str, Any]:
        extracted_info = {}
        try:
            self._initialize_conversation(text)
            for field, field_info in MODEL_FIELDS.items():
                if images and field_info.get("requires_image", False):
                    field_value = self._extract_field_info_multimodal(field, field_info, images)
                else:
                    field_value = self._extract_field_info_text(field, field_info)
                extracted_info[field] = field_value
            
            logger.info("Successfully extracted information from text and images")
            return extracted_info
        except Exception as e:
            logger.error(f"Error extracting information: {str(e)}")
            raise

    def _initialize_conversation(self, text: str):
        self.conversation_history = [
            {"role": "system", "content": "You are an AI assistant tasked with extracting specific information about AI models from academic papers and related documents. Please analyze the following text and answer the questions as accurately as possible. If the information is not available or unclear, please state so explicitly."},
            {"role": "user", "content": text}
        ]

    def _extract_field_info_text(self, field: str, field_info: Dict[str, str]) -> Dict[str, Any]:
        prompt = field_info["prompt"]
        response = self._get_claude_response(prompt)
        
        extracted_value = self._parse_response(response, field_info["type"])
        confidence = self._assess_confidence(response)
        
        return {
            "value": extracted_value,
            "confidence": confidence,
            "notes": self._extract_notes(field, response)
        }

    def _extract_field_info_multimodal(self, field: str, field_info: Dict[str, str], images: List[str]) -> Dict[str, Any]:
        prompt = field_info["prompt"]
        response = self._get_gpt4_response(prompt, images)
        
        extracted_value = self._parse_response(response, field_info["type"])
        confidence = self._assess_confidence(response)
        
        return {
            "value": extracted_value,
            "confidence": confidence,
            "notes": self._extract_notes(field, response)
        }

    def _get_claude_response(self, prompt: str) -> str:
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0,
                system="You are an AI assistant tasked with extracting specific information about AI models from academic papers and related documents.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            raise

    def _get_gpt4_response(self, prompt: str, images: List[str]) -> str:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }

            encoded_images = [self._encode_image(img) for img in images]

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            *[{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} for img in encoded_images]
                        ]
                    }
                ],
                "max_tokens": 300
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error getting GPT-4 response: {str(e)}")
            raise

    @staticmethod
    def _encode_image(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _parse_response(self, response: str, field_type: str) -> Union[str, int, float, List[str]]:
        """
        Parse the model's response based on the expected field type.

        Args:
        response (str): The model's response.
        field_type (str): The expected type of the field.

        Returns:
        Union[str, int, float, List[str]]: The parsed value.
        """
        if field_type == "numeric":
            match = re.search(r'\d+(?:\.\d+)?', response)
            return float(match.group()) if match else None
        elif field_type == "categorical":
            return [item.strip() for item in response.split(',')]
        elif field_type == "date":
            match = re.search(r'\d{4}-\d{2}-\d{2}', response)
            return match.group() if match else None
        else:
            return response

    def _assess_confidence(self, response: str) -> str:
        """
        Assess the confidence of the model's response.

        Args:
        response (str): The model's response.

        Returns:
        str: A confidence level (Confident, Likely, Speculative, Unknown).
        """
        if "I'm confident" in response or "The text clearly states" in response:
            return "Confident"
        elif "It's likely" in response or "The text suggests" in response:
            return "Likely"
        elif "It's possible" in response or "The text hints at" in response:
            return "Speculative"
        else:
            return "Unknown"

    def _extract_notes(self, field: str, response: str) -> str:
        """
        Extract any notes or explanations from the model's response.

        Args:
        field (str): The field being extracted.
        response (str): The model's response.

        Returns:
        str: Extracted notes.
        """
        prompt = f"Based on the response for the {field} field, provide any additional notes or explanations that might be relevant."
        notes_response = self._get_model_response(prompt)
        return notes_response

def extract_information_from_text(text: str, images: List[str] = None) -> Dict[str, Any]:
    """
    Extract relevant information from text using the PromptingSystem.

    Args:
    text (str): The text content to analyze.

    Returns:
    Dict[str, Any]: Extracted information organized by field.
    """
    prompting_system = PromptingSystem()
    return prompting_system.extract_information(text, images)