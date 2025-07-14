# File Agent

一个集成了文件管理和AI能力的智能代理，支持主流大模型API。这是一个学习项目，展示了如何构建一个功能完整的AI文件管理助手。

## 🌟 功能特性

- 🗂️ **智能文件管理**: 支持文件的创建、读取、写入、删除、移动、复制等操作
- 🤖 **多AI提供商集成**: 支持OpenAI、Claude、Gemini、DeepSeek等主流大模型API
- 💬 **自然语言交互**: 通过中文自然语言与AI交互，执行文件操作
- ⚙️ **灵活配置管理**: 支持YAML配置文件和环境变量配置
- 🔒 **安全文件操作**: 自动备份、路径验证、错误处理
- 📝 **完整日志记录**: 详细的操作日志和错误追踪
- 🧪 **完善测试覆盖**: 单元测试确保代码质量
- 🎯 **命令行界面**: 支持交互式和单命令模式

## 🚀 快速开始

### 自动安装

```bash
# 克隆项目
git clone <repository-url>
cd file-agent

# 运行安装脚本
python install.py
```

### 手动安装

1. **安装依赖**：
```bash
pip install -r requirements.txt
```

2. **安装包**：
```bash
pip install -e .
```

3. **配置API密钥**：
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

## 📖 使用方法

### 命令行界面

#### 交互式模式
```bash
file-agent
```

#### 单命令模式
```bash
# 创建文件
file-agent -c "创建一个名为\"hello.txt\"的文件，内容是\"Hello World\""

# 读取文件
file-agent -c "读取文件\"hello.txt\""

# 列出文件
file-agent -c "列出当前目录的所有文件"

# 指定工作目录
file-agent --workspace ./my-workspace -c "创建文件\"test.txt\""
```

#### 命令行选项
```bash
file-agent --help

Options:
  -c, --command TEXT    执行单个命令
  -w, --workspace TEXT  指定工作目录
  -f, --config TEXT     指定配置文件
  -p, --provider TEXT   指定AI提供商 (openai, anthropic, google, deepseek)
  -m, --model TEXT      指定AI模型
  -v, --verbose         详细输出
```

### Python API

```python
import asyncio
from file_agent import FileAgent

async def main():
    # 创建agent实例
    agent = FileAgent()

    # 执行文件操作
    result = await agent.execute("创建一个名为\"demo.txt\"的文件")
    print(f"结果: {result['message']}")

    # 读取文件
    result = await agent.execute("读取文件\"demo.txt\"")
    if result['success']:
        print(f"内容: {result['content']}")

    # AI对话
    result = await agent.execute("请帮我分析当前目录的文件结构")
    print(f"AI回复: {result['message']}")

# 运行
asyncio.run(main())
```

## ⚙️ 配置

### 环境变量配置

在 `.env` 文件中配置：

```bash
# AI API密钥
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 默认设置
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-3.5-turbo
DEFAULT_WORKSPACE=./workspace

# 文件管理设置
MAX_FILE_SIZE_MB=10
BACKUP_ENABLED=true
BACKUP_DIR=./backups

# 日志设置
LOG_LEVEL=INFO
LOG_FILE=./logs/agent.log
```

### YAML配置文件

创建 `config.yaml`：

```yaml
ai:
  default_provider: openai  # 可选: openai, anthropic, google, deepseek
  default_model: gpt-3.5-turbo
  max_tokens: 1000
  temperature: 0.7

file_manager:
  default_workspace: ./workspace
  max_file_size_mb: 10
  backup_enabled: true
  backup_dir: ./backups

logging:
  level: INFO
  file: ./logs/agent.log
```

## 🎯 支持的命令

### 文件操作命令

| 命令 | 示例 | 说明 |
|------|------|------|
| 创建文件 | `创建一个名为"test.txt"的文件，内容是"Hello"` | 创建新文件 |
| 读取文件 | `读取文件"test.txt"` | 读取文件内容 |
| 删除文件 | `删除文件"test.txt"` | 删除文件（自动备份） |
| 复制文件 | `将"test.txt"复制为"backup.txt"` | 复制文件 |
| 创建目录 | `创建一个名为"docs"的目录` | 创建目录 |
| 列出文件 | `列出当前目录的文件` | 列出文件和目录 |

### 系统命令

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助信息 |
| `status` | 显示系统状态 |
| `config` | 显示配置信息 |
| `exit` | 退出程序 |

### AI对话

任何不匹配文件操作的输入都会发送给AI助手处理，例如：
- "请帮我分析这个项目的结构"
- "如何优化我的代码？"
- "解释一下这个错误信息"

### DeepSeek特别说明

DeepSeek是一个优秀的中文AI模型，特别适合：
- 🇨🇳 **中文对话**: 优秀的中文理解和生成能力
- 💻 **代码生成**: 强大的编程能力，支持多种编程语言
- 🔍 **代码审查**: 专业的代码质量分析
- 📚 **技术文档**: 高质量的技术文档生成

获取DeepSeek API密钥: https://platform.deepseek.com/

使用DeepSeek的示例：
```bash
# 设置DeepSeek为默认提供商
file-agent -p deepseek -c "请帮我写一个Python排序算法"

# 运行DeepSeek专门演示
python examples/deepseek_demo.py
```

## 🧪 开发和测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_file_manager.py -v

# 运行测试并显示覆盖率
pytest --cov=file_agent
```

### 代码质量

```bash
# 代码格式化
black file_agent tests

# 代码检查
flake8 file_agent tests

# 类型检查
mypy file_agent
```

### 项目结构

```
file-agent/
├── file_agent/           # 主要代码
│   ├── __init__.py
│   ├── agent.py         # 主代理类
│   ├── file_manager.py  # 文件管理器
│   ├── ai_providers.py  # AI提供商集成
│   ├── config.py        # 配置管理
│   └── cli.py           # 命令行界面
├── tests/               # 测试代码
├── examples/            # 使用示例
├── workspace/           # 默认工作目录
├── backups/            # 备份目录
├── logs/               # 日志目录
├── config.yaml         # 配置文件示例
├── .env.example        # 环境变量示例
└── README.md           # 项目文档
```

## 📚 学习要点

这个项目展示了以下技术和概念：

1. **异步编程**: 使用 `asyncio` 处理AI API调用
2. **设计模式**: 工厂模式、策略模式的应用
3. **配置管理**: 多层次配置系统设计
4. **错误处理**: 完善的异常处理和日志记录
5. **测试驱动开发**: 完整的单元测试覆盖
6. **命令行工具**: 使用 `click` 构建CLI
7. **自然语言处理**: 简单的命令解析逻辑
8. **文件系统操作**: 安全的文件操作实践

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
