# dps_core/engine/core/state.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Literal
import copy

Side = Literal["ally", "enemy", "summon"]


@dataclass
class EntityStats:
    """
    Static and dynamic battle stats combined.
    Only the minimal fields are included for the MVP engine.
    """
    hp_max: float
    atk: float
    defense: float
    speed: float
    crit_rate: float
    crit_dmg: float
    energy_max: float

    # Dynamic values in battle
    hp: float
    energy: float = 0.0

    # Star Rail toughness (stagger bar). For dummy targets = 0.
    toughness: float = 0.0


@dataclass
class EntityStatus:
    """
    Minimal control/debuff markers.
    These will be expanded later (burn, bleed, dot stacks, etc.)
    """
    frozen: bool = False
    stunned: bool = False
    weakness_broken: bool = False


@dataclass
class EntityState:
    """
    Representation of a combat entity (ally, enemy, summon).
    Holds full real-time stats and status flags.
    """
    id: str
    name: str
    side: Side
    stats: EntityStats
    status: EntityStatus = field(default_factory=EntityStatus)

    # Simplified action-value (initiative). Lower = acts earlier.
    action_value: float = 0.0

    alive: bool = True

    def is_action_available(self) -> bool:
        """Returns True if the unit is alive and not hard-CC’d."""
        return self.alive and not (self.status.frozen or self.status.stunned)


@dataclass
class BattleState:
    """
    Snapshot of the entire battlefield at a given time point.
    """
    time: float
    entities: Dict[str, EntityState]

    # Star Rail shared Skill Points for the team
    skill_points: int
    max_skill_points: int = 5

    # Simple string log for debugging (will be replaced by structured events)
    log: List[str] = field(default_factory=list)

    # RNG seed (to ensure full reproducibility in simulations)
    rng_seed: Optional[int] = None

    def clone(self) -> "BattleState":
        """Deep-copy state to make step() functional and side-effect free."""
        return copy.deepcopy(self)

    def get_alive_entities(self, side: Optional[Side] = None) -> List[EntityState]:
        """Return all alive entities, optionally filtered by side."""
        ents = [e for e in self.entities.values() if e.alive]
        if side is not None:
            ents = [e for e in ents if e.side == side]
        return ents

    def is_battle_over(self) -> bool:
        """Win/loss check: battle ends if either side has no living units."""
        allies_alive = any(e.alive and e.side == "ally" for e in self.entities.values())
        enemies_alive = any(e.alive and e.side == "enemy" for e in self.entities.values())
        return (not allies_alive) or (not enemies_alive)


def get_next_actor(state: BattleState) -> Optional[EntityState]:
    """
    Minimal turn-order logic:
    - This simplified MVP always picks the unit with the highest Speed.
    - Later replace this with a CT-bar (Action Value) system.
    """
    alive = [e for e in state.entities.values() if e.alive]
    if not alive:
        return None

    alive.sort(key=lambda e: (-e.stats.speed, e.id))
    return alive[0]
