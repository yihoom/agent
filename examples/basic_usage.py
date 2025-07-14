#!/usr/bin/env python3
"""
File Agent 基本使用示例
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from file_agent import FileAgent


async def main():
    """主函数演示基本用法。"""
    print("=== File Agent 基本使用示例 ===\n")
    
    # 创建agent实例
    agent = FileAgent()
    
    # 显示系统状态
    print("1. 系统状态:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    print()
    
    # 创建文件
    print("2. 创建文件:")
    result = await agent.execute('创建一个名为"hello.txt"的文件，内容是"Hello, World!"')
    print(f"   结果: {result['message']}")
    print()
    
    # 读取文件
    print("3. 读取文件:")
    result = await agent.execute('读取文件"hello.txt"')
    if result['success']:
        print(f"   内容: {result.get('content', 'N/A')}")
    else:
        print(f"   错误: {result['message']}")
    print()
    
    # 列出文件
    print("4. 列出文件:")
    result = await agent.execute('列出当前目录的所有文件')
    if result['success']:
        print(f"   找到 {result.get('total_files', 0)} 个文件")
        for file_info in result.get('files', [])[:3]:  # 只显示前3个
            print(f"   - {file_info['name']} ({file_info.get('size', 0)} bytes)")
    print()
    
    # 创建目录
    print("5. 创建目录:")
    result = await agent.execute('创建一个名为"test_dir"的目录')
    print(f"   结果: {result['message']}")
    print()
    
    # AI助手对话
    print("6. AI助手对话:")
    result = await agent.execute('请帮我分析一下当前工作目录的结构')
    if result['success']:
        print(f"   AI回复: {result['message'][:200]}...")
    else:
        print(f"   错误: {result['message']}")
    print()
    
    # 复制文件
    print("7. 复制文件:")
    result = await agent.execute('将"hello.txt"复制为"hello_copy.txt"')
    print(f"   结果: {result['message']}")
    print()
    
    # 最终文件列表
    print("8. 最终文件列表:")
    result = await agent.execute('列出所有文件')
    if result['success']:
        print(f"   总计: {result.get('total_files', 0)} 个文件, {result.get('total_directories', 0)} 个目录")
        for file_info in result.get('files', []):
            print(f"   📄 {file_info['name']}")
        for dir_info in result.get('directories', []):
            print(f"   📁 {dir_info['name']}")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    # 检查是否设置了API密钥
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("警告: 未检测到AI API密钥，AI功能将不可用")
        print("请设置环境变量: OPENAI_API_KEY, ANTHROPIC_API_KEY, 或 GOOGLE_API_KEY")
        print("文件操作功能仍然可用\n")
    
    asyncio.run(main())
