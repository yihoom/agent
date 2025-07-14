#!/usr/bin/env python3
"""
File Agent 安装脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """运行命令并返回结果。"""
    print(f"执行: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False


def check_python_version():
    """检查Python版本。"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """安装依赖包。"""
    print("\n=== 安装依赖包 ===")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip"):
        print("警告: pip升级失败，继续安装...")
    
    # 安装依赖
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        print("错误: 依赖安装失败")
        return False
    
    print("✓ 依赖安装完成")
    return True


def create_directories():
    """创建必要的目录。"""
    print("\n=== 创建目录结构 ===")
    
    directories = [
        "workspace",
        "backups", 
        "logs",
        "examples"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    return True


def setup_environment():
    """设置环境配置。"""
    print("\n=== 设置环境配置 ===")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ 创建 .env 文件")
        print("请编辑 .env 文件，添加你的API密钥")
    else:
        print("✓ .env 文件已存在")
    
    return True


def install_package():
    """安装包到系统。"""
    print("\n=== 安装File Agent包 ===")
    
    if not run_command(f"{sys.executable} -m pip install -e ."):
        print("错误: 包安装失败")
        return False
    
    print("✓ File Agent包安装完成")
    return True


def run_tests():
    """运行测试。"""
    print("\n=== 运行测试 ===")
    
    if not run_command("python -m pytest tests/ -v", check=False):
        print("警告: 部分测试失败，但安装可以继续")
    else:
        print("✓ 所有测试通过")
    
    return True


def show_usage_info():
    """显示使用信息。"""
    print("\n" + "="*50)
    print("🎉 File Agent 安装完成!")
    print("="*50)
    
    print("\n📖 使用方法:")
    print("1. 命令行模式:")
    print("   file-agent                    # 交互式模式")
    print("   file-agent -c '创建文件test.txt'  # 单命令模式")
    
    print("\n2. Python API:")
    print("   from file_agent import FileAgent")
    print("   agent = FileAgent()")
    print("   result = await agent.execute('你的命令')")
    
    print("\n3. 运行示例:")
    print("   python examples/basic_usage.py")
    
    print("\n⚙️ 配置:")
    print("1. 编辑 .env 文件，添加API密钥:")
    print("   OPENAI_API_KEY=your_key_here")
    print("   ANTHROPIC_API_KEY=your_key_here")
    print("   GOOGLE_API_KEY=your_key_here")
    
    print("\n2. 可选：编辑 config.yaml 自定义配置")
    
    print("\n📚 更多信息请查看 README.md")


def main():
    """主安装流程。"""
    print("File Agent 安装程序")
    print("="*30)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 创建目录
    if not create_directories():
        sys.exit(1)
    
    # 设置环境
    if not setup_environment():
        sys.exit(1)
    
    # 安装包
    if not install_package():
        sys.exit(1)
    
    # 运行测试
    run_tests()
    
    # 显示使用信息
    show_usage_info()


if __name__ == "__main__":
    main()
