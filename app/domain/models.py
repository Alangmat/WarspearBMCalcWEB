from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class DamagePercent(str, Enum):
    none = "none"
    magic5 = "magic5"
    magic6 = "magic6"
    magic7_5 = "magic7_5"
    magic9 = "magic9"
    magic10 = "magic10"
    magic12 = "magic12"
    magic15 = "magic15"
    physical3 = "physical3"
    physical4 = "physical4"
    physical5 = "physical5"
    physical6 = "physical6"
    physical7 = "physical7"
    physical8 = "physical8"


class EquipmentMaterial(str, Enum):
    none = "none"
    cloth = "cloth"
    leather = "leather"


class CastleSector(str, Enum):
    empty = "empty"
    first = "first"
    second = "second"
    third = "third"
    fourth = "fourth"
    fifth = "fifth"


class WeaponType(str, Enum):
    mace = "mace"
    staff = "staff"
    spear = "spear"
    sword = "sword"
    axe = "axe"


class DamageTotals(BaseModel):
    hero: int = 0
    luna: int = 0
    total: int = 0


class DamageLine(BaseModel):
    hit: int = 0
    dpm: int = 0


class SkillBreakdown(BaseModel):
    attack: DamageLine = Field(default_factory=DamageLine)
    moon_touch: DamageLine = Field(default_factory=DamageLine)
    chain_lightning: DamageLine = Field(default_factory=DamageLine)
    beast_awakening: DamageLine = Field(default_factory=DamageLine)
    bestial_rampage: DamageLine = Field(default_factory=DamageLine)
    order_to_attack: DamageLine = Field(default_factory=DamageLine)
    aura_luna: DamageLine = Field(default_factory=DamageLine)
    aura_hero: DamageLine = Field(default_factory=DamageLine)
    moonlight_permanent: DamageLine = Field(default_factory=DamageLine)
    moonlight_non_permanent: DamageLine = Field(default_factory=DamageLine)
    symbiosis_hero: int = 0
    symbiosis_luna: int = 0


class FinalStats(BaseModel):
    skill_cooldown: float = 0
    attack_speed: float = 0
    critical_hit_hero: float = 0
    critical_hit_luna: float = 0
    critical_damage_hero: float = 0
    critical_damage_luna: float = 0
    penetration_hero: float = 0
    penetration_luna: float = 0
    accuracy_hero: float = 0
    accuracy_luna: float = 0
    attack_strength_hero: float = 0
    attack_strength_luna: float = 0
    piercing_attack: float = 0
    rage: float = 0
    facilitation_hero: float = 0
    facilitation_luna: float = 0
    skill_power: float = 0
    depths_fury: float = 0
    effective_magical_damage: int = 0
    effective_physical_damage: int = 0
    pure_magical_damage: int = 0
    pure_physical_damage: int = 0


class CalculationResult(BaseModel):
    totals: DamageTotals
    skills: SkillBreakdown
    final_stats: FinalStats


class MainStats(BaseModel):
    magical_damage: int = 0
    physical_damage: int = 0
    skill_cooldown: float = 0
    attack_speed: float = 0
    critical_hit: float = 0
    critical_damage: float = 0
    penetration: float = 0
    accuracy: float = 0
    attack_strength: float = 0
    piercing_attack: float = 0
    rage: float = 0
    facilitation: float = 0
    depths_fury: float = 0
    protection: float = 0
    dodge: float = 0
    resilience: float = 0
    skill_power: float = 0


class PotStats(BaseModel):
    skill_cooldown: float = 0
    attack_speed: float = 0
    critical_hit: float = 0
    critical_damage: float = 0
    penetration: float = 0
    accuracy: float = 0
    attack_strength: float = 0
    piercing_attack: float = 0
    rage: float = 0
    facilitation: float = 0
    skill_power: float = 0


class ScrollStats(BaseModel):
    skill_cooldown: float = 0
    attack_speed: float = 0
    critical_hit: float = 0
    critical_damage: float = 0
    penetration: float = 0
    accuracy: float = 0
    attack_strength: float = 0
    piercing_attack: float = 0
    rage: float = 0
    facilitation: float = 0
    depths_fury: float = 0


class PetStats(BaseModel):
    skill_cooldown: float = 0
    attack_speed: float = 0
    critical_damage: float = 0
    penetration: float = 0
    accuracy: float = 0
    attack_strength: float = 0
    rage: float = 0
    facilitation: float = 0


class StatsSet(BaseModel):
    main: MainStats = Field(default_factory=MainStats)
    pot: PotStats = Field(default_factory=PotStats)
    scroll: ScrollStats = Field(default_factory=ScrollStats)
    pet: PetStats = Field(default_factory=PetStats)


class AttackSkill(BaseModel):
    active: bool = False


class LevelSkill(BaseModel):
    active: bool = False
    level: int = Field(default=1, ge=1, le=5)


class MoonTouchSkill(LevelSkill):
    talent_plus: bool = False
    relic: bool = False


class BeastAwakeningSkill(LevelSkill):
    talent_mage: bool = False
    talent_physical_level: int = Field(default=0, ge=0, le=3)


class OrderToAttackSkill(LevelSkill):
    talent_dual_rage_level: int = Field(default=0, ge=0, le=3)
    talent_guardian_unity_level: int = Field(default=0, ge=0, le=3)


class ChainLightningSkill(LevelSkill):
    relic: bool = False


