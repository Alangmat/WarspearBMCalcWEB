from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.domain.models import CastleSector, DamagePercent, DataSetBM, EquipmentMaterial, WeaponType
from app.services.state_rules import normalize_dataset


PERCENT_TO_OLD = {
    DamagePercent.none: 0,
    DamagePercent.magic5: 1,
    DamagePercent.magic6: 2,
    DamagePercent.magic7_5: 3,
    DamagePercent.magic9: 4,
    DamagePercent.magic10: 5,
    DamagePercent.magic12: 6,
    DamagePercent.magic15: 7,
    DamagePercent.physical3: 8,
    DamagePercent.physical4: 9,
    DamagePercent.physical5: 10,
    DamagePercent.physical6: 11,
    DamagePercent.physical7: 12,
    DamagePercent.physical8: 13,
}

PERCENT_FROM_OLD = {
    0: DamagePercent.none,
    1: DamagePercent.magic5,
    2: DamagePercent.magic6,
    3: DamagePercent.magic7_5,
    4: DamagePercent.magic9,
    5: DamagePercent.magic10,
    6: DamagePercent.magic12,
    7: DamagePercent.magic15,
    8: DamagePercent.physical3,
    9: DamagePercent.physical4,
    10: DamagePercent.physical5,
    11: DamagePercent.physical6,
    12: DamagePercent.physical7,
    13: DamagePercent.physical8,
}

OLD_PERCENT_NAMES = {
    "none": DamagePercent.none,
    "magic5percent": DamagePercent.magic5,
    "magic6percent": DamagePercent.magic6,
    "magic7_5percent": DamagePercent.magic7_5,
    "magic9percent": DamagePercent.magic9,
    "magic10percent": DamagePercent.magic10,
    "magic12percent": DamagePercent.magic12,
    "magic15percent": DamagePercent.magic15,
    "physical3percent": DamagePercent.physical3,
    "physical4percent": DamagePercent.physical4,
    "physical5percent": DamagePercent.physical5,
    "physical6percent": DamagePercent.physical6,
    "physical7percent": DamagePercent.physical7,
    "physical8percent": DamagePercent.physical8,
}

CASTLE_TO_OLD = {
    CastleSector.empty: 0,
    CastleSector.first: 2,
    CastleSector.second: 3,
    CastleSector.third: 4,
    CastleSector.fourth: 5,
    CastleSector.fifth: 6,
}

CASTLE_FROM_OLD = {
    0: CastleSector.empty,
    2: CastleSector.first,
    3: CastleSector.second,
    4: CastleSector.third,
    5: CastleSector.fourth,
    6: CastleSector.fifth,
}

OLD_CASTLE_NAMES = {
    "empty": CastleSector.empty,
    "first": CastleSector.first,
    "second": CastleSector.second,
    "third": CastleSector.third,
    "fourth": CastleSector.fourth,
    "fifth": CastleSector.fifth,
}

EQUIPMENT_TO_OLD = {
    EquipmentMaterial.none: 0,
    EquipmentMaterial.cloth: 1,
    EquipmentMaterial.leather: 2,
}

EQUIPMENT_FROM_OLD = {
    0: EquipmentMaterial.none,
    1: EquipmentMaterial.cloth,
    2: EquipmentMaterial.leather,
}

OLD_EQUIPMENT_NAMES = {
    "none": EquipmentMaterial.none,
    "cloth": EquipmentMaterial.cloth,
    "leather": EquipmentMaterial.leather,
}


def import_build(payload: Any) -> DataSetBM:
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    if not isinstance(payload, dict):
        raise ValueError("JSON должен быть объектом сборки")
    if "stats" in payload and "skills" in payload:
        return normalize_dataset(DataSetBM.model_validate(payload))
    return normalize_dataset(_from_legacy_build(payload))


