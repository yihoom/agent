"""
Command line interface for the File Agent.
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

import click
from colorama import init, Fore, Style

from .agent import FileAgent
from .config import Config

# 初始化colorama
init(autoreset=True)

# 设置日志
def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """设置日志配置。"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 创建日志目录
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_banner():
    """打印欢迎横幅。"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                        File Agent v0.1.0                    ║
║                   智能文件管理代理                           ║
║                                                              ║
║  支持自然语言文件操作 + AI智能助手                          ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_help():
    """打印帮助信息。"""
    help_text = f"""
{Fore.YELLOW}可用命令：{Style.RESET_ALL}
  {Fore.GREEN}文件操作：{Style.RESET_ALL}
    • 创建文件 "filename.txt"
    • 读取文件 "filename.txt"
    • 删除文件 "filename.txt"
    • 列出文件
    • 创建目录 "dirname"
  
  {Fore.GREEN}系统命令：{Style.RESET_ALL}
    • help, h - 显示帮助
    • status - 显示系统状态
    • config - 显示配置信息
    • exit, quit, q - 退出程序
  
  {Fore.GREEN}AI助手：{Style.RESET_ALL}
    • 任何其他输入都会发送给AI助手处理
    
{Fore.YELLOW}示例：{Style.RESET_ALL}
  创建一个包含当前时间的日志文件
  读取 "config.yaml" 文件
  列出所有 .py 文件
  帮我分析这个项目的结构
"""
    print(help_text)


def format_result(result: dict) -> str:
    """格式化执行结果。"""
    if result["success"]:
        message = f"{Fore.GREEN}✓ {result['message']}{Style.RESET_ALL}"
        
        # 添加额外信息
        if "content" in result:
            content = result["content"]
            if len(content) > 200:
                content = content[:200] + "..."
            message += f"\n{Fore.CYAN}内容预览：{Style.RESET_ALL}\n{content}"
        
        if "files" in result:
            files = result["files"][:10]  # 只显示前10个文件
            if files:
                message += f"\n{Fore.CYAN}文件列表：{Style.RESET_ALL}"
                for file_info in files:
                    size = f" ({file_info['size']} bytes)" if file_info['size'] else ""
                    message += f"\n  📄 {file_info['name']}{size}"
                
                if len(result["files"]) > 10:
                    message += f"\n  ... 还有 {len(result['files']) - 10} 个文件"
        
        if "directories" in result:
            dirs = result["directories"][:5]  # 只显示前5个目录
            if dirs:
                message += f"\n{Fore.CYAN}目录列表：{Style.RESET_ALL}"
                for dir_info in dirs:
                    message += f"\n  📁 {dir_info['name']}"
                
                if len(result["directories"]) > 5:
                    message += f"\n  ... 还有 {len(result['directories']) - 5} 个目录"
        
        if "ai_message" in result:
            message += f"\n{Fore.MAGENTA}AI助手：{Style.RESET_ALL} {result['ai_message']}"
        
        if "usage" in result and result["usage"]:
            usage = result["usage"]
            if "total_tokens" in usage:
                message += f"\n{Fore.YELLOW}Token使用：{Style.RESET_ALL} {usage['total_tokens']}"
    else:
        message = f"{Fore.RED}✗ {result['message']}{Style.RESET_ALL}"
    
    return message


async def interactive_mode(agent: FileAgent):
    """交互式模式。"""
    print_banner()
    print(f"{Fore.YELLOW}输入 'help' 查看帮助，输入 'exit' 退出{Style.RESET_ALL}\n")
    
    while True:
        try:
            # 获取用户输入
            user_input = input(f"{Fore.BLUE}File Agent> {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue
            
            # 处理系统命令
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"{Fore.YELLOW}再见！{Style.RESET_ALL}")
                break
            elif user_input.lower() in ['help', 'h']:
                print_help()
                continue
            elif user_input.lower() == 'status':
                status = agent.get_status()
                print(f"{Fore.CYAN}系统状态：{Style.RESET_ALL}")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                continue
            elif user_input.lower() == 'config':
                ai_config = agent.config.get_ai_config()
                fm_config = agent.config.get_file_manager_config()
                print(f"{Fore.CYAN}配置信息：{Style.RESET_ALL}")
                print(f"  AI提供商: {ai_config['provider']}")
                print(f"  AI模型: {ai_config['model']}")
                print(f"  工作目录: {fm_config['workspace']}")
                print(f"  备份启用: {fm_config['backup_enabled']}")
                continue
            
            # 执行用户命令
            print(f"{Fore.YELLOW}正在处理...{Style.RESET_ALL}")
            result = await agent.execute(user_input)
            
            # 显示结果
            print(format_result(result))
            print()  # 空行分隔
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}程序被中断，再见！{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}发生错误: {str(e)}{Style.RESET_ALL}")


@click.command()
@click.option('--command', '-c', help='执行单个命令')
@click.option('--workspace', '-w', help='指定工作目录')
@click.option('--config', '-f', help='指定配置文件')
@click.option('--provider', '-p', help='指定AI提供商 (openai, anthropic, google, deepseek)')
@click.option('--model', '-m', help='指定AI模型')
@click.option('--verbose', '-v', is_flag=True, help='详细输出')
def main(command, workspace, config, provider, model, verbose):
    """File Agent - 智能文件管理代理"""
    
    # 设置日志
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level, "./logs/agent.log")
    
    try:
        # 创建代理实例
        agent = FileAgent(config)
        
        # 应用命令行参数覆盖配置
        if workspace:
            agent.config.set("file_manager.default_workspace", workspace)
            # 重新初始化文件管理器
            fm_config = agent.config.get_file_manager_config()
            agent.file_manager = FileManager(
                workspace=fm_config["workspace"],
                backup_enabled=fm_config["backup_enabled"]
            )
        
        if provider:
            agent.config.set("ai.default_provider", provider)
            agent._setup_ai_provider()
        
        if model:
            agent.config.set("ai.default_model", model)
            agent._setup_ai_provider()
        
        # 执行单个命令或进入交互模式
        if command:
            # 单命令模式
            result = asyncio.run(agent.execute(command))
            print(format_result(result))
        else:
            # 交互模式
            asyncio.run(interactive_mode(agent))
    
    except Exception as e:
        print(f"{Fore.RED}启动失败: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
