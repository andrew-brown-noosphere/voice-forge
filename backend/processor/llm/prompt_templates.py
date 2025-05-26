"""
Prompt template manager for LLM API calls.
"""
import json
import os
import logging
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class PromptTemplateManager:
    """Manages prompt templates for different LLM providers."""
    
    def __init__(self, template_file=None):
        self.templates = self._load_templates(template_file)
    
    def _load_templates(self, template_file=None):
        """Load prompt templates from file or use defaults."""
        # Default templates
        templates = {
            "rag_response": {
                "openai": [
                    {"role": "system", "content": "You are a helpful AI assistant. Answer the question based on the provided context. If the answer is not in the context, say you don't know."},
                    {"role": "user", "content": "Context: {{context}}\n\nQuestion: {{query}}"}
                ],
                "anthropic": "You are a helpful AI assistant. Answer the question based on the provided context. If the answer is not in the context, say you don't know.\n\nContext: {{context}}\n\nQuestion: {{query}}"
            },
            "query_reformulation": {
                "openai": [
                    {"role": "system", "content": "Generate 3 alternative search queries that might help retrieve relevant information for the original query. Return only the queries, one per line."},
                    {"role": "user", "content": "Original query: {{query}}"}
                ],
                "anthropic": "Generate 3 alternative search queries that might help retrieve relevant information for the original query. Return only the queries, one per line.\n\nOriginal query: {{query}}"
            },
            "content_generation": {
                "openai": [
                    {"role": "system", "content": "Generate {{platform}} content in a {{tone}} tone based on the context. The content should be concise and engaging. Target audience is {{audience}}."},
                    {"role": "user", "content": "Topic: {{topic}}\nContext: {{context}}"}
                ],
                "anthropic": "Generate {{platform}} content in a {{tone}} tone based on the context. The content should be concise and engaging. Target audience is {{audience}}.\n\nTopic: {{topic}}\nContext: {{context}}"
            },
            "key_points_extraction": {
                "openai": [
                    {"role": "system", "content": "Extract the 3-5 most important key points from the following text. Return each key point on a new line."},
                    {"role": "user", "content": "{{text}}"}
                ],
                "anthropic": "Extract the 3-5 most important key points from the following text. Return each key point on a new line.\n\nText: {{text}}"
            },
            "marketing_analysis": {
                "openai": [
                    {"role": "system", "content": "Analyze the following marketing content. Identify key messaging, target audience, tone, and suggested improvements."},
                    {"role": "user", "content": "{{content}}"}
                ],
                "anthropic": "Analyze the following marketing content. Identify key messaging, target audience, tone, and suggested improvements.\n\nContent: {{content}}"
            }
        }
        
        # Try to load templates from file
        if template_file:
            template_path = template_file
        else:
            template_path = os.path.join(os.path.dirname(__file__), "templates.json")
            
        if os.path.exists(template_path):
            try:
                with open(template_path, "r") as f:
                    loaded_templates = json.load(f)
                
                # Update templates
                for template_type, providers in loaded_templates.items():
                    if template_type not in templates:
                        templates[template_type] = {}
                    
                    templates[template_type].update(providers)
                    
                logger.info(f"Loaded {len(loaded_templates)} template types from {template_path}")
            except Exception as e:
                logger.error(f"Error loading templates from {template_path}: {str(e)}")
        else:
            logger.info(f"No template file found at {template_path}, using default templates")
        
        return templates
    
    def get_prompt(self, prompt_type, provider, params):
        """
        Get a prompt template for a specific provider.
        
        Args:
            prompt_type: Type of prompt
            provider: LLM provider
            params: Parameters to fill in the template
            
        Returns:
            Prepared prompt
        """
        # Get template
        if prompt_type not in self.templates:
            logger.warning(f"Unknown prompt type: {prompt_type}, falling back to generic template")
            # Fallback to a generic template
            if provider == "openai":
                template = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "{{query}}"}
                ]
            else:
                template = "Human: {{query}}\n\nAssistant: "
        else:
            provider_templates = self.templates[prompt_type]
            
            if provider not in provider_templates:
                # Try to fall back to a supported provider
                available_providers = list(provider_templates.keys())
                if available_providers:
                    provider = available_providers[0]
                    logger.warning(f"Provider {provider} not available for prompt type {prompt_type}, falling back to {provider}")
                else:
                    logger.error(f"No template available for {prompt_type}")
                    raise ValueError(f"No template available for {prompt_type}")
            
            template = provider_templates[provider]
        
        # Fill template
        if isinstance(template, str):
            # String template
            return self._fill_string_template(template, params)
        elif isinstance(template, list):
            # Message template
            return self._fill_message_template(template, params)
        else:
            logger.error(f"Unsupported template format: {type(template)}")
            raise ValueError(f"Unsupported template format: {type(template)}")
    
    def _fill_string_template(self, template, params):
        """Fill a string template with parameters."""
        result = template
        
        for key, value in params.items():
            placeholder = f"{{{{{key}}}}}"
            
            # Convert context chunks to string if needed
            if key == "context" and isinstance(value, list):
                value = "\n\n".join([chunk["text"] for chunk in value])
            
            # Replace placeholder
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def _fill_message_template(self, template, params):
        """Fill a message template with parameters."""
        result = []
        
        for message in template:
            new_message = message.copy()
            
            # Fill content
            if "content" in new_message:
                new_message["content"] = self._fill_string_template(new_message["content"], params)
            
            result.append(new_message)
        
        return result
    
    def add_template(self, prompt_type, provider, template):
        """
        Add a new template or update an existing one.
        
        Args:
            prompt_type: Type of prompt
            provider: LLM provider
            template: Template string or message list
            
        Returns:
            None
        """
        if prompt_type not in self.templates:
            self.templates[prompt_type] = {}
        
        self.templates[prompt_type][provider] = template
        logger.info(f"Added template for {prompt_type}/{provider}")
    
    def save_templates(self, template_file=None):
        """
        Save templates to a file.
        
        Args:
            template_file: Path to save templates to (defaults to templates.json in module directory)
            
        Returns:
            Success status (bool)
        """
        if not template_file:
            template_file = os.path.join(os.path.dirname(__file__), "templates.json")
        
        try:
            with open(template_file, "w") as f:
                json.dump(self.templates, f, indent=2)
            logger.info(f"Saved templates to {template_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving templates to {template_file}: {str(e)}")
            return False