def export_legacy_build(dataset: DataSetBM, result_dd: int = 0) -> dict[str, Any]:
    data = normalize_dataset(dataset)
    old: dict[str, Any] = {
        "Name": data.name,
        "Description": data.description,
        "ID": str(uuid4()),
        "LastDate": datetime.now().isoformat(timespec="seconds"),
        "ResultDD": result_dd,
        "Attack": {"IsStaff": data.weapon == WeaponType.staff},
        "MoonTouch": {
            "Level": data.skills.moon_touch.level,
            "HasTalantPlus": data.skills.moon_touch.talent_plus,
            "HasRelic": data.skills.moon_touch.relic,
        },
        "BeastAwakening": {
            "Level": data.skills.beast_awakening.level,
            "HasTalantMage": data.skills.beast_awakening.talent_mage,
            "LvlTalantPhys": data.skills.beast_awakening.talent_physical_level,
        },
        "OrderToAttack": {
            "Level": data.skills.order_to_attack.level,
            "LvlTalantDualRage": data.skills.order_to_attack.talent_dual_rage_level,
            "LvlTalantGuardianUnity": data.skills.order_to_attack.talent_guardian_unity_level,
        },
        "ChainLightning": {
            "Level": data.skills.chain_lightning.level,
            "HasRelic": data.skills.chain_lightning.relic,
        },
        "AuraOfTheForest": {
            "Level": data.skills.aura_of_the_forest.level,
            "HasTalantPowerOfNature": data.skills.aura_of_the_forest.talent_power_of_nature,
        },
        "BestialRampage": {
            "Level": data.skills.bestial_rampage.level,
            "HasTalant": data.skills.bestial_rampage.talent,
        },
        "Moonlight": {
            "Level": data.skills.moonlight.level,
            "LvlTalant": data.skills.moonlight.talent_level,
        },
        "BlessingOfTheMoon": {
            "Level": data.skills.blessing_of_the_moon.level,
            "HasTalantPlusCriticalHit": data.skills.blessing_of_the_moon.talent_plus_critical_hit,
            "HasTalantPlusPenetration": data.skills.blessing_of_the_moon.talent_plus_penetration,
        },
        "DoubleConcentration": {
            "Level": data.skills.double_concentration.level,
            "HasTalentDeadlyDexterity": data.skills.double_concentration.talent_deadly_dexterity,
        },
        "MagicalDamage": str(data.stats.main.magical_damage),
        "PhysicalDamage": str(data.stats.main.physical_damage),
        "SkillCooldown": data.stats.main.skill_cooldown,
        "AttackSpeed": data.stats.main.attack_speed,
        "CriticalHit": data.stats.main.critical_hit,
        "CriticalDamage": data.stats.main.critical_damage,
        "Penetration": data.stats.main.penetration,
        "Accuracy": data.stats.main.accuracy,
        "AttackStrength": data.stats.main.attack_strength,
        "PiercingAttack": data.stats.main.piercing_attack,
        "Rage": data.stats.main.rage,
        "Facilitation": data.stats.main.facilitation,
        "DepthsFury": data.stats.main.depths_fury,
        "Protection": data.stats.main.protection,
        "Dodge": data.stats.main.dodge,
        "Resilience": data.stats.main.resilience,
        "SkillPower": data.stats.main.skill_power,
        "SkillCooldownPot": data.stats.pot.skill_cooldown,
        "AttackSpeedPot": data.stats.pot.attack_speed,
        "CriticalHitPot": data.stats.pot.critical_hit,
        "CriticalDamagePot": data.stats.pot.critical_damage,
        "PenetrationPot": data.stats.pot.penetration,
        "AccuracyPot": data.stats.pot.accuracy,
        "AttackStrengthPot": data.stats.pot.attack_strength,
        "PiercingAttackPot": data.stats.pot.piercing_attack,
        "RagePot": data.stats.pot.rage,
        "FacilitationPot": data.stats.pot.facilitation,
        "SkillPowerPot": data.stats.pot.skill_power,
        "SkillCooldownScroll": data.stats.scroll.skill_cooldown,
        "AttackSpeedScroll": data.stats.scroll.attack_speed,
        "CriticalHitScroll": data.stats.scroll.critical_hit,
        "CriticalDamageScroll": data.stats.scroll.critical_damage,
        "PenetrationScroll": data.stats.scroll.penetration,
        "AccuracyScroll": data.stats.scroll.accuracy,
        "AttackStrengthScroll": data.stats.scroll.attack_strength,
        "PiercingAttackScroll": data.stats.scroll.piercing_attack,
        "RageScroll": data.stats.scroll.rage,
        "FacilitationScroll": data.stats.scroll.facilitation,
        "DepthsFuryScroll": data.stats.scroll.depths_fury,
        "SkillCooldownPet": data.stats.pet.skill_cooldown,
        "AttackSpeedPet": data.stats.pet.attack_speed,
        "CriticalDamagePet": data.stats.pet.critical_damage,
        "PenetrationPet": data.stats.pet.penetration,
        "AccuracyPet": data.stats.pet.accuracy,
        "AttackStrengthPet": data.stats.pet.attack_strength,
        "RagePet": data.stats.pet.rage,
        "FacilitationPet": data.stats.pet.facilitation,
        "CrushingWill": data.mods.crushing_will,
        "IrreversibleAnger": data.mods.irreversible_anger,
        "Counterstand": data.mods.counterstand,
        "GuildDamageStartModifierActive": data.start_power_mods.guild_damage,
        "CastleStartModifierActive": data.start_power_mods.castle_damage,
        "TalentDamageStartModifierActive": data.start_power_mods.talent_damage,
        "HarmoniousPowerStartModifierActive": data.start_power_mods.harmonious_power,
        "AdditionalPercentMDDStart": data.start_power_mods.additional_mdd,
        "AdditionalPercentPDDStart": data.start_power_mods.additional_pdd,
        "AdditionalPercentMDDFinal": data.final_power_mods.additional_mdd,
        "AdditionalPercentPDDFinal": data.final_power_mods.additional_pdd,
        "GuildDamageModifierActive": data.final_power_mods.guild_damage,
        "CastleSwordActive": data.final_power_mods.castle_damage,
        "TalentDamageModifierActive": data.final_power_mods.talent_damage,
        "SelectedCastle": CASTLE_TO_OLD[data.final_power_mods.castle_sector],
        "SelectedCastleStart": CASTLE_TO_OLD[data.start_power_mods.castle_sector],
        "BPDungeon": data.mods.bp_dungeon,
        "SacredShieldHeroActive": data.mods.sacred_shield_hero,
        "SacredShieldLunaActive": data.mods.sacred_shield_luna,
        "GodsAid": data.mods.gods_aid_hero,
        "GodsAidLuna": data.mods.gods_aid_luna,
        "PairingTalentAlmahadActive": data.mods.pairing_talent_almahad,
        "RoarTalentAlmahadActive": data.mods.roar_talent_almahad,
        "PredatoryBondTalentAlmahadActive": data.mods.predatory_bond_talent_almahad,
        "SelectedAmuletNew": PERCENT_TO_OLD[data.percents.amulet],
        "SelectedCloakNew": PERCENT_TO_OLD[data.percents.cloak],
        "SelectedRingLNew": PERCENT_TO_OLD[data.percents.ring_left],
        "SelectedRingRNew": PERCENT_TO_OLD[data.percents.ring_right],
        "SelectedBraceletLNew": PERCENT_TO_OLD[data.percents.bracelet_left],
        "SelectedBraceletRNew": PERCENT_TO_OLD[data.percents.bracelet_right],
        "SelectedSetNew": PERCENT_TO_OLD[data.percents.set_bonus],
        "SelectedHelmetNew": EQUIPMENT_TO_OLD[data.equipment.helmet],
        "SelectedBodyNew": EQUIPMENT_TO_OLD[data.equipment.body],
        "SelectedHandsNew": EQUIPMENT_TO_OLD[data.equipment.gloves],
        "SelectedBeltNew": EQUIPMENT_TO_OLD[data.equipment.belt],
        "SelectedFootsNew": EQUIPMENT_TO_OLD[data.equipment.boots],
        "ForestInspirationActive": data.talents.forest_inspiration_active,
        "DualRageActive": data.talents.dual_rage_active,
        "GuardianUnityActive": data.talents.guardian_unity_active,
        "HasTalantGrandeurOfTheLotus": data.skills.aura_of_the_forest.talent_grandeur_of_lotus,
        "HasTalantSymbiosis": data.talents.symbiosis,
        "HasTalentHarmoniousPower": data.talents.harmonious_power,
        "LvlTalantBestialRage": data.talents.bestial_rage_level,
        "LvlTalantPredatoryDelirium": data.talents.predatory_delirium_level,
        "LvlTalantAnimalRage": data.talents.animal_rage_level,
        "LvlTalantMomentOfPower": data.talents.moment_of_power_level,
        "LvlTalantLongDeath": data.talents.long_death_level,
        "LvlTalantContinuousFury": data.talents.continuous_fury_level,
        "DragonEyeLvl": data.mods.dragon_eye_level,
        "PriestActive": data.mods.priest_active,
        "DruidActive": data.mods.druid_active,
        "TemplActive": data.mods.templar_active,
        "BlagoTalent": data.mods.blago_talent,
        "AttackActive": data.skills.attack.active,
        "MoonTouchActive": data.skills.moon_touch.active,
        "BeastAwakeningActive": data.skills.beast_awakening.active,
        "OrderToAttackActive": data.skills.order_to_attack.active,
        "HealingActive": data.skills.healing.active,
        "ChainLightningActive": data.skills.chain_lightning.active,
        "BestialRampageActive": data.skills.bestial_rampage.active,
        "AuraOfTheForestActive": data.skills.aura_of_the_forest.active,
        "MoonlightPermanentActive": data.skills.moonlight.permanent_active,
        "MoonlightNonPermanentActive": data.skills.moonlight.non_permanent_active,
        "BlessingOfTheMoonActive": data.skills.blessing_of_the_moon.active,
        "IsUsingBlessingOfTheMoonOnLuna": data.skills.blessing_of_the_moon.use_on_luna,
        "DoubleConcentrationActive": data.skills.double_concentration.active,
        "StaffSelected": data.weapon == WeaponType.staff,
        "SpearSelected": data.weapon == WeaponType.spear,
        "MaceSelected": data.weapon == WeaponType.mace,
        "SwordSelected": data.weapon == WeaponType.sword,
        "AxeSelected": data.weapon == WeaponType.axe,
        "AuraTalentAbuse": data.skills.aura_of_the_forest.talent_abuse,
        "Consumables": data.consumables.model_dump(),
    }
    return old


