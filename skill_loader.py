from __future__ import annotations

import json
from pathlib import Path

from config import SKILLS_DIR

REGISTRY_FILE = "registry.json"


def _load_registry() -> dict[str, list[str]]:
    path = Path(SKILLS_DIR) / REGISTRY_FILE
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("skills/registry.json must contain an object")
    return data


def get_agent_skill_files(agent_name: str) -> list[str]:
    files = _load_registry().get(agent_name, [])
    if not isinstance(files, list):
        raise ValueError(f"Registry entry {agent_name!r} must be a list")
    return [str(x) for x in files]


def get_agent_skill_names(agent_name: str) -> list[str]:
    return [Path(x).stem for x in get_agent_skill_files(agent_name)]


def render_agent_skills(agent_name: str) -> str:
    """Load all skills assigned to an agent at runtime.

    Agent code knows only its role name. Concrete skill filenames live only in registry.json.
    """
    blocks: list[str] = []
    for filename in get_agent_skill_files(agent_name):
        path = Path(SKILLS_DIR) / filename
        if not path.exists():
            raise FileNotFoundError(f"Skill not found: {path}")
        content = path.read_text(encoding="utf-8")
        blocks.append(f"--- SKILL: {path.stem} ---\n{content}")
    return "\n\n".join(blocks)
