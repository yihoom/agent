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
                # 提取内容 - 改进的内容提取逻辑
                content = ""

                # 方法1: 查找"内容是/为"模式
                if "内容" in user_input:
                    content_match = re.search(r'内容[是为]?["\']([^"\']+)["\']', original_input)
                    content = content_match.group(1) if content_match else ""

                # 方法2: 查找文件名后的内容描述
                if not content:
                    # 查找类似"内容是print('Hello')"的模式
                    content_match = re.search(r'内容[是为]?\s*(.+)', original_input)
                    if content_match:
                        content_part = content_match.group(1).strip()
                        # 移除引号
                        if content_part.startswith('"') and content_part.endswith('"'):
                            content = content_part[1:-1]
                        elif content_part.startswith("'") and content_part.endswith("'"):
                            content = content_part[1:-1]
                        else:
                            content = content_part

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

如果用户需要执行文件操作，请在回复的最后添加一行：
EXECUTE: operation_name(param1, param2, ...)

例如：
- 如果要创建文件：EXECUTE: create_file("test.py", "print('Hello World')")
- 如果要列出文件：EXECUTE: list_files(".", "*.py")

请分析用户的需求并提供帮助。
"""

                ai_config = self.config.get_ai_config()
                ai_response = await self.ai_provider.generate_response(
                    enhanced_prompt,
                    max_tokens=ai_config["max_tokens"],
                    temperature=ai_config["temperature"]
                )

                if not ai_response["success"]:
                    return {
                        "success": False,
                        "message": ai_response.get("error", "Unknown error"),
                        "operation": operation,
                        "ai_model": ai_response.get("model"),
                        "usage": ai_response.get("usage")
                    }

                # 解析AI响应中的执行指令
                response_text = ai_response.get("response", "")
                executed_operations = []

                # 查找EXECUTE指令
                import re
                execute_pattern = r'EXECUTE:\s*(\w+)\((.*?)\)(?:\s|$)'
                matches = re.findall(execute_pattern, response_text, re.DOTALL)

                for operation_name, params_str in matches:
                    if operation_name in self.file_operations:
                        try:
                            # 更好的参数解析
                            params_list = []
                            if params_str.strip():
                                # 使用eval来安全解析参数（仅限于简单的字符串和数字）
                                try:
                                    # 构建一个安全的参数列表
                                    params_str = params_str.strip()
                                    if params_str.startswith('"') and '", "' in params_str:
                                        # 处理多个字符串参数
                                        parts = params_str.split('", "')
                                        params_list = [part.strip('"') for part in parts]
                                    elif params_str.startswith('"') and params_str.endswith('"'):
                                        # 单个字符串参数
                                        params_list = [params_str.strip('"')]
                                    else:
                                        # 尝试分割逗号分隔的参数
                                        import ast
                                        params_list = ast.literal_eval(f"[{params_str}]")
                                except:
                                    # 如果解析失败，尝试简单的字符串分割
                                    params_list = [p.strip().strip('"\'') for p in params_str.split(',')]

                            # 执行操作
                            if operation_name == "create_file" and len(params_list) >= 1:
                                path = params_list[0]
                                content = params_list[1] if len(params_list) > 1 else ""
                                op_result = self.file_operations[operation_name](path, content)
                                executed_operations.append(f"✓ {operation_name}: {op_result['message']}")

                            elif operation_name == "list_files":
                                path = params_list[0] if params_list else "."
                                pattern = params_list[1] if len(params_list) > 1 else "*"
                                op_result = self.file_operations[operation_name](path, pattern)
                                executed_operations.append(f"✓ {operation_name}: Found {op_result.get('total_files', 0)} files")

                            elif operation_name in ["read_file", "delete_file"] and len(params_list) >= 1:
                                path = params_list[0]
                                op_result = self.file_operations[operation_name](path)
                                executed_operations.append(f"✓ {operation_name}: {op_result['message']}")

                            elif operation_name in ["move_file", "copy_file"] and len(params_list) >= 2:
                                src_path = params_list[0]
                                dst_path = params_list[1]
                                op_result = self.file_operations[operation_name](src_path, dst_path)
                                executed_operations.append(f"✓ {operation_name}: {op_result['message']}")

                            elif operation_name == "create_directory" and len(params_list) >= 1:
                                path = params_list[0]
                                op_result = self.file_operations[operation_name](path)
                                executed_operations.append(f"✓ {operation_name}: {op_result['message']}")

                        except Exception as e:
                            executed_operations.append(f"✗ {operation_name}: Error - {str(e)}")

                # 构建最终响应
                final_message = response_text
                if executed_operations:
                    # 移除EXECUTE指令行
                    final_message = re.sub(r'EXECUTE:.*?\n?', '', final_message).strip()
                    final_message += "\n\n执行的操作：\n" + "\n".join(executed_operations)

                return {
                    "success": True,
                    "message": final_message,
                    "operation": operation,
                    "ai_model": ai_response.get("model"),
                    "usage": ai_response.get("usage"),
                    "executed_operations": executed_operations
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