def _from_legacy_build(old: dict[str, Any]) -> DataSetBM:
    data = DataSetBM(name=str(old.get("Name") or "Imported Build"), description=str(old.get("Description") or ""))

    data.stats.main.magical_damage = int(_number(old.get("MagicalDamage")))
    data.stats.main.physical_damage = int(_number(old.get("PhysicalDamage")))
    data.stats.main.skill_cooldown = _number(old.get("SkillCooldown"))
    data.stats.main.attack_speed = _number(old.get("AttackSpeed"))
    data.stats.main.critical_hit = _number(old.get("CriticalHit"))
    data.stats.main.critical_damage = _number(old.get("CriticalDamage"))
    data.stats.main.penetration = _number(old.get("Penetration"))
    data.stats.main.accuracy = _number(old.get("Accuracy"))
    data.stats.main.attack_strength = _number(old.get("AttackStrength"))
    data.stats.main.piercing_attack = _number(old.get("PiercingAttack"))
    data.stats.main.rage = _number(old.get("Rage"))
    data.stats.main.facilitation = _number(old.get("Facilitation"))
    data.stats.main.depths_fury = _number(old.get("DepthsFury"))
    data.stats.main.protection = _number(old.get("Protection"))
    data.stats.main.dodge = _number(old.get("Dodge"))
    data.stats.main.resilience = _number(old.get("Resilience"))
    data.stats.main.skill_power = _number(old.get("SkillPower"))

    for target, suffix in (
        (data.stats.pot, "Pot"),
        (data.stats.scroll, "Scroll"),
        (data.stats.pet, "Pet"),
    ):
        _set_if_present(target, "skill_cooldown", old, "SkillCooldown" + suffix)
        _set_if_present(target, "attack_speed", old, "AttackSpeed" + suffix)
        _set_if_present(target, "critical_hit", old, "CriticalHit" + suffix)
        _set_if_present(target, "critical_damage", old, "CriticalDamage" + suffix)
        _set_if_present(target, "penetration", old, "Penetration" + suffix)
        _set_if_present(target, "accuracy", old, "Accuracy" + suffix)
        _set_if_present(target, "attack_strength", old, "AttackStrength" + suffix)
        _set_if_present(target, "piercing_attack", old, "PiercingAttack" + suffix)
        _set_if_present(target, "rage", old, "Rage" + suffix)
        _set_if_present(target, "facilitation", old, "Facilitation" + suffix)
        _set_if_present(target, "skill_power", old, "SkillPower" + suffix)
        _set_if_present(target, "depths_fury", old, "DepthsFury" + suffix)

    moon_touch = _dict(old.get("MoonTouch"))
    beast = _dict(old.get("BeastAwakening"))
    order = _dict(old.get("OrderToAttack"))
    chain = _dict(old.get("ChainLightning"))
    aura = _dict(old.get("AuraOfTheForest"))
    bestial = _dict(old.get("BestialRampage"))
    moonlight = _dict(old.get("Moonlight"))
    blessing = _dict(old.get("BlessingOfTheMoon"))
    double = _dict(old.get("DoubleConcentration"))

    data.skills.moon_touch.level = _level(moon_touch.get("Level"), 1, 5)
    data.skills.moon_touch.talent_plus = _bool(moon_touch.get("HasTalantPlus"))
    data.skills.moon_touch.relic = _bool(moon_touch.get("HasRelic"))
    data.skills.beast_awakening.level = _level(beast.get("Level"), 1, 5)
    data.skills.beast_awakening.talent_mage = _bool(beast.get("HasTalantMage"))
    data.skills.beast_awakening.talent_physical_level = _level(beast.get("LvlTalantPhys"), 0, 3)
    data.skills.order_to_attack.level = _level(order.get("Level"), 1, 5)
    data.skills.order_to_attack.talent_dual_rage_level = _level(order.get("LvlTalantDualRage"), 0, 3)
    data.skills.order_to_attack.talent_guardian_unity_level = _level(order.get("LvlTalantGuardianUnity"), 0, 3)
    data.skills.chain_lightning.level = _level(chain.get("Level"), 1, 5)
    data.skills.chain_lightning.relic = _bool(chain.get("HasRelic"))
    data.skills.aura_of_the_forest.level = _level(aura.get("Level"), 1, 4)
    data.skills.aura_of_the_forest.talent_power_of_nature = _bool(aura.get("HasTalantPowerOfNature"))
    data.skills.bestial_rampage.level = _level(bestial.get("Level"), 1, 4)
    data.skills.bestial_rampage.talent = _bool(bestial.get("HasTalant"))
    data.skills.moonlight.level = _level(moonlight.get("Level"), 1, 4)
    data.skills.moonlight.talent_level = _level(moonlight.get("LvlTalant"), 0, 3)
    data.skills.blessing_of_the_moon.level = _level(blessing.get("Level"), 1, 4)
    data.skills.blessing_of_the_moon.talent_plus_critical_hit = _bool(blessing.get("HasTalantPlusCriticalHit"))
    data.skills.blessing_of_the_moon.talent_plus_penetration = _bool(blessing.get("HasTalantPlusPenetration"))
    data.skills.double_concentration.level = _level(double.get("Level"), 1, 4)
    data.skills.double_concentration.talent_deadly_dexterity = _bool(double.get("HasTalentDeadlyDexterity"))

    data.skills.attack.active = _bool(old.get("AttackActive"))
    data.skills.moon_touch.active = _bool(old.get("MoonTouchActive"))
    data.skills.beast_awakening.active = _bool(old.get("BeastAwakeningActive"))
    data.skills.order_to_attack.active = _bool(old.get("OrderToAttackActive"))
    data.skills.healing.active = _bool(old.get("HealingActive"))
    data.skills.chain_lightning.active = _bool(old.get("ChainLightningActive"))
    data.skills.bestial_rampage.active = _bool(old.get("BestialRampageActive"))
    data.skills.aura_of_the_forest.active = _bool(old.get("AuraOfTheForestActive"))
    data.skills.moonlight.permanent_active = _bool(old.get("MoonlightPermanentActive"))
    data.skills.moonlight.non_permanent_active = _bool(old.get("MoonlightNonPermanentActive"))
    data.skills.blessing_of_the_moon.active = _bool(old.get("BlessingOfTheMoonActive"))
    data.skills.blessing_of_the_moon.use_on_luna = _bool(old.get("IsUsingBlessingOfTheMoonOnLuna"))
    data.skills.double_concentration.active = _bool(old.get("DoubleConcentrationActive"))

    data.weapon = _weapon(old)
    data.start_power_mods.guild_damage = _bool(old.get("GuildDamageStartModifierActive"))
    data.start_power_mods.castle_damage = _bool(old.get("CastleStartModifierActive"))
    data.start_power_mods.talent_damage = _bool(old.get("TalentDamageStartModifierActive"))
    data.start_power_mods.harmonious_power = _bool(old.get("HarmoniousPowerStartModifierActive"))
    data.start_power_mods.additional_mdd = _number(old.get("AdditionalPercentMDDStart"))
    data.start_power_mods.additional_pdd = _number(old.get("AdditionalPercentPDDStart"))
    data.start_power_mods.castle_sector = _castle(old.get("SelectedCastleStart"))

    data.final_power_mods.guild_damage = _bool(old.get("GuildDamageModifierActive"))
    data.final_power_mods.castle_damage = _bool(old.get("CastleSwordActive"))
    data.final_power_mods.talent_damage = _bool(old.get("TalentDamageModifierActive"))
    data.final_power_mods.additional_mdd = _number(old.get("AdditionalPercentMDDFinal"))
    data.final_power_mods.additional_pdd = _number(old.get("AdditionalPercentPDDFinal"))
    data.final_power_mods.castle_sector = _castle(old.get("SelectedCastle"))

    data.mods.crushing_will = _bool(old.get("CrushingWill"))
    data.mods.irreversible_anger = _bool(old.get("IrreversibleAnger"))
    data.mods.counterstand = _bool(old.get("Counterstand"))
    data.mods.bp_dungeon = _bool(old.get("BPDungeon"))
    data.mods.sacred_shield_hero = _bool(old.get("SacredShieldHeroActive"))
    data.mods.sacred_shield_luna = _bool(old.get("SacredShieldLunaActive"))
    data.mods.gods_aid_hero = _bool(old.get("GodsAid"))
    data.mods.gods_aid_luna = _bool(old.get("GodsAidLuna"))
    data.mods.pairing_talent_almahad = _bool(old.get("PairingTalentAlmahadActive"))
    data.mods.roar_talent_almahad = _bool(old.get("RoarTalentAlmahadActive"))
    data.mods.predatory_bond_talent_almahad = _bool(old.get("PredatoryBondTalentAlmahadActive"))
    data.mods.priest_active = _bool(old.get("PriestActive"))
    data.mods.druid_active = _bool(old.get("DruidActive"))
    data.mods.templar_active = _bool(old.get("TemplActive"))
    data.mods.dragon_eye_level = _level(old.get("DragonEyeLvl"), 0, 4)
    data.mods.blago_talent = _bool(old.get("BlagoTalent"))

    data.percents.amulet = _percent(old.get("SelectedAmuletNew"))
    data.percents.cloak = _percent(old.get("SelectedCloakNew"))
    data.percents.ring_left = _percent(old.get("SelectedRingLNew"))
    data.percents.ring_right = _percent(old.get("SelectedRingRNew"))
    data.percents.bracelet_left = _percent(old.get("SelectedBraceletLNew"))
    data.percents.bracelet_right = _percent(old.get("SelectedBraceletRNew"))
    data.percents.set_bonus = _percent(old.get("SelectedSetNew"))
    data.equipment.helmet = _equipment(old.get("SelectedHelmetNew"))
    data.equipment.body = _equipment(old.get("SelectedBodyNew"))
    data.equipment.gloves = _equipment(old.get("SelectedHandsNew"))
    data.equipment.belt = _equipment(old.get("SelectedBeltNew"))
    data.equipment.boots = _equipment(old.get("SelectedFootsNew"))

    data.talents.forest_inspiration_active = _bool(old.get("ForestInspirationActive"))
    data.talents.dual_rage_active = _bool(old.get("DualRageActive"))
    data.talents.guardian_unity_active = _bool(old.get("GuardianUnityActive"))
    data.skills.aura_of_the_forest.talent_grandeur_of_lotus = _bool(old.get("HasTalantGrandeurOfTheLotus"))
    data.talents.symbiosis = _bool(old.get("HasTalantSymbiosis"))
    data.talents.harmonious_power = _bool(old.get("HasTalentHarmoniousPower"))
    data.talents.bestial_rage_level = _level(old.get("LvlTalantBestialRage"), 0, 3)
    data.talents.predatory_delirium_level = _level(old.get("LvlTalantPredatoryDelirium"), 0, 3)
    data.talents.animal_rage_level = _level(old.get("LvlTalantAnimalRage"), 0, 3)
    data.talents.moment_of_power_level = _level(old.get("LvlTalantMomentOfPower"), 0, 4)
    data.talents.long_death_level = _level(old.get("LvlTalantLongDeath"), 0, 4)
    data.talents.continuous_fury_level = _level(old.get("LvlTalantContinuousFury"), 0, 3)
    data.skills.aura_of_the_forest.talent_abuse = _bool(old.get("AuraTalentAbuse"))
    if isinstance(old.get("Consumables"), dict):
        consumables = old["Consumables"]
        data.consumables.potion = str(consumables.get("potion") or consumables.get("Potion") or "")
        data.consumables.scroll = str(consumables.get("scroll") or consumables.get("Scroll") or "")
        data.consumables.pet = str(consumables.get("pet") or consumables.get("Pet") or "")
    return data


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _number(value: Any) -> float:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("\xa0", "").replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "да"}
    return False


