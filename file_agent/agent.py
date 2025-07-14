"""
Main agent module that integrates file management and AI capabilities.
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional
import logging

from .config import Config
from .file_manager import FileManager
from .ai_providers import AIProviderFactory, AIProvider

logger = logging.getLogger(__name__)


class FileAgent:
    """文件管理智能代理主类。"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化文件代理。
        
        Args:
            config_file: 配置文件路径（可选）
        """
        self.config = Config(config_file)
        
        # 验证配置
        validation = self.config.validate_config()
        if not validation["valid"]:
            logger.warning(f"Configuration issues: {validation['issues']}")
        
        # 初始化文件管理器
        fm_config = self.config.get_file_manager_config()
        self.file_manager = FileManager(
            workspace=fm_config["workspace"],
            backup_enabled=fm_config["backup_enabled"]
        )
        
        # 初始化AI提供商
        self.ai_provider = None
        self._setup_ai_provider()
        
        # 定义可用的文件操作
        self.file_operations = {
            "create_file": self.file_manager.create_file,
            "read_file": self.file_manager.read_file,
            "write_file": self.file_manager.write_file,
            "delete_file": self.file_manager.delete_file,
            "move_file": self.file_manager.move_file,
            "copy_file": self.file_manager.copy_file,
            "create_directory": self.file_manager.create_directory,
            "list_files": self.file_manager.list_files,
        }
    
    def _setup_ai_provider(self) -> None:
        """设置AI提供商。"""
        try:
            ai_config = self.config.get_ai_config()
            provider_name = ai_config["provider"]
            api_key = ai_config["api_keys"].get(provider_name)

            if not api_key:
                logger.error(f"No API key found for provider: {provider_name}")
                return

            # 根据提供商选择合适的默认模型
            model = ai_config["model"]

            # 如果当前模型不适合选定的提供商，使用提供商的默认模型
            provider_default_models = {
                "openai": "gpt-3.5-turbo",
                "anthropic": "claude-3-sonnet-20240229",
                "google": "gemini-pro",
                "deepseek": "deepseek-chat"
            }

            # 检查当前模型是否适合当前提供商
            if provider_name in provider_default_models:
                # 创建临时提供商实例来获取可用模型列表
                temp_provider = AIProviderFactory.create_provider(
                    provider_name=provider_name,
                    api_key=api_key,
                    model=provider_default_models[provider_name]
                )
                available_models = temp_provider.get_available_models()

                # 如果当前模型不在可用模型列表中，使用默认模型
                if model not in available_models:
                    model = provider_default_models[provider_name]
                    logger.info(f"Switched to default model {model} for provider {provider_name}")

            self.ai_provider = AIProviderFactory.create_provider(
                provider_name=provider_name,
                api_key=api_key,
                model=model
            )

            logger.info(f"Initialized AI provider: {provider_name} with model: {model}")
        except Exception as e:
            logger.error(f"Failed to setup AI provider: {e}")
    
    def _parse_command(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入的命令。

        Args:
            user_input: 用户输入的自然语言命令

        Returns:
            解析后的命令字典
        """
        # 简单的命令解析逻辑（可以扩展为更复杂的NLP解析）
        original_input = user_input.strip()
        user_input = user_input.lower().strip()

        # 文件创建命令
        if "创建" in user_input and "文件" in user_input:
            # 提取引号中的文件名
            file_match = re.search(r'["\']([^"\']+\.[\w]+)["\']', original_input)
            if file_match:
                filename = file_match.group(1)
                # 提取内容
                content = ""
                if "内容" in user_input:
                    content_match = re.search(r'内容[是为]?["\']([^"\']+)["\']', original_input)
                    content = content_match.group(1) if content_match else ""

                return {
                    "operation": "create_file",
                    "params": {"path": filename, "content": content}
                }

        elif "创建" in user_input and ("目录" in user_input or "文件夹" in user_input):
            # 提取引号中的目录名
            dir_match = re.search(r'["\']([^"\']+)["\']', original_input)
            if dir_match:
                dirname = dir_match.group(1)
                return {
                    "operation": "create_directory",
                    "params": {"path": dirname}
                }

        # 文件读取命令
        elif "读取" in user_input or "查看" in user_input:
            file_match = re.search(r'["\']([^"\']+\.[\w]+)["\']', original_input)
            if file_match:
                filename = file_match.group(1)
                return {
                    "operation": "read_file",
                    "params": {"path": filename}
                }

        # 文件列表命令
        elif "列出" in user_input or "显示" in user_input:
            return {
                "operation": "list_files",
                "params": {"path": ".", "recursive": "递归" in user_input}
            }

        # 文件删除命令
        elif "删除" in user_input:
            file_match = re.search(r'["\']([^"\']+\.[\w]+)["\']', original_input)
            if file_match:
                filename = file_match.group(1)
                return {
                    "operation": "delete_file",
                    "params": {"path": filename}
                }

        # 文件复制命令
        elif "复制" in user_input or "拷贝" in user_input:
            # 匹配两个文件名
            file_matches = re.findall(r'["\']([^"\']+\.[\w]+)["\']', original_input)
            if len(file_matches) >= 2:
                return {
                    "operation": "copy_file",
                    "params": {"src_path": file_matches[0], "dst_path": file_matches[1]}
                }

        # 默认返回AI处理命令
        return {
            "operation": "ai_process",
            "params": {"prompt": original_input}
        }
    
    async def execute(self, user_input: str) -> Dict[str, Any]:
        """
        执行用户命令。
        
        Args:
            user_input: 用户输入的自然语言命令
            
        Returns:
            执行结果字典
        """
        try:
            # 解析命令
            command = self._parse_command(user_input)
            operation = command["operation"]
            params = command["params"]
            
            logger.info(f"Executing operation: {operation} with params: {params}")
            
            # 执行文件操作
            if operation in self.file_operations:
                result = self.file_operations[operation](**params)
                
                # 如果操作成功，可以选择性地使用AI生成更友好的响应
                if result["success"] and self.ai_provider:
                    ai_prompt = f"用户执行了文件操作：{operation}，结果：{result['message']}。请生成一个简洁友好的确认消息。"
                    ai_response = await self.ai_provider.generate_response(ai_prompt, max_tokens=100)
                    
                    if ai_response["success"]:
                        result["ai_message"] = ai_response["response"]
                
                return result
            
            # AI处理
            elif operation == "ai_process":
                if not self.ai_provider:
                    return {
                        "success": False,
                        "message": "AI provider not configured",
                        "operation": operation
                    }
                
                # 构建包含文件操作能力的提示
                enhanced_prompt = f"""
你是一个文件管理助手。用户说："{params['prompt']}"

你可以执行以下文件操作：
- 创建文件：create_file(path, content)
- 读取文件：read_file(path)
- 写入文件：write_file(path, content, append=False)
- 删除文件：delete_file(path)
- 移动文件：move_file(src_path, dst_path)
- 复制文件：copy_file(src_path, dst_path)
- 创建目录：create_directory(path)
- 列出文件：list_files(path, pattern="*", recursive=False)

请分析用户的需求，如果需要执行文件操作，请说明具体的操作步骤。如果不需要文件操作，请直接回答用户的问题。
"""
                
                ai_config = self.config.get_ai_config()
                ai_response = await self.ai_provider.generate_response(
                    enhanced_prompt,
                    max_tokens=ai_config["max_tokens"],
                    temperature=ai_config["temperature"]
                )
                
                return {
                    "success": ai_response["success"],
                    "message": ai_response.get("response", ai_response.get("error", "Unknown error")),
                    "operation": operation,
                    "ai_model": ai_response.get("model"),
                    "usage": ai_response.get("usage")
                }
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown operation: {operation}",
                    "operation": operation
                }
        
        except Exception as e:
            logger.error(f"Error executing command '{user_input}': {e}")
            return {
                "success": False,
                "message": f"Error executing command: {str(e)}",
                "operation": "unknown"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """获取代理状态信息。"""
        ai_config = self.config.get_ai_config()
        fm_config = self.config.get_file_manager_config()
        
        return {
            "ai_provider": ai_config["provider"] if self.ai_provider else "Not configured",
            "ai_model": ai_config["model"] if self.ai_provider else "N/A",
            "workspace": fm_config["workspace"],
            "backup_enabled": fm_config["backup_enabled"],
            "available_operations": list(self.file_operations.keys())
        }
