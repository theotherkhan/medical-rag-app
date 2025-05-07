import os
from typing import Optional, List, Dict
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

    async def answer_question(self, question: str, context_documents: List[Dict]) -> Optional[str]:
        """
        Answer a question using the provided context documents.
        
        Args:
            question (str): The question to answer
            context_documents (List[Dict]): List of relevant documents with their content
            
        Returns:
            Optional[str]: The generated answer, or None if the API call fails
        """
        try:
            # Prepare context from documents
            context = "\n\n".join([
                f"Document {i+1}:\nTitle: {doc['title']}\nContent: {doc['content']}"
                for i, doc in enumerate(context_documents)
            ])

            # Create the prompt
            messages = [
                {"role": "system", "content": """You are a medical assistant. Answer the user's question based on the provided medical documents.
                If the answer cannot be found in the documents, say so.
                Be concise but thorough in your response.
                Include relevant details from the documents to support your answer."""},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]

            # Generate the answer
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return None

    async def extract_structured(self, prompt: str) -> Optional[str]:
        """
        Extract structured data from a medical note using OpenAI's GPT model.
        
        Args:
            prompt (str): The prompt to extract structured data from    
        Returns:
            Optional[str]: The extracted structured data, or None if the API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a medical data extraction assistant. Extract structured data from medical notes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            print("\n\nRESPONSE: ", response)

            return response #.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return None
        
# Create a singleton instance
llm_service = LLMService()