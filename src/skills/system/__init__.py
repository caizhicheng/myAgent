"""
系统技能模块
"""

from src.skills.system.execute_command import ExecuteCommandSkill
from src.skills.system.get_system_info import GetSystemInfoSkill
from src.skills.system.list_processes import ListProcessesSkill

__all__ = ["ExecuteCommandSkill", "GetSystemInfoSkill", "ListProcessesSkill"]
