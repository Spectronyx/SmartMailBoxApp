import logging
import google.genai as genai
from google.genai import types
from django.conf import settings
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Base class for Gemini services.
    Migrated to use the unified google-genai SDK.
    """
    
    def __init__(self, model_name: str = 'gemini-3.0-flash'):
        self.model_name = model_name
        self._client = None
        self._is_configured = False
        
    def _configure(self) -> bool:
        """Initialize the Gemini 3 Client."""
        if self._is_configured:
            return True
            
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            logger.warning(f"GEMINI_API_KEY not set. {self.__class__.__name__} disabled.")
            return False
            
        try:
            # Gemini 3 uses the 'client' pattern rather than global configuration
            self._client = genai.Client(api_key=api_key)
            self._is_configured = True
            logger.info(f"Gemini 3 model '{self.model_name}' ready for {self.__class__.__name__}.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini 3 client: {e}")
            return False

    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Wrapper for generating content. 
        Accepts kwargs to pass thinking_level or temperature.
        """
        if not self._configure():
            return None
            
        try:
            # Set default thinking to 'high' for classification accuracy
            thinking_level = kwargs.get('thinking_level', 'high')
            
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level=thinking_level
                    ),
                    temperature=kwargs.get('temperature', 1.0)
                )
            )
            
            if not response or not response.text:
                logger.warning(f"Empty response from Gemini 3 for {self.__class__.__name__}")
                return None
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini 3 generation failed: {e}")
            return None