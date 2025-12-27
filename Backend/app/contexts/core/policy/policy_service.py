# app/core/policy_service.py
import json
from pathlib import Path
from typing import List
from app.contexts.shared.enum.roles import StaffRole

class PolicyService:
    def __init__(self, config_path: str | None = None):
        path = config_path or "config/policies.json"
        self._policies = self._load_config(path)

    def _load_config(self, path: str) -> dict:
        file_path = Path(path)
        if not file_path.exists():
            return {}  # default to empty dict to avoid None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:

            return {}

    def get_default_permissions(self, role: StaffRole) -> List[str]:
        return self._policies.get("staff_roles", {}).get(role.value, [])