# dps_core/sim/battle_env.py

from __future__ import annotations
from typing import Callable
from dataclasses import dataclass

from ..engine.core.state import BattleState, get_next_actor
from ..engine.core.actions import Action
from ..engine.core.transition import step

PolicyFn = Callable[[BattleState, str], Action]


@dataclass
class BattleEnv:
    """
    High-level battle loop wrapper.
    Handles the simulation cycle:
    - pick next actor
    - query policy(action)
    - call step()
    - accumulate reward
    """
    state: BattleState
    policy: PolicyFn

    def run(self, max_steps: int = 1000):
        total_reward = 0.0
        for _ in range(max_steps):
            if self.state.is_battle_over():
                break

            actor = get_next_actor(self.state)
            if actor is None:
                break

            action = self.policy(self.state, actor.id)
            result = step(self.state, action)
            self.state = result.new_state
            total_reward += result.reward

            if result.done:
                break

        return self.state, total_reward
