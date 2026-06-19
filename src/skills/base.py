"""
技能基类
定义技能的基本接口和数据结构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SkillParameter:
    """技能参数"""

    def __init__(
        self,
        param_type: type,
        description: str,
        required: bool = True,
        default: Any = None,
        choices: Optional[List[Any]] = None,
    ):
        """
        初始化参数

        Args:
            param_type: 参数类型
            description: 参数描述
            required: 是否必需
            default: 默认值
            choices: 可选值列表
        """
        self.param_type = param_type
        self.description = description
        self.required = required
        self.default = default
        self.choices = choices

    def to_json_schema(self) -> Dict[str, Any]:
        """转换为 JSON Schema 格式"""
        schema = {
            "type": self._get_json_type(),
            "description": self.description,
        }

        if self.default is not None:
            schema["default"] = self.default

        if self.choices:
            schema["enum"] = self.choices

        return schema

    def _get_json_type(self) -> str:
        """获取 JSON 类型"""
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_mapping.get(self.param_type, "string")


class SkillStatus(Enum):
    """技能执行状态"""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SkillResult:
    """技能执行结果"""

    status: SkillStatus
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        """是否成功"""
        return self.status == SkillStatus.SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


class Skill(ABC):
    """技能基类"""

    # 技能元信息
    name: str = ""
    description: str = ""
    category: str = "general"
    tags: List[str] = []
    version: str = "1.0.0"
    author: str = ""

    # 参数定义
    parameters: Dict[str, SkillParameter] = {}

    def __init__(self):
        """初始化技能"""
        if not self.name:
            raise ValueError("技能名称不能为空")

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """
        执行技能

        Args:
            **kwargs: 技能参数

        Returns:
            执行结果
        """
        pass

    def validate_parameters(self, params: Dict[str, Any]) -> List[str]:
        """
        验证参数

        Args:
            params: 参数字典

        Returns:
            错误消息列表
        """
        errors = []

        # 检查必需参数
        for param_name, param_def in self.parameters.items():
            if param_def.required and param_name not in params:
                errors.append(f"缺少必需参数: {param_name}")

        # 检查参数类型
        for param_name, param_value in params.items():
            if param_name in self.parameters:
                param_def = self.parameters[param_name]
                if not isinstance(param_value, param_def.param_type):
                    # 尝试类型转换
                    try:
                        params[param_name] = param_def.param_type(param_value)
                    except (ValueError, TypeError):
                        errors.append(
                            f"参数 {param_name} 类型错误，期望 {param_def.param_type.__name__}"
                        )

                # 检查可选值
                if param_def.choices and param_value not in param_def.choices:
                    errors.append(
                        f"参数 {param_name} 的值 {param_value} 不在可选值列表中: {param_def.choices}"
                    )

        return errors

    def get_info(self) -> Dict[str, Any]:
        """
        获取技能信息

        Returns:
            技能信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "version": self.version,
            "author": self.author,
            "parameters": {
                name: param.to_json_schema() for name, param in self.parameters.items()
            },
        }

    def to_tool_schema(self) -> Dict[str, Any]:
        """
        转换为 LangChain Tool Schema

        Returns:
            Tool Schema 字典
        """
        properties = {}
        required = []

        for param_name, param_def in self.parameters.items():
            properties[param_name] = param_def.to_json_schema()
            if param_def.required:
                required.append(param_name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
