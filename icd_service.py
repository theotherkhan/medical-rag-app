import os
import requests
import asyncio
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

class ICDService:
    def __init__(self):
        self.client_id = os.getenv("ICD_CLIENT_ID")
        self.client_secret = os.getenv("ICD_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise ValueError("ICD_CLIENT_ID and ICD_CLIENT_SECRET environment variables must be set")
        
        self.base_url = "https://id.who.int/icd/entity"
        self.token_url = "https://icdaccessmanagement.who.int/connect/token"
        self.access_token = None
        self.token_expiry = 0

    async def get_access_token(self) -> str:
        """
        Get an access token using client credentials.
        Returns the access token string.
        """
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'icdapi_access'
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Set token expiry (subtract 60 seconds for safety margin)
            self.token_expiry = asyncio.get_event_loop().time() + token_data['expires_in'] - 60
            
            return self.access_token
            
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            raise


    async def get_icd_code(self, condition: str) -> Optional[Dict]:
        """
        Get ICD-11 code and description for a medical condition.
        
        Args:
            condition (str): The medical condition to look up
            
        Returns:
            Optional[Dict]: Dictionary containing icd_code and description, or None if not found
        """
        try:
            # Ensure we have a valid access token
            self.access_token = await self.get_access_token()

            print(self.access_token)
            
            # Set up headers with the access token
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Accept-Language": "en",
                "API-version": "v2"
            }
            
            # Search for the condition
            search_url = f"{self.base_url}/search"
            params = {
                "q": condition,
                "useFlexisearch": "true",
                "flatResults": "false",
            }
            
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            
            results = response.json()
            #print("Results: ", results)
            if not results:
                return None
                
            # Get the first result
            first_result = results["destinationEntities"][0]
            print("First result: ", first_result)
            
            # Get detailed information for the code
            #code_url = f"{self.base_url}/{first_result['code']}
            code_url = first_result['id']
            code = code_url.split('/')[-1]
            code_response = requests.get(code_url, headers=headers)
            code_response.raise_for_status()
            
            code_data = code_response.json()
            
            return {
                "icd_code": code,
                "icd_description": code_data.get("title", {}).get("@value", "No description available")
            }
            
        except Exception as e:
            print(f"Error looking up ICD code: {str(e)}")
            return None

async def test_obesity_icd_code():
    """
    Test function to check ICD code lookup for Obesity.
    Run this function to test the ICD code lookup functionality.
    """
    result = await icd_service.get_icd_code("Obesity")
    if result:
        print(f"Found ICD code for Obesity:")
        print(f"Code: {result['icd_code']}")
        print(f"Description: {result['icd_description']}")
    else:
        print("No ICD code found for Obesity")

# Create a singleton instance
icd_service = ICDService()
#token = asyncio.run(icd_service.get_access_token()) 
#asyncio.run(test_obesity_icd_code()) 