import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)

    async def summarize_medical_note(self, text: str) -> Optional[str]:
        """
        Summarize a medical note using OpenAI's GPT model.
        
        Args:
            text (str): The medical note text to summarize
            
        Returns:
            Optional[str]: The summarized text, or None if the API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical assistant. Summarize the following medical note, highlighting key patient information, diagnoses, and treatment plans."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return None

# Create a singleton instance
llm_service = LLMService() 