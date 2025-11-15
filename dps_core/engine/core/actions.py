# dps_core/engine/core/actions.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Literal

ActionType = Literal["use_skill", "do_nothing"]


@dataclass
class Action:
    """
    A generic action:
    - actor_id: who performs the action
    - skill_id: which skill (basic, skill, ult, follow-up, etc.)
    - target_ids: target list
    """
    actor_id: str
    type: ActionType
    skill_id: Optional[str] = None
    target_ids: Optional[List[str]] = None


@dataclass
class StepResult:
    """
    Standard return object for step():
    - new_state: the post-action BattleState
    - reward: typically damage; RL can redefine this
    - done: battle termination flag
    - info: misc debugging information
    """
    new_state: "BattleState"
    reward: float
    done: bool
    info: dict
