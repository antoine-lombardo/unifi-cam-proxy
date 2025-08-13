from __future__ import annotations
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class CameraDriver(ABC):
    """Brand-agnostic camera API used by WssManager."""

    def __init__(self, settings: Dict[str, Any], log):
        self.settings = settings
        self.log = log

    # --- on-demand snapshot (used for GetRequest what="snapshot") ---
    @abstractmethod
    async def get_snapshot_jpeg(self, *, timeout_s: int = 5) -> bytes:
        ...

    # --- stat queries shown in your logs ---
    async def get_system_stats(self) -> Dict[str, Any]:
        # Optional override; provide sane defaults
        return {"cpu": 5, "memory": 20, "temperature": 45}

    # --- settings calls the controller may send; return what you applied/accepted ---
    async def apply_video_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"video": payload.get("video", {})}

    async def apply_isp_settings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Return fields the controller might read back (mountPosition, masks, etc.)
        return {}

    async def network_status(self) -> Dict[str, Any]:
        return {"status": "connected"}

    async def close(self) -> None:
        pass