class BestialRampageSkill(LevelSkill):
    level: int = Field(default=1, ge=1, le=4)
    talent: bool = False


class AuraOfTheForestSkill(LevelSkill):
    level: int = Field(default=1, ge=1, le=4)
    talent_power_of_nature: bool = False
    talent_grandeur_of_lotus: bool = False
    talent_abuse: bool = False


class MoonlightSkill(BaseModel):
    permanent_active: bool = False
    non_permanent_active: bool = False
    level: int = Field(default=1, ge=1, le=4)
    talent_level: int = Field(default=0, ge=0, le=3)


class BlessingOfTheMoonSkill(LevelSkill):
    level: int = Field(default=1, ge=1, le=4)
    use_on_luna: bool = False
    talent_plus_critical_hit: bool = False
    talent_plus_penetration: bool = False


class DoubleConcentrationSkill(LevelSkill):
    level: int = Field(default=1, ge=1, le=4)
    talent_deadly_dexterity: bool = False


class HealingSkill(BaseModel):
    active: bool = False


class SkillsSet(BaseModel):
    attack: AttackSkill = Field(default_factory=AttackSkill)
    moon_touch: MoonTouchSkill = Field(default_factory=MoonTouchSkill)
    beast_awakening: BeastAwakeningSkill = Field(default_factory=BeastAwakeningSkill)
    order_to_attack: OrderToAttackSkill = Field(default_factory=OrderToAttackSkill)
    chain_lightning: ChainLightningSkill = Field(default_factory=ChainLightningSkill)
    bestial_rampage: BestialRampageSkill = Field(default_factory=BestialRampageSkill)
    aura_of_the_forest: AuraOfTheForestSkill = Field(default_factory=AuraOfTheForestSkill)
    moonlight: MoonlightSkill = Field(default_factory=MoonlightSkill)
    blessing_of_the_moon: BlessingOfTheMoonSkill = Field(default_factory=BlessingOfTheMoonSkill)
    double_concentration: DoubleConcentrationSkill = Field(default_factory=DoubleConcentrationSkill)
    healing: HealingSkill = Field(default_factory=HealingSkill)


class GeneralPowerMods(BaseModel):
    guild_damage: bool = False
    talent_damage: bool = False
    castle_damage: bool = False
    harmonious_power: bool = False
    additional_mdd: float = 0
    additional_pdd: float = 0
    castle_sector: CastleSector = CastleSector.empty


class GlobalMods(BaseModel):
    crushing_will: bool = False
    irreversible_anger: bool = False
    bp_dungeon: bool = False
    sacred_shield_hero: bool = False
    sacred_shield_luna: bool = False
    gods_aid_hero: bool = False
    gods_aid_luna: bool = False
    counterstand: bool = False
    pairing_talent_almahad: bool = False
    roar_talent_almahad: bool = False
    predatory_bond_talent_almahad: bool = False
    priest_active: bool = False
    druid_active: bool = False
    templar_active: bool = False
    dragon_eye_level: int = Field(default=0, ge=0, le=4)
    blago_talent: bool = False


class TalentSet(BaseModel):
    forest_inspiration_active: bool = False
    dual_rage_active: bool = False
    guardian_unity_active: bool = False
    harmonious_power: bool = False
    symbiosis: bool = False
    bestial_rage_level: int = Field(default=0, ge=0, le=3)
    predatory_delirium_level: int = Field(default=0, ge=0, le=3)
    animal_rage_level: int = Field(default=0, ge=0, le=3)
    moment_of_power_level: int = Field(default=0, ge=0, le=4)
    long_death_level: int = Field(default=0, ge=0, le=4)
    continuous_fury_level: int = Field(default=0, ge=0, le=3)


class JewelryPercents(BaseModel):
    amulet: DamagePercent = DamagePercent.none
    cloak: DamagePercent = DamagePercent.none
    ring_left: DamagePercent = DamagePercent.none
    ring_right: DamagePercent = DamagePercent.none
    bracelet_left: DamagePercent = DamagePercent.none
    bracelet_right: DamagePercent = DamagePercent.none
    set_bonus: DamagePercent = DamagePercent.none


class EquipmentPercents(BaseModel):
    helmet: EquipmentMaterial = EquipmentMaterial.none
    body: EquipmentMaterial = EquipmentMaterial.none
    gloves: EquipmentMaterial = EquipmentMaterial.none
    belt: EquipmentMaterial = EquipmentMaterial.none
    boots: EquipmentMaterial = EquipmentMaterial.none


class ConsumableSelection(BaseModel):
    potion: str = ""
    scroll: str = ""
    pet: str = ""


class DataSetBM(BaseModel):
    name: str = "New Data Set"
    description: str = ""
    weapon: WeaponType = WeaponType.mace
    stats: StatsSet = Field(default_factory=StatsSet)
    skills: SkillsSet = Field(default_factory=SkillsSet)
    start_power_mods: GeneralPowerMods = Field(default_factory=GeneralPowerMods)
    final_power_mods: GeneralPowerMods = Field(default_factory=GeneralPowerMods)
    mods: GlobalMods = Field(default_factory=GlobalMods)
    talents: TalentSet = Field(default_factory=TalentSet)
    percents: JewelryPercents = Field(default_factory=JewelryPercents)
    equipment: EquipmentPercents = Field(default_factory=EquipmentPercents)
    consumables: ConsumableSelection = Field(default_factory=ConsumableSelection)


class PresetRequest(BaseModel):
    preset: Literal["empty", "default"] = "default"
