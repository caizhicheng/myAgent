# MyAgent - 个人智能体系统

一个类似 OpenClaw 的个人使用 AI 智能体系统，运行在 Windows 环境下。

## 特性

- 🏠 **本地运行** - 数据完全本地化，保护隐私安全
- 🤖 **多模型支持** - 支持 Claude、GPT、Kimi、Minimax 等主流 LLM
- 🔧 **技能扩展** - 支持自定义技能，可扩展到数千种能力
- 💾 **智能记忆** - 三层记忆架构（短期/长期/向量）
- ⏰ **任务调度** - 支持定时任务和后台运行
- 💻 **多通道交互** - CLI、Web UI、API 等多种交互方式

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，填入你的 API Key
notepad .env
```

### 3. 运行 Agent

```bash
# 启动 CLI 交互模式
python -m src.main

# 或者使用命令行工具
myagent
```

## 项目结构

```
myAgent/
├── src/
│   ├── core/          # 核心模块（配置、LLM、记忆）
│   ├── agent/         # Agent 运行时
│   ├── skills/        # 技能库
│   ├── memory/        # 记忆系统
│   ├── channels/      # 交互通道
│   └── utils/         # 工具函数
├── config/            # 配置文件
├── data/              # 数据存储
├── logs/              # 日志文件
└── tests/             # 测试代码
```

## 使用示例

### CLI 交互

```bash
$ myagent
> 帮我查看当前目录下的所有 Python 文件
> 解释一下这个函数的作用
> 创建一个定时任务，每天早上8点提醒我开会
```

### 编程接口

```python
from src.agent.runtime import AgentRuntime

async def main():
    agent = AgentRuntime()
    
    # 对话
    response = await agent.chat("你好！")
    print(response)
    
    # 执行技能
    result = await agent.execute_skill("read_file", path="README.md")
    print(result)
```

## 开发计划

- [x] 阶段一：基础框架
  - [x] 配置管理系统
  - [x] LLM 适配层
  - [x] 记忆系统
  - [x] 技能系统
  - [x] CLI 界面
  
- [ ] 阶段二：功能完善
  - [ ] Web UI
  - [ ] 向量记忆
  - [ ] 任务调度
  - [ ] 高级技能
  
- [ ] 阶段三：生态建设
  - [ ] 插件系统
  - [ ] 技能市场
  - [ ] 文档完善

## 技术栈

- **语言**: Python 3.10+
- **框架**: LangChain + LangGraph
- **数据库**: SQLite + ChromaDB
- **CLI**: Rich + Click
- **LLM**: Claude / GPT / Kimi / Minimax

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
