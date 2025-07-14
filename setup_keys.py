#!/usr/bin/env python3
"""
安全的API密钥设置脚本
"""

import os
import yaml
import getpass
from pathlib import Path


def setup_api_keys():
    """交互式设置API密钥"""
    print("🔐 API密钥安全设置")
    print("=" * 40)
    print("此脚本将帮助你安全地设置API密钥")
    print("密钥将保存在本地配置文件中，不会被提交到版本控制")
    print()
    
    # 检查是否已有本地配置
    local_config_path = Path("config.local.yaml")
    config = {}
    
    if local_config_path.exists():
        print("📁 发现现有的本地配置文件")
        choice = input("是否要更新现有配置？(y/N): ").lower().strip()
        if choice in ['y', 'yes']:
            with open(local_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        else:
            print("取消设置")
            return
    
    # 确保配置结构存在
    if 'api_keys' not in config:
        config['api_keys'] = {}
    
    # API提供商信息
    providers = {
        'openai': {
            'name': 'OpenAI',
            'url': 'https://platform.openai.com/api-keys',
            'description': 'GPT模型提供商'
        },
        'anthropic': {
            'name': 'Anthropic',
            'url': 'https://console.anthropic.com/',
            'description': 'Claude模型提供商'
        },
        'google': {
            'name': 'Google',
            'url': 'https://makersuite.google.com/app/apikey',
            'description': 'Gemini模型提供商'
        },
        'deepseek': {
            'name': 'DeepSeek',
            'url': 'https://platform.deepseek.com/',
            'description': '中文优化AI模型'
        }
    }
    
    print("🔑 设置API密钥")
    print("提示：直接按回车跳过某个提供商")
    print()
    
    for provider_id, provider_info in providers.items():
        print(f"📌 {provider_info['name']} ({provider_info['description']})")
        print(f"   获取密钥: {provider_info['url']}")
        
        # 显示当前密钥状态
        current_key = config['api_keys'].get(provider_id, '')
        if current_key:
            masked_key = current_key[:8] + '*' * (len(current_key) - 8) if len(current_key) > 8 else '*' * len(current_key)
            print(f"   当前密钥: {masked_key}")
        
        # 输入新密钥
        new_key = getpass.getpass(f"   输入{provider_info['name']} API密钥 (隐藏输入): ").strip()
        
        if new_key:
            config['api_keys'][provider_id] = new_key
            print(f"   ✅ {provider_info['name']} 密钥已设置")
        elif not current_key:
            print(f"   ⏭️  跳过 {provider_info['name']}")
        else:
            print(f"   📋 保持现有 {provider_info['name']} 密钥")
        print()
    
    # 设置默认提供商
    print("🎯 设置默认AI提供商")
    available_providers = [p for p in providers.keys() if config['api_keys'].get(p)]
    
    if available_providers:
        print("可用的提供商:")
        for i, provider in enumerate(available_providers, 1):
            print(f"  {i}. {providers[provider]['name']} ({provider})")
        
        try:
            choice = input(f"选择默认提供商 (1-{len(available_providers)}) [1]: ").strip()
            if not choice:
                choice = "1"
            
            provider_index = int(choice) - 1
            if 0 <= provider_index < len(available_providers):
                default_provider = available_providers[provider_index]
                
                if 'ai' not in config:
                    config['ai'] = {}
                config['ai']['default_provider'] = default_provider
                print(f"✅ 默认提供商设置为: {providers[default_provider]['name']}")
            else:
                print("⚠️  无效选择，使用第一个可用提供商")
                config['ai'] = {'default_provider': available_providers[0]}
        except ValueError:
            print("⚠️  无效输入，使用第一个可用提供商")
            config['ai'] = {'default_provider': available_providers[0]}
    
    # 保存配置
    try:
        with open(local_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n✅ 配置已保存到 {local_config_path}")
        print("🔒 此文件已被 .gitignore 忽略，不会被提交到版本控制")
        
        # 设置文件权限（仅限Unix系统）
        if os.name != 'nt':  # 不是Windows
            os.chmod(local_config_path, 0o600)  # 仅所有者可读写
            print("🛡️  文件权限已设置为仅所有者可访问")
        
        print("\n🎉 设置完成！现在你可以安全地使用File Agent了")
        print("\n💡 使用提示:")
        print("   file-agent                    # 使用默认提供商")
        print(f"   file-agent -p {config.get('ai', {}).get('default_provider', 'deepseek')}           # 明确指定提供商")
        
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")


def show_current_config():
    """显示当前配置状态"""
    print("📋 当前API密钥配置状态")
    print("=" * 30)
    
    local_config_path = Path("config.local.yaml")
    if not local_config_path.exists():
        print("❌ 未找到本地配置文件")
        print("💡 运行 'python setup_keys.py' 来设置API密钥")
        return
    
    try:
        with open(local_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        api_keys = config.get('api_keys', {})
        providers = ['openai', 'anthropic', 'google', 'deepseek']
        
        for provider in providers:
            key = api_keys.get(provider, '')
            if key:
                masked_key = key[:8] + '*' * (len(key) - 8) if len(key) > 8 else '*' * len(key)
                print(f"✅ {provider.ljust(10)}: {masked_key}")
            else:
                print(f"❌ {provider.ljust(10)}: 未设置")
        
        default_provider = config.get('ai', {}).get('default_provider', '未设置')
        print(f"\n🎯 默认提供商: {default_provider}")
        
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_current_config()
    else:
        setup_api_keys()


if __name__ == "__main__":
    main()
