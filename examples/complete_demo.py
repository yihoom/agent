#!/usr/bin/env python3
"""
File Agent 完整功能演示
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from file_agent import FileAgent


def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(operation, result):
    """打印操作结果"""
    status = "✅" if result['success'] else "❌"
    print(f"{status} {operation}")
    print(f"   结果: {result['message']}")
    
    # 显示额外信息
    if result['success']:
        if 'content' in result and result['content']:
            content = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
            print(f"   内容: {content}")
        
        if 'files' in result:
            print(f"   文件数: {len(result['files'])}")
            for file_info in result['files'][:3]:  # 只显示前3个
                print(f"   📄 {file_info['name']} ({file_info.get('size', 0)} bytes)")
        
        if 'directories' in result:
            print(f"   目录数: {len(result['directories'])}")
            for dir_info in result['directories'][:3]:  # 只显示前3个
                print(f"   📁 {dir_info['name']}")
    
    print()


async def demo_basic_file_operations(agent):
    """演示基本文件操作"""
    print_section("基本文件操作演示")
    
    # 1. 创建文件
    result = await agent.execute('创建一个名为"demo.txt"的文件，内容是"这是一个演示文件"')
    print_result("创建文件", result)
    
    # 2. 读取文件
    result = await agent.execute('读取文件"demo.txt"')
    print_result("读取文件", result)
    
    # 3. 创建带时间戳的日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = await agent.execute(f'创建一个名为"log_{timestamp}.txt"的文件，内容是"日志记录: {datetime.now()}"')
    print_result("创建日志文件", result)
    
    # 4. 创建目录
    result = await agent.execute('创建一个名为"documents"的目录')
    print_result("创建目录", result)
    
    # 5. 在子目录中创建文件
    result = await agent.execute('创建一个名为"documents/readme.md"的文件，内容是"# 项目文档"')
    print_result("在子目录创建文件", result)


async def demo_file_management(agent):
    """演示文件管理功能"""
    print_section("文件管理功能演示")
    
    # 1. 列出所有文件
    result = await agent.execute('列出当前目录的所有文件')
    print_result("列出文件", result)
    
    # 2. 复制文件
    result = await agent.execute('将"demo.txt"复制为"demo_backup.txt"')
    print_result("复制文件", result)
    
    # 3. 创建多个测试文件
    for i in range(3):
        result = await agent.execute(f'创建一个名为"test_{i}.txt"的文件，内容是"测试文件 {i}"')
        print_result(f"创建测试文件 {i}", result)
    
    # 4. 再次列出文件查看变化
    result = await agent.execute('列出当前目录的所有文件')
    print_result("列出所有文件", result)


async def demo_ai_interaction(agent):
    """演示AI交互功能"""
    print_section("AI交互功能演示")
    
    # 注意：这些命令需要有效的API密钥才能工作
    ai_commands = [
        "请帮我分析当前工作目录的文件结构",
        "如何更好地组织这些文件？",
        "解释一下文件备份的重要性",
    ]
    
    for command in ai_commands:
        print(f"🤖 用户: {command}")
        result = await agent.execute(command)
        if result['success']:
            print(f"🤖 AI: {result['message'][:200]}...")
        else:
            print(f"❌ AI服务不可用: {result['message']}")
        print()


async def demo_advanced_features(agent):
    """演示高级功能"""
    print_section("高级功能演示")
    
    # 1. 显示系统状态
    status = agent.get_status()
    print("📊 系统状态:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    print()
    
    # 2. 测试错误处理
    result = await agent.execute('读取文件"不存在的文件.txt"')
    print_result("读取不存在的文件（错误处理测试）", result)
    
    # 3. 测试文件删除（会创建备份）
    result = await agent.execute('删除文件"test_0.txt"')
    print_result("删除文件（自动备份）", result)
    
    # 4. 验证备份是否创建
    if os.path.exists("backups"):
        backup_files = os.listdir("backups")
        if backup_files:
            print(f"✅ 备份文件已创建: {backup_files}")
        else:
            print("ℹ️  没有找到备份文件")
    else:
        print("ℹ️  备份目录不存在")


async def demo_cleanup(agent):
    """清理演示文件"""
    print_section("清理演示文件")
    
    # 删除演示文件
    demo_files = [
        "demo.txt", "demo_backup.txt", 
        "test_1.txt", "test_2.txt"
    ]
    
    for filename in demo_files:
        result = await agent.execute(f'删除文件"{filename}"')
        if result['success']:
            print(f"🗑️  已删除: {filename}")
    
    print("\n✨ 演示完成！")


async def main():
    """主演示函数"""
    print("🚀 File Agent 完整功能演示")
    print("=" * 60)
    
    # 检查API密钥
    has_api_key = any([
        os.getenv("OPENAI_API_KEY") and not os.getenv("OPENAI_API_KEY").startswith("your_"),
        os.getenv("ANTHROPIC_API_KEY") and not os.getenv("ANTHROPIC_API_KEY").startswith("your_"),
        os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")
    ])
    
    if not has_api_key:
        print("⚠️  警告: 未检测到有效的AI API密钥")
        print("   AI功能将不可用，但文件操作功能正常")
        print("   请在 .env 文件中配置有效的API密钥以体验完整功能")
    else:
        print("✅ 检测到AI API密钥，所有功能可用")
    
    # 创建agent实例
    try:
        agent = FileAgent()
        print(f"✅ File Agent 初始化成功")
        print(f"   工作目录: {agent.file_manager.workspace}")
        print(f"   备份启用: {agent.file_manager.backup_enabled}")
    except Exception as e:
        print(f"❌ File Agent 初始化失败: {e}")
        return
    
    try:
        # 运行各个演示
        await demo_basic_file_operations(agent)
        await demo_file_management(agent)
        
        if has_api_key:
            await demo_ai_interaction(agent)
        else:
            print_section("AI交互功能演示")
            print("⚠️  跳过AI交互演示（需要API密钥）")
        
        await demo_advanced_features(agent)
        
        # 询问是否清理
        print_section("演示结束")
        cleanup = input("是否清理演示文件？(y/N): ").lower().strip()
        if cleanup in ['y', 'yes']:
            await demo_cleanup(agent)
        else:
            print("📁 演示文件保留在workspace目录中")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
