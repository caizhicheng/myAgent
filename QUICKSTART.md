# 快速开始指南

## 🚀 5 分钟快速上手

### 第一步：安装依赖

```powershell
# 运行安装脚本
.\scripts\install.ps1

# 或者手动安装
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 第二步：配置 API Key

编辑 `.env` 文件，填入你的 API Key：

```env
# 选择 LLM 提供者
LLM_PROVIDER=claude

# Claude API
ANTHROPIC_API_KEY=your_api_key_here

# 或者使用 OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_api_key_here
```

### 第三步：启动 Agent

```powershell
# 方式 1: 使用启动脚本
.\scripts\start.ps1

# 方式 2: 直接运行
.\venv\Scripts\activate
python -m src.main
```

## 📖 使用教程

### 基本对话

启动后，你会看到欢迎界面：

```
================================
MyAgent v0.1.0
================================

> 你好！
```

直接输入消息即可与 Agent 对话：

```
> 你好！请介绍一下你自己

Agent: 你好！我是 MyAgent，一个智能助手...
```

### 使用技能

Agent 可以自动识别并执行技能：

```
> 列出当前目录下的所有 Python 文件

Agent: 我找到了以下 Python 文件：
- main.py
- config.py
...
```

### CLI 命令

在对话中输入 `/` 开头的命令：

- `/help` - 显示帮助
- `/clear` - 清空对话历史
- `/history` - 查看对话历史
- `/skills` - 列出所有技能
- `/config` - 查看配置
- `/quit` - 退出程序

## 🎯 示例场景

### 场景 1：文件管理

```
> 读取 README.md 文件
> 在 data 目录下创建一个 test.txt 文件，内容是"Hello World"
> 搜索所有包含 "config" 的 Python 文件
```

### 场景 2：系统监控

```
> 查看系统信息
> 列出内存占用最高的 5 个进程
> 执行 dir 命令查看当前目录
```

### 场景 3：多轮对话

```
> 我想学习 Python
> 能推荐一些学习资源吗？
> 刚才我们讨论了什么？
```

## 🔧 高级用法

### 编程接口

```python
import asyncio
from src.agent.runtime import AgentRuntime

async def main():
    agent = AgentRuntime()
    await agent.initialize()
    
    # 对话
    response = await agent.chat("你好！")
    print(response)
    
    # 执行技能
    result = await agent.execute_skill("read_file", path="README.md")
    print(result)
    
    await agent.close()

asyncio.run(main())
```

### 自定义技能

```python
from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus

class MyCustomSkill(Skill):
    name = "my_custom_skill"
    description = "我的自定义技能"
    category = "custom"
    
    parameters = {
        "input": SkillParameter(str, "输入参数", required=True)
    }
    
    async def execute(self, input: str) -> SkillResult:
        # 实现你的逻辑
        result = f"处理结果: {input}"
        
        return SkillResult(
            status=SkillStatus.SUCCESS,
            output=result
        )
```

## 📚 更多资源

- [完整文档](./spec.md)
- [API 参考](./docs/api.md)
- [技能开发指南](./docs/skills.md)
- [示例代码](./examples/)

## ❓ 常见问题

### Q: 如何切换 LLM？

A: 编辑 `.env` 文件，修改 `LLM_PROVIDER` 为 `claude`、`openai`、`kimi` 或 `minimax`。

### Q: 如何添加新的技能？

A: 在 `src/skills/custom/` 目录下创建新的 Python 文件，继承 `Skill` 基类即可。

### Q: 对话历史保存在哪里？

A: 保存在 `data/sqlite/memory.db` 数据库中。

### Q: 如何清空对话历史？

A: 在 CLI 中输入 `/clear` 命令，或删除 `data/sqlite/memory.db` 文件。

## 🐛 遇到问题？

1. 查看日志文件：`logs/agent.log`
2. 运行测试：`pytest tests/`
3. 提交 Issue：[GitHub Issues]

---

**祝你使用愉快！🎉**
