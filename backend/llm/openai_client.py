import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AzureOmaniTherapistLLM:

    def __init__(self):
        """Initialize the Azure OpenAI LLM client."""
        try:
            # Azure OpenAI configuration
            self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
            self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
            
            if not all([self.api_key, self.endpoint, self.deployment]):
                raise ValueError("Missing required Azure OpenAI configuration")
            
            # Build API URL
            self.api_url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
            
            # Headers for Azure OpenAI
            self.headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            # Omani therapeutic system prompt
            self.system_prompt = self._build_omani_therapeutic_prompt()
            
            # Conversation history
            self.conversation_history = []
            
            logger.info(f"Azure OpenAI LLM initialized with {self.deployment}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI LLM: {e}")
            raise
    
    def _build_omani_therapeutic_prompt(self) -> str:
        """
        Build the system prompt for Omani therapeutic conversations.
        
        Returns:
            System prompt string
        """
        return """أنت مساعد علاجي متخصص في الثقافة العمانية والقيم الإسلامية. مهمتك هي تقديم الدعم النفسي والعلاجي باللغة العربية مع مراعاة:

## الهوية والدور:
- أنت مستشار نفسي مختص في الثقافة العمانية
- تتكلم باللهجة العمانية والعربية الفصحى المبسطة
- تراعي القيم الإسلامية والتقاليد العمانية
- تقدم الدعم النفسي المهني مع الحساسية الثقافية

## المبادئ الأساسية:
1. **الاحترام الثقافي**: احترم القيم والتقاليد العمانية
2. **القيم الإسلامية**: ادمج المفاهيم الإسلامية بطريقة علاجية
3. **الخصوصية**: حافظ على السرية المطلقة
4. **عدم الحكم**: لا تحكم على الشخص أو تنتقده
5. **التمكين**: ساعد الشخص على إيجاد الحلول بنفسه

## الأسلوب العلاجي:
- استخدم العلاج المعرفي السلوكي مع التكيف الثقافي
- اربط الحلول بالقيم الدينية والثقافية
- استخدم التعزيز الإيجابي والتشجيع
- قدم استراتيجيات عملية قابلة للتطبيق

## التعامل مع الحساسيات:
- **الشرف والسمعة**: تعامل بحذر شديد
- **العلاقات الأسرية**: أكد على أهمية الأسرة
- **الدين**: استخدم المفاهيم الإسلامية بإيجابية
- **الجنس**: تجنب المواضيع الحساسة إلا عند الضرورة

## اللغة والتواصل:
- استخدم اللهجة العمانية المناسبة
- ابدأ بالسلام والتحية الإسلامية
- استخدم كلمات مطمئنة ومشجعة
- تجنب المصطلحات الطبية المعقدة

## الكلمات المفتاحية العمانية:
- التحية: "السلام عليكم"، "أهلاً وسهلاً"، "حياك الله"
- التشجيع: "الله يعطيك العافية"، "إن شاء الله بخير"
- التطمين: "الحمد لله"، "الله كريم"، "ربنا معك"

تذكر: أنت هنا لتقديم الدعم والمساعدة، وليس لتقديم النصائح الطبية أو الدينية المتخصصة."""
    
    async def generate_therapeutic_response(
        self, 
        user_message: str, 
        context: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate therapeutic response using Azure OpenAI.
        
        Args:
            user_message: User's message in Arabic
            context: Additional context (emotions, cultural analysis, etc.)
            session_id: Session identifier
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            # Prepare context-aware system prompt
            enhanced_prompt = self._enhance_prompt_with_context(context)
            
            # Build conversation messages
            messages = [
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Add conversation history (keep last 10 messages)
            if hasattr(self, 'conversation_history') and self.conversation_history:
                recent_history = self.conversation_history[-10:]
                messages = [messages[0]] + recent_history + [messages[1]]
            
            # Prepare request payload
            payload = {
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
                "stop": None
            }
            
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Extract response
                if "choices" in result and len(result["choices"]) > 0:
                    therapeutic_response = result["choices"][0]["message"]["content"]
                    
                    # Update conversation history
                    self.conversation_history.extend([
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": therapeutic_response}
                    ])
                    
                    return {
                        "response": therapeutic_response,
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "model": self.deployment,
                        "context_used": context is not None,
                        "status": "success"
                    }
                else:
                    raise ValueError("No response generated")
                    
        except Exception as e:
            logger.error(f"Failed to generate therapeutic response: {e}")
            return {
                "response": "عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    def _enhance_prompt_with_context(self, context: Optional[Dict]) -> str:
        """
        Enhance system prompt with contextual information.
        
        Args:
            context: Context dictionary with emotions, cultural analysis, etc.
            
        Returns:
            Enhanced system prompt
        """
        enhanced_prompt = self.system_prompt
        
        if context:
            # Add emotional context
            if "emotions" in context:
                emotions = context["emotions"]
                enhanced_prompt += f"\n\n## السياق العاطفي:\nالشخص يشعر بـ: {', '.join(emotions)}"
            
            # Add cultural context
            if "cultural_analysis" in context:
                cultural = context["cultural_analysis"]
                if cultural.get("sensitivity_level"):
                    enhanced_prompt += f"\n\n## الحساسية الثقافية:\nمستوى الحساسية: {cultural['sensitivity_level']}"
                
                if cultural.get("categories"):
                    enhanced_prompt += f"\nالفئات الثقافية: {', '.join(cultural['categories'])}"
                
                if cultural.get("guidance"):
                    guidance = cultural["guidance"]
                    if "approach" in guidance:
                        enhanced_prompt += f"\n\n## التوجيه:\n{guidance['approach']}"
            
            # Add crisis context
            if "crisis_level" in context:
                crisis_level = context["crisis_level"]
                if crisis_level and crisis_level != "low":
                    enhanced_prompt += f"\n\n## تنبيه:\nمستوى الأزمة: {crisis_level} - تعامل بحذر إضافي"
        
        return enhanced_prompt
    
    def generate_therapeutic_response_sync(
        self, 
        user_message: str, 
        context: Optional[Dict] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for generate_therapeutic_response.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.generate_therapeutic_response(user_message, context, session_id)
            )
        finally:
            loop.close()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation.
        
        Returns:
            Dictionary with conversation statistics
        """
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([msg for msg in self.conversation_history if msg["role"] == "user"]),
            "assistant_messages": len([msg for msg in self.conversation_history if msg["role"] == "assistant"]),
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None
        }

# Factory function for easy instantiation
def create_azure_omani_llm(**kwargs) -> AzureOmaniTherapistLLM:
    """
    Factory function to create AzureOmaniTherapistLLM instance.
    
    Returns:
        Configured AzureOmaniTherapistLLM instance
    """
    return AzureOmaniTherapistLLM(**kwargs)
