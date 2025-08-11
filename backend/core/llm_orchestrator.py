"""
LLM Orchestrator with hybrid routing (local + cloud fallbacks)
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers in priority order"""
    LOCAL = "local"  # Ollama/vLLM
    GROQ = "groq"
    GEMINI = "gemini"
    CURSOR = "cursor"
    OPENAI = "openai"


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: LLMProvider
    model: str
    latency_ms: float
    token_count: Optional[int] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


class LLMOrchestrator:
    """Orchestrates LLM calls with hybrid routing and fallbacks"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.providers = self._initialize_providers()
        self.sensitive_patterns = ["password", "ssn", "credit", "medical"]
        
    def _initialize_providers(self) -> Dict[LLMProvider, Any]:
        """Initialize available providers"""
        providers = {}
        
        # Local model (Ollama)
        if self.config.get("enable_local", True):
            try:
                import ollama
                providers[LLMProvider.LOCAL] = ollama.Client()
            except ImportError:
                logger.warning("Ollama not available for local model")
        
        # Groq
        if groq_key := os.getenv("GROQ_API_KEY"):
            try:
                from groq import Groq
                providers[LLMProvider.GROQ] = Groq(api_key=groq_key)
            except ImportError:
                logger.warning("Groq SDK not available")
        
        # Gemini
        if gemini_key := os.getenv("GOOGLE_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                providers[LLMProvider.GEMINI] = genai.GenerativeModel('gemini-1.5-flash')
            except ImportError:
                logger.warning("Google Generative AI not available")
        
        # OpenAI
        if openai_key := os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                providers[LLMProvider.OPENAI] = OpenAI(api_key=openai_key)
            except ImportError:
                logger.warning("OpenAI SDK not available")
        
        return providers
    
    def _is_sensitive(self, text: str) -> bool:
        """Check if text contains sensitive data"""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.sensitive_patterns)
    
    def _is_high_volume(self, text: str) -> bool:
        """Check if request is high-volume (bulk processing)"""
        # Simple heuristic: long text or multiple items
        return len(text) > 10000 or text.count("\n") > 50
    
    def _should_use_local(self, prompt: str, task_type: str) -> bool:
        """Determine if local model should be preferred"""
        # Use local for sensitive data or high-volume tasks
        if self._is_sensitive(prompt):
            logger.info("Using local model for sensitive data")
            return True
        if self._is_high_volume(prompt):
            logger.info("Using local model for high-volume task")
            return True
        # Use local for deterministic tasks
        if task_type in ["schema_fix", "template_fill", "validation"]:
            return True
        return False
    
    def _call_local(self, prompt: str, system: str) -> Optional[LLMResponse]:
        """Call local Ollama model"""
        if LLMProvider.LOCAL not in self.providers:
            return None
        
        try:
            start = time.time()
            client = self.providers[LLMProvider.LOCAL]
            response = client.generate(
                model="llama3.2",
                prompt=f"{system}\n\n{prompt}"
            )
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=response['response'],
                provider=LLMProvider.LOCAL,
                model="llama3.2",
                latency_ms=latency
            )
        except Exception as e:
            logger.error(f"Local model error: {e}")
            return None
    
    def _call_groq(self, prompt: str, system: str) -> Optional[LLMResponse]:
        """Call Groq API"""
        if LLMProvider.GROQ not in self.providers:
            return None
        
        try:
            start = time.time()
            client = self.providers[LLMProvider.GROQ]
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.GROQ,
                model="llama-3.3-70b",
                latency_ms=latency,
                token_count=response.usage.total_tokens if response.usage else None
            )
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None
    
    def _call_gemini(self, prompt: str, system: str) -> Optional[LLMResponse]:
        """Call Google Gemini API"""
        if LLMProvider.GEMINI not in self.providers:
            return None
        
        try:
            start = time.time()
            model = self.providers[LLMProvider.GEMINI]
            response = model.generate_content(f"{system}\n\n{prompt}")
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=response.text,
                provider=LLMProvider.GEMINI,
                model="gemini-1.5-flash",
                latency_ms=latency
            )
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
    
    def _call_openai(self, prompt: str, system: str) -> Optional[LLMResponse]:
        """Call OpenAI API"""
        if LLMProvider.OPENAI not in self.providers:
            return None
        
        try:
            start = time.time()
            client = self.providers[LLMProvider.OPENAI]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                latency_ms=latency,
                token_count=response.usage.total_tokens if response.usage else None
            )
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None
    
    def call(self, 
             prompt: str, 
             system: str = "You are a helpful assistant.",
             task_type: str = "general",
             force_provider: Optional[LLMProvider] = None) -> LLMResponse:
        """
        Call LLM with hybrid routing and fallbacks
        
        Args:
            prompt: User prompt
            system: System prompt
            task_type: Type of task (affects routing)
            force_provider: Override routing to use specific provider
        """
        # Forced provider
        if force_provider:
            handlers = {
                LLMProvider.LOCAL: self._call_local,
                LLMProvider.GROQ: self._call_groq,
                LLMProvider.GEMINI: self._call_gemini,
                LLMProvider.OPENAI: self._call_openai
            }
            if handler := handlers.get(force_provider):
                if response := handler(prompt, system):
                    return response
        
        # Hybrid routing
        if self._should_use_local(prompt, task_type):
            if response := self._call_local(prompt, system):
                return response
        
        # Cloud fallback chain
        for handler in [self._call_groq, self._call_gemini, self._call_openai]:
            if response := handler(prompt, system):
                return response
        
        # All failed
        return LLMResponse(
            content="",
            provider=LLMProvider.LOCAL,
            model="none",
            latency_ms=0,
            error="All LLM providers failed"
        )
    
    def validate_json_response(self, response: str, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate JSON response against schema"""
        try:
            data = json.loads(response)
            # Basic validation - would use jsonschema in production
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
    
    def repair_json(self, invalid_json: str, error: str, schema: Dict[str, Any]) -> Optional[str]:
        """Attempt to repair invalid JSON using LLM"""
        repair_prompt = f"""
Fix this JSON to match the schema. Return only valid JSON, no explanations.

Error: {error}

Invalid JSON:
{invalid_json}

Required schema:
{json.dumps(schema, indent=2)}
"""
        response = self.call(
            prompt=repair_prompt,
            system="You are a JSON repair expert. Return only valid JSON.",
            task_type="schema_fix"
        )
        
        if response.content:
            valid, _ = self.validate_json_response(response.content, schema)
            if valid:
                return response.content
        return None
