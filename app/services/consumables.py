from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


ConsumableType = Literal["potion", "scroll", "pet"]

POWER_PERCENT_STATS = {"magical_power_percent", "physical_power_percent"}
POWER_FLAT_STATS = {"magical_power_flat", "physical_power_flat"}

STAT_LABELS: dict[str, str] = {
    "skill_cooldown": "Перезарядка навыков",
    "attack_speed": "Скорость атаки",
    "critical_hit": "Критический удар",
    "critical_damage": "Критический урон",
    "penetration": "Пробивная способность",
    "accuracy": "Точность",
    "attack_strength": "Сила атаки",
    "piercing_attack": "Пронзающая атака",
    "rage": "Ярость",
    "facilitation": "Содействие",
    "skill_power": "Сила навыков",
    "depths_fury": "Гнев глубин",
    "magical_power_percent": "Магическая сила %",
    "physical_power_percent": "Физическая сила %",
    "magical_power_flat": "Магическая сила",
    "physical_power_flat": "Физическая сила",
}

ALLOWED_STATS: dict[str, set[str]] = {
    "potion": {
        "skill_cooldown",
        "attack_speed",
        "critical_hit",
        "critical_damage",
        "penetration",
        "accuracy",
        "attack_strength",
        "piercing_attack",
        "rage",
        "facilitation",
        "skill_power",
        "magical_power_percent",
        "physical_power_percent",
    },
    "scroll": {
        "skill_cooldown",
        "attack_speed",
        "critical_hit",
        "critical_damage",
        "penetration",
        "accuracy",
        "attack_strength",
        "piercing_attack",
        "rage",
        "facilitation",
        "depths_fury",
        "magical_power_percent",
        "physical_power_percent",
        "magical_power_flat",
        "physical_power_flat",
    },
    "pet": {
        "skill_cooldown",
        "attack_speed",
        "critical_damage",
        "penetration",
        "accuracy",
        "attack_strength",
        "rage",
        "facilitation",
        "skill_power",
        "magical_power_percent",
        "physical_power_percent",
    },
}


class ConsumableEffect(BaseModel):
    stat: str
    value: float = 0
    passive: bool = False
    duration: float = 0
    cooldown: float = 0


class ConsumableItem(BaseModel):
    id: str
    type: ConsumableType
    name: str
    icon: str = ""
    passive: bool = False
    duration: float = 0
    cooldown: float = 0
    effects: list[ConsumableEffect] = Field(default_factory=list)


class ConsumableCatalog(BaseModel):
    version: int = 1
    items: list[ConsumableItem] = Field(default_factory=list)
    stat_labels: dict[str, str] = Field(default_factory=lambda: STAT_LABELS.copy())
    allowed_stats: dict[str, list[str]] = Field(
        default_factory=lambda: {key: sorted(value) for key, value in ALLOWED_STATS.items()}
    )


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "consumables.json"


def load_consumable_catalog(path: Path = CONFIG_PATH) -> ConsumableCatalog:
    if not path.exists():
        return ConsumableCatalog()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ConsumableCatalog()
    catalog = ConsumableCatalog.model_validate(raw)
    valid_items: list[ConsumableItem] = []
    for item in catalog.items:
        effects = [effect for effect in item.effects[:4] if effect.stat in ALLOWED_STATS[item.type]]
        if item.id and item.name and effects:
            valid_items.append(item.model_copy(update={"effects": effects}))
    return ConsumableCatalog(version=catalog.version, items=valid_items)


def get_selected_consumables(selection: object) -> list[ConsumableItem]:
    catalog = load_consumable_catalog()
    by_type_and_id = {(item.type, item.id): item for item in catalog.items}
    selected: list[ConsumableItem] = []
    for item_type in ("potion", "scroll", "pet"):
        item_id = str(getattr(selection, item_type, "") or "")
        item = by_type_and_id.get((item_type, item_id))
        if item:
            selected.append(item)
    return selected
