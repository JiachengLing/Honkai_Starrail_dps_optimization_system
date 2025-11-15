# dps_core/engine/starrail/loader.py

from __future__ import annotations
from typing import Dict, Any
import json
from pathlib import Path

from dps_core.engine.core.state import BattleState, EntityState, EntityStats


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON file as dict."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_entity_from_char(char_data: Dict[str, Any], side: str) -> EntityState:
    """
    Convert a character JSON entry into an EntityState.
    Currently only reads base_stats; traces/LC buffs will be added later.
    """
    base = char_data["base_stats"]

    stats = EntityStats(
        hp_max=base["hp"],
        atk=base["atk"],
        defense=base["def"],
        speed=base.get("speed", 100),
        crit_rate=base.get("crit_rate", 0.05),
        crit_dmg=base.get("crit_dmg", 0.50),
        energy_max=base.get("energy_max", 100),
        hp=base["hp"],
        energy=0.0,
        toughness=0.0,
    )

    return EntityState(
        id=char_data["id"],
        name=char_data["name"],
        side=side,
        stats=stats,
    )


def build_simple_battle_state(
        characters_json: Path,
        allies_ids: Dict[str, str],
        enemy_config: Dict[str, Any],
) -> BattleState:
    """
    Build a minimal battle state:
    - allies loaded from characters.json
    - enemy built directly from the provided config
    """
    chars_raw = load_json(characters_json)
    entities: Dict[str, EntityState] = {}

    # Load allies
    for char_key, entity_id in allies_ids.items():
        char_data = chars_raw[char_key]
        ent = build_entity_from_char(char_data, side="ally")
        ent.id = entity_id
        entities[entity_id] = ent

    # Load a dummy enemy (not from JSON in MVP)
    enemy_stats = EntityStats(
        hp_max=enemy_config["hp_max"],
        atk=enemy_config["atk"],
        defense=enemy_config["defense"],
        speed=enemy_config.get("speed", 80),
        crit_rate=0.0,
        crit_dmg=0.5,
        energy_max=0.0,
        hp=enemy_config["hp_max"],
        energy=0.0,
        toughness=enemy_config.get("toughness", 0.0),
    )
    enemy = EntityState(
        id="dummy_enemy",
        name="Training Dummy",
        side="enemy",
        stats=enemy_stats,
    )
    entities[enemy.id] = enemy

    state = BattleState(
        time=0.0,
        entities=entities,
        skill_points=3,
        max_skill_points=5,
    )
    return state
