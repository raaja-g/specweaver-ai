"""
Prompt Template Loader and Manager
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptLoader:
    """Loads and manages prompt templates from external files"""
    
    def __init__(self, prompts_dir: str = "config/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Load all prompt templates from YAML files"""
        prompts = {}
        
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory {self.prompts_dir} not found")
            return prompts
        
        for prompt_file in self.prompts_dir.glob("*.yml"):
            try:
                with open(prompt_file, 'r') as f:
                    prompt_config = yaml.safe_load(f)
                    prompts.update(prompt_config)
                    logger.info(f"Loaded prompts from: {prompt_file.name}")
            except Exception as e:
                logger.error(f"Failed to load prompts from {prompt_file}: {e}")
        
        return prompts
    
    def get_prompt(self, prompt_key: str, **kwargs) -> Optional[str]:
        """
        Get a prompt template and format it with provided variables
        
        Args:
            prompt_key: Key to identify the prompt (e.g., 'bdd_generation.main_prompt')
            **kwargs: Variables to format into the prompt template
            
        Returns:
            Formatted prompt string or None if not found
        """
        try:
            # Navigate nested keys (e.g., 'bdd_generation.main_prompt')
            keys = prompt_key.split('.')
            prompt_data = self.prompts
            
            for key in keys:
                prompt_data = prompt_data[key]
            
            # Format the prompt with provided variables
            if isinstance(prompt_data, str):
                return prompt_data.format(**kwargs)
            else:
                logger.error(f"Prompt {prompt_key} is not a string")
                return None
                
        except KeyError:
            logger.error(f"Prompt {prompt_key} not found")
            return None
        except Exception as e:
            logger.error(f"Error formatting prompt {prompt_key}: {e}")
            return None
    
    def get_system_prompt(self, prompt_key: str) -> Optional[str]:
        """Get system prompt for a specific task"""
        return self.get_prompt(f"{prompt_key}.system_prompt")
    
    def list_available_prompts(self) -> Dict[str, list]:
        """Return available prompts organized by category"""
        available = {}
        for category, prompts in self.prompts.items():
            if isinstance(prompts, dict):
                available[category] = list(prompts.keys())
        return available
    
    def reload_prompts(self):
        """Reload prompts from files (useful for development)"""
        self.prompts = self._load_prompts()
        logger.info("Prompts reloaded from files")
