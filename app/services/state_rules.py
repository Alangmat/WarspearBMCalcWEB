from __future__ import annotations

from app.domain.models import DataSetBM


def normalize_dataset(dataset: DataSetBM) -> DataSetBM:
    """Apply UI/domain exclusivity rules before calculation or export."""
    data = dataset.model_copy(deep=True)

    active_branch = _active_branch(data)
    data.talents.guardian_unity_active = active_branch == "guardian"
    data.talents.dual_rage_active = active_branch == "dual"
    data.talents.forest_inspiration_active = active_branch == "forest"

    if active_branch != "guardian":
        data.skills.order_to_attack.talent_guardian_unity_level = 0
        data.skills.blessing_of_the_moon.talent_plus_penetration = False
        data.talents.harmonious_power = False

    if active_branch != "dual":
        data.skills.bestial_rampage.talent = False
        data.skills.beast_awakening.talent_physical_level = 0
        data.skills.double_concentration.talent_deadly_dexterity = False
        data.skills.order_to_attack.talent_dual_rage_level = 0
        data.skills.blessing_of_the_moon.talent_plus_critical_hit = False
        data.talents.symbiosis = False

    if active_branch != "forest":
        data.skills.moonlight.talent_level = 0
        data.skills.beast_awakening.talent_mage = False
        data.skills.aura_of_the_forest.talent_grandeur_of_lotus = False
        data.skills.aura_of_the_forest.talent_abuse = False

    if not data.skills.aura_of_the_forest.talent_grandeur_of_lotus:
        data.skills.aura_of_the_forest.talent_abuse = False

    if data.mods.roar_talent_almahad and data.mods.predatory_bond_talent_almahad:
        data.mods.predatory_bond_talent_almahad = False

    return data


def _active_branch(dataset: DataSetBM) -> str | None:
    talents = dataset.talents
    if talents.dual_rage_active:
        return "dual"
    if talents.forest_inspiration_active:
        return "forest"
    if talents.guardian_unity_active:
        return "guardian"
    return None
