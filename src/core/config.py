"""
配置管理模块
负责加载和管理系统配置
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LLMModelConfig(BaseModel):
    """LLM 模型配置"""

    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7


class LLMConfig(BaseModel):
    """LLM 配置"""

    provider: str = "claude"
    models: Dict[str, LLMModelConfig] = Field(default_factory=dict)


class ShortTermMemoryConfig(BaseModel):
    """短期记忆配置"""

    enabled: bool = True
    max_turns: int = 20
    database: str = "./data/sqlite/memory.db"


class LongTermMemoryConfig(BaseModel):
    """长期记忆配置"""

    enabled: bool = True
    database: str = "./data/sqlite/knowledge.db"


class VectorMemoryConfig(BaseModel):
    """向量记忆配置"""

    enabled: bool = False
    database: str = "./data/chroma"
    collection: str = "agent_memory"


class MemoryConfig(BaseModel):
    """记忆系统配置"""

    short_term: ShortTermMemoryConfig = Field(default_factory=ShortTermMemoryConfig)
    long_term: LongTermMemoryConfig = Field(default_factory=LongTermMemoryConfig)
    vector: VectorMemoryConfig = Field(default_factory=VectorMemoryConfig)


class SkillSecurityConfig(BaseModel):
    """技能安全配置"""

    allowed_commands: list[str] = Field(default_factory=list)
    max_command_timeout: int = 30
    sandbox_mode: bool = False


class SkillsConfig(BaseModel):
    """技能配置"""

    enabled: bool = True
    auto_load: bool = True
    skill_dirs: list[str] = Field(default_factory=list)
    security: SkillSecurityConfig = Field(default_factory=SkillSecurityConfig)


class CLIChannelConfig(BaseModel):
    """CLI 通道配置"""

    enabled: bool = True
    prompt_style: str = ">"
    history_file: str = "./data/.cli_history"


class APIChannelConfig(BaseModel):
    """API 通道配置"""

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8000


class WebUIChannelConfig(BaseModel):
    """Web UI 通道配置"""

    enabled: bool = False


class ChannelsConfig(BaseModel):
    """通道配置"""

    cli: CLIChannelConfig = Field(default_factory=CLIChannelConfig)
    api: APIChannelConfig = Field(default_factory=APIChannelConfig)
    webui: WebUIChannelConfig = Field(default_factory=WebUIChannelConfig)


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = "INFO"
    file: str = "./logs/agent.log"
    rotation: str = "10 MB"
    retention: str = "7 days"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"


class SecurityConfig(BaseModel):
    """安全配置"""

    encrypt_sensitive_data: bool = True
    api_key_encryption_key: str = ""


class AgentConfig(BaseModel):
    """Agent 配置"""

    name: str = "MyAgent"
    version: str = "0.1.0"
    description: str = "个人智能助手"
    max_memory_turns: int = 20
    temperature: float = 0.7
    max_tokens: int = 4096


class Settings(BaseSettings):
    """系统设置"""

    # 环境变量配置
    llm_provider: str = Field(default="claude", alias="LLM_PROVIDER")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", alias="ANTHROPIC_MODEL")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    kimi_api_key: Optional[str] = Field(default=None, alias="KIMI_API_KEY")
    kimi_base_url: str = Field(default="https://api.moonshot.cn/v1", alias="KIMI_BASE_URL")
    kimi_model: str = Field(default="moonshot-v1-8k", alias="KIMI_MODEL")
    minimax_api_key: Optional[str] = Field(default=None, alias="MINIMAX_API_KEY")
    minimax_group_id: Optional[str] = Field(default=None, alias="MINIMAX_GROUP_ID")
    minimax_model: str = Field(default="abab6.5-chat", alias="MINIMAX_MODEL")

    agent_name: str = Field(default="MyAgent", alias="AGENT_NAME")
    agent_max_memory_turns: int = Field(default=20, alias="AGENT_MAX_MEMORY_TURNS")
    agent_temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")

    database_path: str = Field(default="./data/sqlite/agent.db", alias="DATABASE_PATH")
    vector_db_path: str = Field(default="./data/chroma", alias="VECTOR_DB_PATH")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="./logs/agent.log", alias="LOG_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class Config:
    """配置管理器"""

    _instance: Optional["Config"] = None
    _initialized: bool = False

    def __new__(cls) -> "Config":
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化配置"""
        if self._initialized:
            return

        # 加载环境变量
        load_dotenv()

        # 加载配置文件
        self.config_dir = Path("config")
        self.settings = Settings()

        # 加载 YAML 配置
        self._load_yaml_configs()

        # 初始化日志
        self._setup_logging()

        # 创建必要的目录
        self._create_directories()

        Config._initialized = True
        logger.info("配置管理器初始化完成")

    def _load_yaml_configs(self):
        """加载 YAML 配置文件"""
        # 加载主配置
        settings_file = self.config_dir / "settings.yaml"
        if settings_file.exists():
            with open(settings_file, "r", encoding="utf-8") as f:
                settings_data = yaml.safe_load(f)
                self.agent = AgentConfig(**settings_data.get("agent", {}))
                self.llm = LLMConfig(**settings_data.get("llm", {}))
                self.memory = MemoryConfig(**settings_data.get("memory", {}))
                self.skills = SkillsConfig(**settings_data.get("skills", {}))
                self.channels = ChannelsConfig(**settings_data.get("channels", {}))
                self.logging = LoggingConfig(**settings_data.get("logging", {}))
                self.security = SecurityConfig(**settings_data.get("security", {}))
        else:
            # 使用默认配置
            self.agent = AgentConfig()
            self.llm = LLMConfig()
            self.memory = MemoryConfig()
            self.skills = SkillsConfig()
            self.channels = ChannelsConfig()
            self.logging = LoggingConfig()
            self.security = SecurityConfig()

        # 加载技能配置
        skills_file = self.config_dir / "skills.yaml"
        if skills_file.exists():
            with open(skills_file, "r", encoding="utf-8") as f:
                self.skills_config = yaml.safe_load(f)
        else:
            self.skills_config = {}

    def _setup_logging(self):
        """设置日志"""
        # 移除默认处理器
        logger.remove()

        # 添加控制台输出
        logger.add(
            sink=lambda msg: print(msg, end=""),
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            level=self.logging.level,
            colorize=True,
        )

        # 添加文件输出
        log_file = Path(self.logging.file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            sink=str(log_file),
            rotation=self.logging.rotation,
            retention=self.logging.retention,
            level=self.logging.level,
            format=self.logging.format,
            encoding="utf-8",
        )

    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            Path("./data/sqlite"),
            Path("./data/chroma"),
            Path("./logs"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """获取 LLM 配置"""
        provider = provider or self.settings.llm_provider

        config = {
            "provider": provider,
            "api_key": None,
            "model": None,
            "base_url": None,
        }

        if provider == "claude":
            config["api_key"] = self.settings.anthropic_api_key
            config["model"] = self.settings.anthropic_model
        elif provider == "openai":
            config["api_key"] = self.settings.openai_api_key
            config["model"] = self.settings.openai_model
        elif provider == "deepseek":
            config["api_key"] = self.settings.deepseek_api_key
            config["model"] = self.settings.deepseek_model
            config["base_url"] = self.settings.deepseek_base_url
        elif provider == "kimi":
            config["api_key"] = self.settings.kimi_api_key
            config["model"] = self.settings.kimi_model
            config["base_url"] = self.settings.kimi_base_url
        elif provider == "minimax":
            config["api_key"] = self.settings.minimax_api_key
            config["model"] = self.settings.minimax_model
            config["group_id"] = self.settings.minimax_group_id

        # 合并 YAML 配置
        if provider in self.llm.models:
            model_config = self.llm.models[provider]
            config["max_tokens"] = model_config.max_tokens
            config["temperature"] = model_config.temperature

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self

        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def reload(self):
        """重新加载配置"""
        Config._initialized = False
        self.__init__()
        logger.info("配置已重新加载")

    @classmethod
    def load(cls) -> "Config":
        """加载配置（单例）"""
        return cls()


# 全局配置实例
config = Config.load()
