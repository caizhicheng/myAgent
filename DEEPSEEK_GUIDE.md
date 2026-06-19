# DeepSeek 模型配置指南

## 📝 修改说明

已成功适配 DeepSeek 模型！以下是修改的文件：

### 1. 环境变量配置 (.env.example)
- ✅ 添加 DeepSeek API 配置项
- ✅ 默认设置为 DeepSeek 提供者

### 2. 配置管理 (src/core/config.py)
- ✅ 添加 DeepSeek 环境变量字段
- ✅ 添加 DeepSeek 配置获取逻辑

### 3. LLM 适配层 (src/core/llm.py)
- ✅ 新增 DeepSeekProvider 类
- ✅ 注册到 LLMFactory

### 4. 系统配置 (config/settings.yaml)
- ✅ 添加 DeepSeek 模型配置
- ✅ 默认提供者改为 DeepSeek

## 🚀 快速开始

### 步骤 1: 创建 .env 文件

```powershell
# 复制模板
copy .env.example .env

# 编辑 .env 文件
notepad .env
```

### 步骤 2: 配置 DeepSeek API Key

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
# LLM Provider Configuration
LLM_PROVIDER=deepseek

# DeepSeek API
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### 步骤 3: 启动 Agent

```powershell
# 方式 1: 使用启动脚本
.\scripts\start.ps1

# 方式 2: 直接运行
.\venv\Scripts\activate
python -m src.main
```

## 🎯 可用的 DeepSeek 模型

### DeepSeek Chat
- **模型名称**: `deepseek-chat`
- **适用场景**: 日常对话、问答、文本生成
- **推荐用途**: 通用对话、技能调用

### DeepSeek Coder
- **模型名称**: `deepseek-coder`
- **适用场景**: 代码生成、代码解释、编程辅助
- **推荐用途**: 代码相关任务

### 切换模型

在 `.env` 文件中修改：

```env
# 使用 DeepSeek Chat
DEEPSEEK_MODEL=deepseek-chat

# 或使用 DeepSeek Coder
DEEPSEEK_MODEL=deepseek-coder
```

## 💡 使用示例

### 基本对话

```
> 你好！请介绍一下你自己

Agent: 你好！我是 MyAgent，一个智能助手...
```

### 代码生成（使用 DeepSeek Coder）

```
> 写一个 Python 函数，计算斐波那契数列

Agent: 好的，这是一个计算斐波那契数列的 Python 函数：

def fibonacci(n):
    """计算斐波那契数列的第 n 项"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 技能调用

```
> 读取 README.md 文件

Agent: 我来帮你读取 README.md 文件...
[调用 read_file 技能]
```

## 🔧 高级配置

### 调整温度参数

在 `config/settings.yaml` 中修改：

```yaml
llm:
  models:
    deepseek:
      model: "deepseek-chat"
      max_tokens: 4096
      temperature: 0.7  # 0.0-1.0，值越低越确定，值越高越随机
```

### 自定义 Base URL

如果你使用 DeepSeek 的代理或私有部署：

```env
DEEPSEEK_BASE_URL=https://your-custom-endpoint.com/v1
```

## 📊 性能对比

| 模型 | 速度 | 质量 | 成本 | 推荐场景 |
|------|------|------|------|----------|
| deepseek-chat | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 日常对话、通用任务 |
| deepseek-coder | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 代码生成、编程辅助 |

## ⚠️ 注意事项

### 1. API Key 安全
- 不要将 `.env` 文件提交到 Git
- 定期更换 API Key
- 使用环境变量管理敏感信息

### 2. 费用控制
- DeepSeek 按 token 计费
- 可以在 `config/settings.yaml` 中设置 `max_tokens` 限制
- 建议开启对话历史清理功能

### 3. 模型限制
- DeepSeek Chat: 最大上下文 64K tokens
- DeepSeek Coder: 最大上下文 16K tokens
- 注意对话历史长度，避免超出限制

## 🐛 常见问题

### Q: 提示 "不支持的 LLM 提供者: deepseek"
**A**: 确保已更新到最新代码，检查 `src/core/llm.py` 中是否包含 `DeepSeekProvider`

### Q: API 调用失败
**A**: 检查以下几点：
1. API Key 是否正确
2. Base URL 是否正确
3. 网络连接是否正常
4. API 余额是否充足

### Q: 如何查看详细错误日志？
**A**: 查看 `logs/agent.log` 文件

### Q: 如何切换回其他模型？
**A**: 修改 `.env` 文件中的 `LLM_PROVIDER`：
```env
LLM_PROVIDER=openai  # 或 claude, kimi, minimax
```

## 📚 相关文档

- [DeepSeek 官方文档](https://platform.deepseek.com/docs)
- [API 定价](https://platform.deepseek.com/pricing)
- [快速开始指南](./QUICKSTART.md)
- [完整设计方案](./spec.md)

---

**配置完成后，即可开始使用 DeepSeek 模型！** 🎉
