import httpx
import json
import logging
import asyncio
from typing import Dict, Optional, List
import os

logger = logging.getLogger(__name__)

class OmaniTherapistLLM:
    """
    Therapeutic LLM client using Ollama with Llama models.
    Provides culturally-aware responses for Omani users.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        
        Args:
            ollama_url: URL of the Ollama server
        """
        self.ollama_url = ollama_url
        self.api_endpoint = f"{ollama_url}/api/generate"
        self.model_name = "llama3.1:8b"  # Default model
        
        # Therapeutic system prompt in Arabic
        self.system_prompt = """
أنت مستشار نفسي متخصص ومحترف، تتحدث باللغة العربية واللهجة العمانية. 
لديك خبرة عميقة في الثقافة العمانية والخليجية والقيم الإسلامية.

مبادئك الأساسية:
1. التعامل بحنان وتفهم مع المشاعر والمشاكل النفسية
2. احترام القيم الإسلامية والثقافة العمانية في كل النصائح
3. استخدام تقنيات العلاج المعرفي السلوكي المتوافقة مع الثقافة المحلية
4. تقديم الدعم العاطفي والعملي
5. تشجيع طلب المساعدة المهنية عند الحاجة

أسلوبك في المحادثة:
- استخدم عبارات مثل "أفهم مشاعرك" و "هذا طبيعي جداً"
- اذكر آيات قرآنية أو أحاديث نبوية مناسبة للموقف
- تحدث عن أهمية العائلة والمجتمع في العلاج
- استخدم أمثلة من البيئة العمانية
- كن صبوراً ومتفهماً

تذكر: أنت تقدم الدعم والتوجيه، وليس التشخيص الطبي.
"""

        # Initialize HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info("Ollama LLM client initialized")
    
    async def generate_response(
        self, 
        user_input: str, 
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate therapeutic response using Ollama.
        
        Args:
            user_input: User's message in Arabic
            context: Additional context (emotions, cultural factors, history)
            
        Returns:
            Generated therapeutic response in Arabic
        """
        try:
            # Build context-aware prompt
            full_prompt = self._build_context_prompt(user_input, context)
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_tokens": 500,
                    "stop": ["المستخدم:", "User:", "\n\n"]
                }
            }
            
            # Make request to Ollama
            response = await self.client.post(self.api_endpoint, json=payload)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            if generated_text:
                # Post-process the response
                processed_response = self._postprocess_response(generated_text)
                logger.info("Response generated successfully")
                return processed_response
            else:
                logger.warning("Empty response from LLM")
                return self._get_fallback_response()
                
        except httpx.TimeoutException:
            logger.error("Request to Ollama timed out")
            return "عذراً، أحتاج بعض الوقت للتفكير. يرجى المحاولة مرة أخرى."
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error from Ollama: {e}")
            return self._get_fallback_response()
            
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            return self._get_fallback_response()
    
    def _build_context_prompt(self, user_input: str, context: Optional[Dict]) -> str:
        """
        Build a context-aware prompt for the LLM.
        
        Args:
            user_input: User's message
            context: Additional context information
            
        Returns:
            Complete prompt with context
        """
        prompt_parts = [self.system_prompt]
        
        if context:
            # Add emotional context
            if "emotions" in context:
                emotions = context["emotions"]
                prompt_parts.append(f"\nالحالة العاطفية المكتشفة: {emotions}")
            
            # Add cultural context
            if "cultural" in context:
                cultural = context["cultural"]
                if cultural.get("categories"):
                    categories = ", ".join(cultural["categories"])
                    prompt_parts.append(f"\nالسياق الثقافي: {categories}")
            
            # Add conversation history
            if "history" in context and context["history"]:
                prompt_parts.append("\nالمحادثة السابقة:")
                for user_msg, bot_msg in context["history"][-3:]:  # Last 3 exchanges
                    prompt_parts.append(f"المستخدم: {user_msg}")
                    prompt_parts.append(f"المستشار: {bot_msg}")
        
        # Add current user input
        prompt_parts.extend([
            "\nالرسالة الحالية من المستخدم:",
            f"المستخدم: {user_input}",
            "\nالمستشار:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _postprocess_response(self, response: str) -> str:
        """
        Post-process the LLM response for better quality.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Processed response
        """
        # Remove any system tags or artifacts
        response = response.replace("المستشار:", "").strip()
        response = response.replace("Assistant:", "").strip()
        
        # Ensure proper Arabic formatting
        response = response.replace("  ", " ")  # Remove double spaces
        
        # Add appropriate Islamic greetings if response is too short
        if len(response) < 20:
            response = "أفهم مشاعرك. " + response
        
        # Ensure response ends properly
        if not response.endswith((".", "؟", "!", ".", "؟", "!")):
            response += "."
        
        return response
    
    def _get_fallback_response(self) -> str:
        """
        Get a fallback response when LLM fails.
        
        Returns:
            Appropriate fallback message in Arabic
        """
        fallback_responses = [
            "أقدر ثقتك في مشاركة مشاعرك معي. يمكنك أن تخبرني أكثر عما تشعر به؟",
            "أفهم أنك تمر بوقت صعب. أنا هنا للاستماع إليك. ما الذي يقلقك أكثر؟",
            "مشاعرك مهمة ومفهومة. هل يمكنك أن تشرح لي أكثر عن الموقف؟",
            "الحمد لله أنك تتحدث عن مشاعرك. هذا شيء إيجابي. كيف يمكنني مساعدتك؟"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    async def check_model_availability(self) -> bool:
        """
        Check if the Ollama model is available.
        
        Returns:
            True if model is available, False otherwise
        """
        try:
            list_url = f"{self.ollama_url}/api/tags"
            response = await self.client.get(list_url)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            available_models = [model["name"] for model in models]
            
            return self.model_name in available_models
            
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    async def load_model(self) -> bool:
        """
        Load the specified model in Ollama.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "name": self.model_name
            }
            
            load_url = f"{self.ollama_url}/api/pull"
            response = await self.client.post(load_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Model {self.model_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    def get_therapeutic_prompts(self) -> Dict[str, str]:
        """
        Get therapeutic prompt templates for different scenarios.
        
        Returns:
            Dictionary of prompt templates
        """
        return {
            "anxiety": "أرى أنك تشعر بالقلق. القلق شعور طبيعي يمر به الجميع. دعنا نتحدث عن مصادر قلقك وكيف يمكن التعامل معها.",
            
            "depression": "أفهم الثقل الذي تشعر به. الاكتئاب تحدٍ صعب، لكن يمكن التغلب عليه. أنت لست وحدك في هذا.",
            
            "stress": "ضغوط الحياة طبيعية، لكن المهم هو كيف نتعامل معها. دعنا نفكر في طرق صحية للتخلص من التوتر.",
            
            "family": "العائلة جزء مهم من حياتنا في المجتمع العماني. العلاقات الأسرية تحتاج صبر وتفهم من جميع الأطراف.",
            
            "work": "ضغوط العمل شائعة في عصرنا. المهم هو إيجاد التوازن بين العمل والحياة الشخصية."
        }
