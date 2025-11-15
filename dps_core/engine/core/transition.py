# dps_core/engine/core/transition.py

from __future__ import annotations
from dps_core.engine.core.state import BattleState, EntityState
from dps_core.engine.core.actions import Action, StepResult


def apply_damage(attacker: EntityState, defender: EntityState, raw_multiplier: float) -> float:
    """
    Minimal placeholder damage formula for the MVP:
    Damage = ATK * multiplier

    This will later be replaced with:
    - DEF formula
    - RES / PEN
    - CRIT rolls
    - Vulnerability modifiers
    - Skill/LC/Trace/passive rules
    - Follow-up & DoT rules
    """
    if not defender.alive:
        return 0.0

    dmg = attacker.stats.atk * raw_multiplier

    defender.stats.hp -= dmg
    if defender.stats.hp <= 0:
        defender.stats.hp = 0
        defender.alive = False

    return dmg


def step(state: BattleState, action: Action) -> StepResult:
    """
    The central state-transition function.
    Performs:
    - validation
    - damage/heal/buff application
    - stat updates
    - time progression
    """
    s = state.clone()
    log_prefix = f"[t={s.time:.2f}] "

    actor = s.entities.get(action.actor_id)
    if actor is None or not actor.alive:
        s.log.append(log_prefix + f"Invalid actor: {action.actor_id}")
        return StepResult(new_state=s, reward=0.0, done=s.is_battle_over(), info={"error": "invalid_actor"})

    # MVP: only basic single-target attack with multiplier=1.0
    if action.type == "use_skill":
        if not action.target_ids:
            # Auto-target first alive enemy
            targets = [e for e in s.entities.values() if e.side != actor.side and e.alive]
            target = targets[0] if targets else None
        else:
            target = s.entities.get(action.target_ids[0])

        if target is None:
            s.log.append(log_prefix + f"{actor.name} has no valid target.")
            return StepResult(new_state=s, reward=0.0, done=s.is_battle_over(), info={"error": "no_target"})

        dmg = apply_damage(actor, target, raw_multiplier=1.0)
        s.log.append(log_prefix + f"{actor.name} used {action.skill_id}, dealt {dmg:.1f} to {target.name}.")

        reward = dmg

    else:
        s.log.append(log_prefix + f"{actor.name} did nothing.")
        reward = 0.0

    done = s.is_battle_over()
    info = {}

    # Minimal time progression
    s.time += 1.0

    return StepResult(new_state=s, reward=reward, done=done, info=info)
