"""
获取系统信息技能
"""

import platform
import psutil
from datetime import datetime
from typing import Dict, Any

from loguru import logger

from src.skills.base import Skill, SkillParameter, SkillResult, SkillStatus


class GetSystemInfoSkill(Skill):
    """获取系统信息技能"""

    name = "get_system_info"
    description = "获取系统信息（CPU、内存、磁盘、网络等）"
    category = "system"
    tags = ["system", "info", "monitor"]

    parameters = {
        "detail": SkillParameter(
            bool, "是否显示详细信息", required=False, default=False
        ),
    }

    async def execute(self, detail: bool = False) -> SkillResult:
        """
        获取系统信息

        Args:
            detail: 是否显示详细信息

        Returns:
            执行结果
        """
        try:
            info = {
                "system": self._get_system_info(),
                "cpu": self._get_cpu_info(detail),
                "memory": self._get_memory_info(detail),
                "disk": self._get_disk_info(detail),
                "network": self._get_network_info(detail),
            }

            if detail:
                info["processes"] = self._get_process_info()

            logger.info("成功获取系统信息")

            return SkillResult(
                status=SkillStatus.SUCCESS,
                output=info,
                metadata={
                    "detail": detail,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return SkillResult(
                status=SkillStatus.FAILED,
                output=None,
                error=f"获取系统信息失败: {str(e)}",
            )

    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

    def _get_cpu_info(self, detail: bool = False) -> Dict[str, Any]:
        """获取 CPU 信息"""
        info = {
            "count": psutil.cpu_count(),
            "percent": psutil.cpu_percent(interval=1),
        }

        if detail:
            info["percent_per_cpu"] = psutil.cpu_percent(interval=1, percpu=True)
            info["freq"] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            info["stats"] = psutil.cpu_stats()._asdict()

        return info

    def _get_memory_info(self, detail: bool = False) -> Dict[str, Any]:
        """获取内存信息"""
        mem = psutil.virtual_memory()

        info = {
            "total": self._bytes_to_gb(mem.total),
            "available": self._bytes_to_gb(mem.available),
            "used": self._bytes_to_gb(mem.used),
            "percent": mem.percent,
        }

        if detail:
            info["swap"] = psutil.swap_memory()._asdict()

        return info

    def _get_disk_info(self, detail: bool = False) -> Dict[str, Any]:
        """获取磁盘信息"""
        disks = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                disk_info = {
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": self._bytes_to_gb(usage.total),
                    "used": self._bytes_to_gb(usage.used),
                    "free": self._bytes_to_gb(usage.free),
                    "percent": usage.percent,
                }

                disks.append(disk_info)

            except PermissionError:
                # 跳过无权限访问的分区
                continue

        return {"partitions": disks}

    def _get_network_info(self, detail: bool = False) -> Dict[str, Any]:
        """获取网络信息"""
        net_io = psutil.net_io_counters()

        info = {
            "bytes_sent": self._bytes_to_mb(net_io.bytes_sent),
            "bytes_recv": self._bytes_to_mb(net_io.bytes_recv),
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }

        if detail:
            info["interfaces"] = {}
            for name, addrs in psutil.net_if_addrs().items():
                info["interfaces"][name] = [
                    {
                        "family": addr.family.name,
                        "address": addr.address,
                    }
                    for addr in addrs
                ]

        return info

    def _get_process_info(self) -> Dict[str, Any]:
        """获取进程信息"""
        processes = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                processes.append(
                    {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu_percent": proc.info["cpu_percent"],
                        "memory_percent": proc.info["memory_percent"],
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 按内存使用排序
        processes.sort(key=lambda x: x["memory_percent"], reverse=True)

        # 只返回前 10 个进程
        return {"top_processes": processes[:10]}

    def _bytes_to_gb(self, bytes: int) -> float:
        """字节转 GB"""
        return round(bytes / (1024**3), 2)

    def _bytes_to_mb(self, bytes: int) -> float:
        """字节转 MB"""
        return round(bytes / (1024**2), 2)
