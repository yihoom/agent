#!/usr/bin/env python3
"""
DeepSeek AI 提供商演示
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 加载环境变量
load_dotenv()

from file_agent import FileAgent


async def demo_deepseek():
    """演示DeepSeek AI功能"""
    print("🚀 DeepSeek AI 提供商演示")
    print("=" * 50)
    
    # 检查DeepSeek API密钥
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key or deepseek_key.startswith("your_"):
        print("❌ 错误: 未找到有效的DeepSeek API密钥")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        print("获取API密钥: https://platform.deepseek.com/")
        return
    
    print(f"✅ 检测到DeepSeek API密钥: {deepseek_key[:10]}...")
    
    try:
        # 创建使用DeepSeek的agent实例
        agent = FileAgent()
        
        # 设置使用DeepSeek提供商
        agent.config.set("ai.default_provider", "deepseek")
        agent.config.set("ai.default_model", "deepseek-chat")
        
        # 重新初始化AI提供商
        agent._setup_ai_provider()
        
        print(f"✅ 已切换到DeepSeek提供商")
        print(f"   模型: {agent.ai_provider.model}")
        print()
        
        # 演示文件操作 + AI交互
        print("📝 演示1: 创建文件并让AI分析")
        result = await agent.execute('创建一个名为"deepseek_test.py"的文件，内容是"print(\'Hello DeepSeek!\')"')
        print(f"   文件创建: {result['message']}")
        
        if result['success']:
            # 让AI分析文件
            result = await agent.execute("请分析刚创建的Python文件，并给出改进建议")
            if result['success']:
                print(f"   AI分析: {result['message'][:200]}...")
            else:
                print(f"   AI分析失败: {result['message']}")
        print()
        
        # 演示AI编程助手功能
        print("💻 演示2: AI编程助手")
        result = await agent.execute("请帮我写一个Python函数，用于计算斐波那契数列")
        if result['success']:
            print(f"   AI回复: {result['message'][:300]}...")
        else:
            print(f"   AI回复失败: {result['message']}")
        print()
        
        # 演示中文对话
        print("🗣️ 演示3: 中文对话")
        result = await agent.execute("你好！请介绍一下DeepSeek的特点和优势")
        if result['success']:
            print(f"   AI回复: {result['message'][:300]}...")
        else:
            print(f"   AI回复失败: {result['message']}")
        print()
        
        # 演示代码审查
        print("🔍 演示4: 代码审查")
        result = await agent.execute("请审查workspace目录中的Python文件，给出代码质量评估")
        if result['success']:
            print(f"   AI回复: {result['message'][:300]}...")
        else:
            print(f"   AI回复失败: {result['message']}")
        print()
        
        # 显示使用统计
        if hasattr(agent.ai_provider, 'client'):
            print("📊 使用统计:")
            print("   所有演示完成，DeepSeek API调用成功")
        
        print("✨ DeepSeek演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")


async def demo_model_comparison():
    """演示不同DeepSeek模型的对比"""
    print("\n🔬 DeepSeek模型对比演示")
    print("=" * 50)
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key or deepseek_key.startswith("your_"):
        print("⚠️  跳过模型对比演示（需要API密钥）")
        return
    
    models = ["deepseek-chat", "deepseek-coder"]
    prompt = "请用Python写一个简单的排序算法"
    
    for model in models:
        print(f"\n🤖 测试模型: {model}")
        try:
            agent = FileAgent()
            agent.config.set("ai.default_provider", "deepseek")
            agent.config.set("ai.default_model", model)
            agent._setup_ai_provider()
            
            result = await agent.execute(prompt)
            if result['success']:
                print(f"   回复长度: {len(result['message'])} 字符")
                print(f"   回复预览: {result['message'][:150]}...")
                if 'usage' in result:
                    print(f"   Token使用: {result['usage']}")
            else:
                print(f"   错误: {result['message']}")
        except Exception as e:
            print(f"   异常: {e}")


async def main():
    """主函数"""
    await demo_deepseek()
    await demo_model_comparison()


if __name__ == "__main__":
    asyncio.run(main())
