# DeepSeek 使用指南

## 🌟 关于 DeepSeek

DeepSeek 是一个优秀的中文AI模型，由深度求索公司开发。它在中文理解、代码生成和技术问答方面表现出色，特别适合中文开发者使用。

### 主要特点

- 🇨🇳 **优秀的中文支持**: 原生中文训练，理解更准确
- 💻 **强大的编程能力**: 支持多种编程语言，代码质量高
- 🔍 **专业代码审查**: 能够分析代码质量并提供改进建议
- 📚 **技术文档生成**: 高质量的技术文档和注释生成
- 💰 **成本效益**: 相比其他模型，使用成本更低

## 🚀 快速开始

### 1. 获取 API 密钥

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在控制台中创建 API 密钥
4. 复制密钥备用

### 2. 配置 API 密钥

在项目根目录的 `.env` 文件中添加：

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 使用 DeepSeek

#### 命令行方式

```bash
# 指定使用 DeepSeek
file-agent -p deepseek -c "请帮我写一个Python排序算法"

# 使用 DeepSeek Coder 模型
file-agent -p deepseek -m deepseek-coder -c "审查我的代码质量"
```

#### Python API 方式

```python
import asyncio
from file_agent import FileAgent

async def use_deepseek():
    # 创建 agent
    agent = FileAgent()
    
    # 配置使用 DeepSeek
    agent.config.set("ai.default_provider", "deepseek")
    agent.config.set("ai.default_model", "deepseek-chat")
    agent._setup_ai_provider()
    
    # 使用 DeepSeek
    result = await agent.execute("请帮我分析这个项目的代码结构")
    print(result['message'])

asyncio.run(use_deepseek())
```

## 🎯 使用场景

### 1. 代码生成

DeepSeek 在代码生成方面表现优秀：

```bash
file-agent -p deepseek -c "写一个Python函数，实现快速排序算法"
file-agent -p deepseek -c "帮我写一个处理JSON数据的类"
file-agent -p deepseek -c "创建一个简单的Web API接口"
```

### 2. 代码审查

使用 DeepSeek 进行代码质量分析：

```bash
file-agent -p deepseek -c "请审查workspace目录中的Python文件"
file-agent -p deepseek -c "分析这段代码的性能问题"
file-agent -p deepseek -c "检查代码中的潜在bug"
```

### 3. 技术文档

生成高质量的技术文档：

```bash
file-agent -p deepseek -c "为这个项目生成README文档"
file-agent -p deepseek -c "写一份API使用说明"
file-agent -p deepseek -c "创建代码注释和文档"
```

### 4. 中文技术问答

DeepSeek 在中文技术问答方面表现出色：

```bash
file-agent -p deepseek -c "解释一下Python的装饰器原理"
file-agent -p deepseek -c "如何优化数据库查询性能？"
file-agent -p deepseek -c "微服务架构的优缺点是什么？"
```

## 🔧 可用模型

### deepseek-chat
- **用途**: 通用对话和问答
- **特点**: 平衡的性能，适合大多数场景
- **推荐场景**: 技术咨询、文档生成、一般编程任务

### deepseek-coder
- **用途**: 专门的编程助手
- **特点**: 专注于代码生成和分析
- **推荐场景**: 代码生成、代码审查、算法实现

## 📝 最佳实践

### 1. 提示词优化

为了获得更好的结果，建议：

- 使用清晰、具体的中文描述
- 提供足够的上下文信息
- 明确指定期望的输出格式

```bash
# 好的提示词
file-agent -p deepseek -c "请用Python写一个冒泡排序函数，要求包含详细注释和测试用例"

# 一般的提示词
file-agent -p deepseek -c "写个排序"
```

### 2. 模型选择

- 对于一般对话和文档生成，使用 `deepseek-chat`
- 对于编程任务，优先使用 `deepseek-coder`

### 3. 错误处理

如果遇到API错误：

1. 检查API密钥是否正确
2. 确认账户余额是否充足
3. 检查网络连接
4. 查看错误日志获取详细信息

## 🎮 演示示例

运行完整的 DeepSeek 演示：

```bash
python examples/deepseek_demo.py
```

这个演示包括：
- 文件操作 + AI分析
- 代码生成示例
- 中文对话演示
- 代码审查功能
- 不同模型对比

## 🔍 故障排除

### 常见问题

1. **API密钥无效**
   - 检查 `.env` 文件中的密钥是否正确
   - 确认密钥没有过期

2. **请求超时**
   - 检查网络连接
   - 尝试减少请求的复杂度

3. **余额不足**
   - 登录 DeepSeek 平台检查账户余额
   - 充值后重试

4. **模型不可用**
   - 确认使用的模型名称正确
   - 检查模型是否在可用列表中

### 调试技巧

启用详细日志：

```bash
file-agent -v -p deepseek -c "你的命令"
```

查看日志文件：

```bash
tail -f logs/agent.log
```

## 📊 性能对比

| 特性 | DeepSeek | OpenAI | Claude |
|------|----------|--------|--------|
| 中文理解 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 代码生成 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 成本效益 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🤝 社区支持

- [DeepSeek 官方文档](https://platform.deepseek.com/docs)
- [API 参考](https://platform.deepseek.com/api-docs)
- [社区论坛](https://platform.deepseek.com/community)

## 📄 许可证

DeepSeek 的使用需要遵循其服务条款和使用协议。请在使用前仔细阅读相关条款。