def _level(value: Any, minimum: int, maximum: int) -> int:
    return min(max(int(round(_number(value))), minimum), maximum)


def _set_if_present(target: Any, attr: str, source: dict[str, Any], key: str) -> None:
    if key in source and hasattr(target, attr):
        setattr(target, attr, _number(source.get(key)))


def _percent(value: Any) -> DamagePercent:
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in DamagePercent._value2member_map_:
            return DamagePercent(cleaned)
        if cleaned in OLD_PERCENT_NAMES:
            return OLD_PERCENT_NAMES[cleaned]
    return PERCENT_FROM_OLD.get(int(_number(value)), DamagePercent.none)


def _equipment(value: Any) -> EquipmentMaterial:
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in EquipmentMaterial._value2member_map_:
            return EquipmentMaterial(cleaned)
        if cleaned in OLD_EQUIPMENT_NAMES:
            return OLD_EQUIPMENT_NAMES[cleaned]
    return EQUIPMENT_FROM_OLD.get(int(_number(value)), EquipmentMaterial.none)


def _castle(value: Any) -> CastleSector:
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in CastleSector._value2member_map_:
            return CastleSector(cleaned)
        if cleaned in OLD_CASTLE_NAMES:
            return OLD_CASTLE_NAMES[cleaned]
    return CASTLE_FROM_OLD.get(int(_number(value)), CastleSector.empty)


def _weapon(old: dict[str, Any]) -> WeaponType:
    if _bool(old.get("StaffSelected")):
        return WeaponType.staff
    if _bool(old.get("SpearSelected")):
        return WeaponType.spear
    if _bool(old.get("SwordSelected")):
        return WeaponType.sword
    if _bool(old.get("AxeSelected")):
        return WeaponType.axe
    return WeaponType.mace
