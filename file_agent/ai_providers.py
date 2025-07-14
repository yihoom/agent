"""
AI providers module for integrating with different AI APIs.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """AI提供商的抽象基类。"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成AI响应。"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表。"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API提供商。"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is required for OpenAI provider")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用OpenAI API生成响应。"""
        try:
            max_tokens = kwargs.get('max_tokens', 1000)
            temperature = kwargs.get('temperature', 0.7)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    def get_available_models(self) -> List[str]:
        """获取OpenAI可用的模型列表。"""
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]


class AnthropicProvider(AIProvider):
    """Anthropic Claude API提供商。"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, model)
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package is required for Anthropic provider")
    
    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用Anthropic API生成响应。"""
        try:
            max_tokens = kwargs.get('max_tokens', 1000)
            temperature = kwargs.get('temperature', 0.7)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "success": True,
                "response": response.content[0].text,
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    def get_available_models(self) -> List[str]:
        """获取Anthropic可用的模型列表。"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]


class GoogleProvider(AIProvider):
    """Google Gemini API提供商。"""

    def __init__(self, api_key: str, model: str = "gemini-pro"):
        super().__init__(api_key, model)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("google-generativeai package is required for Google provider")

    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用Google Gemini API生成响应。"""
        try:
            response = self.client.generate_content(prompt)

            return {
                "success": True,
                "response": response.text,
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }

    def get_available_models(self) -> List[str]:
        """获取Google可用的模型列表。"""
        return [
            "gemini-pro",
            "gemini-pro-vision"
        ]


class DeepSeekProvider(AIProvider):
    """DeepSeek API提供商。"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(api_key, model)
        try:
            import openai
            # DeepSeek使用OpenAI兼容的API
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        except ImportError:
            raise ImportError("openai package is required for DeepSeek provider")

    async def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用DeepSeek API生成响应。"""
        try:
            max_tokens = kwargs.get('max_tokens', 1000)
            temperature = kwargs.get('temperature', 0.7)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }

    def get_available_models(self) -> List[str]:
        """获取DeepSeek可用的模型列表。"""
        return [
            "deepseek-chat",
            "deepseek-coder"
        ]


class AIProviderFactory:
    """AI提供商工厂类。"""
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str, model: Optional[str] = None) -> AIProvider:
        """
        创建AI提供商实例。

        Args:
            provider_name: 提供商名称 (openai, anthropic, google, deepseek)
            api_key: API密钥
            model: 模型名称（可选）

        Returns:
            AI提供商实例
        """
        provider_name = provider_name.lower()

        if provider_name == "openai":
            default_model = "gpt-3.5-turbo"
            return OpenAIProvider(api_key, model or default_model)
        elif provider_name == "anthropic":
            default_model = "claude-3-sonnet-20240229"
            return AnthropicProvider(api_key, model or default_model)
        elif provider_name == "google":
            default_model = "gemini-pro"
            return GoogleProvider(api_key, model or default_model)
        elif provider_name == "deepseek":
            default_model = "deepseek-chat"
            return DeepSeekProvider(api_key, model or default_model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")

    @staticmethod
    def get_supported_providers() -> List[str]:
        """获取支持的AI提供商列表。"""
        return ["openai", "anthropic", "google", "deepseek"]
