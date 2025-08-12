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
from pathlib import Path
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

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
        self.model_config = self._load_model_config()
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
                providers[LLMProvider.GEMINI] = genai  # keep module; instantiate model per call
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

    def _load_model_config(self) -> Dict[str, Any]:
        """Load model names and routing config from config/llm.yml and/or env vars."""
        defaults = {
            "models": {
                "local": os.getenv("LOCAL_MODEL", "llama3.2"),
                "groq": os.getenv("GROQ_MODEL", "compound-beta"),
                "gemini": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                "openai": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            },
            "routing": {
                "enable_local": False,
                "order": ["groq", "gemini", "openai"],
                "max_retries": 3,
                "timeout_seconds": 30
            }
        }
        cfg_path = Path("config/llm.yml")
        if cfg_path.exists() and yaml is not None:
            try:
                data = yaml.safe_load(cfg_path.read_text()) or {}
                if "models" in data:
                    defaults["models"].update(data["models"])
                if "routing" in data:
                    defaults["routing"].update(data["routing"])
                logger.info(f"Loaded LLM config with order: {defaults['routing']['order']}")
            except Exception as e:
                logger.warning(f"Failed to load config/llm.yml: {e}; using env/defaults")
        return defaults
    
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
        # Respect routing config: disable local if not enabled
        try:
            routing = self.model_config.get("routing", {})
            if not routing.get("enable_local", False):
                return False
        except Exception:
            return False
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
            model_name = self.model_config["models"].get("local", "llama3.2")
            response = client.generate(
                model=model_name,
                prompt=f"{system}\n\n{prompt}"
            )
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=response['response'],
                provider=LLMProvider.LOCAL,
                model=model_name,
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
                model=self.model_config["models"].get("groq", "compound-beta"),
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
                model=self.model_config["models"].get("groq", "compound-beta"),
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
            genai = self.providers[LLMProvider.GEMINI]
            model_name = self.model_config["models"].get("gemini", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"{system}\n\n{prompt}")
            latency = (time.time() - start) * 1000
            
            return LLMResponse(
                content=response.text,
                provider=LLMProvider.GEMINI,
                model=model_name,
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
                model=self.model_config["models"].get("openai", "gpt-4o-mini"),
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
                model=self.model_config["models"].get("openai", "gpt-4o-mini"),
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
        
        # Cloud fallback chain - use configured order
        provider_handlers = {
            "groq": self._call_groq,
            "gemini": self._call_gemini,
            "openai": self._call_openai,
            "local": self._call_local
        }
        
        fallback_order = self.model_config["routing"]["order"]
        logger.info(f"Using LLM fallback order: {fallback_order}")
        
        for provider_name in fallback_order:
            if handler := provider_handlers.get(provider_name):
                logger.info(f"Trying LLM provider: {provider_name}")
                if response := handler(prompt, system):
                    logger.info(f"✅ {provider_name} succeeded")
                    return response
                else:
                    logger.warning(f"❌ {provider_name} failed, trying next provider")
        
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
