from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.domain.models import (
    CalculationResult,
    CastleSector,
    DamageLine,
    DamagePercent,
    DamageTotals,
    DataSetBM,
    EquipmentMaterial,
    FinalStats,
    SkillBreakdown,
    WeaponType,
)
from app.services.consumables import get_selected_consumables


CONFIG_DIR = Path(__file__).resolve().parents[1] / "config" / "skills"
TIME_CAST = 0.65


class StatsLimit:
    MIN_VALUE = 0
    MAX_SKILL_COOLDOWN = 200
    MAX_ATTACK_SPEED = 70
    MAX_CRITICAL_HIT = 100
    MAX_CRITICAL_HIT_HERO = 53
    MAX_CRITICAL_DAMAGE = 200
    MAX_PENETRATION = 100
    MAX_PENETRATION_HERO = 50
    MAX_ACCURACY_HERO = 50
    MAX_ACCURACY = 100
    MAX_ATTACK_STRENGTH = 100
    MAX_PIERCING_ATTACK = 50
    MAX_RAGE = 50
    MAX_FACILITATION = 50
    MAX_PROTECTION = 80
    MAX_DODGE = 60
    MAX_RESILIENCE = 60
    MAX_DEPTH_FURY = 50
    MAX_SKILL_POWER = 100


def clamp(value: float, maximum: float) -> float:
    return min(max(value, StatsLimit.MIN_VALUE), maximum)


def coeff(percent: float) -> float:
    return 1 + percent / 100


def cint(value: float) -> int:
    return int(value)


def cround(value: float) -> int:
    return int(round(value))


def level_row(config: dict[str, Any], level: int) -> dict[str, Any]:
    levels = config.get("Levels") or []
    for row in levels:
        if int(row.get("Level", 0)) == int(level):
            return row
    return levels[0] if levels else {}


def max_level_row(rows: list[dict[str, Any]], level: int) -> dict[str, Any] | None:
    if not rows:
        return None
    for row in rows:
        if int(row.get("Level", 0)) == int(level):
            return row
    return sorted(rows, key=lambda item: int(item.get("Level", 0)))[-1]


class SkillConfigs:
    def __init__(self, root: Path = CONFIG_DIR) -> None:
        self.root = root
        self.moon_touch = self._load("moon_touch.json")
        self.beast_awakening = self._load("beast_awakening.json")
        self.order_to_attack = self._load("order_to_attack.json")
        self.chain_lightning = self._load("chain_lightning.json")
        self.aura = self._load("aura_of_the_forest.json")
        self.bestial_rampage = self._load("bestial_rampage.json")
        self.moonlight = self._load("moonlight.json")
        self.blessing = self._load("blessing_of_the_moon.json")
        self.double_concentration = self._load("double_concentration.json")

    def _load(self, filename: str) -> dict[str, Any]:
        with (self.root / filename).open("r", encoding="utf-8-sig") as file:
            return json.load(file)


def damage_percent(value: DamagePercent, damage_type: str) -> float:
    mapping: dict[DamagePercent, tuple[float, float]] = {
        DamagePercent.none: (0, 0),
        DamagePercent.magic5: (5, 0),
        DamagePercent.magic6: (6, 0),
        DamagePercent.magic7_5: (7.5, 0),
        DamagePercent.magic9: (9, 0),
        DamagePercent.magic10: (10, 0),
        DamagePercent.magic12: (12, 0),
        DamagePercent.magic15: (15, 0),
        DamagePercent.physical3: (0, 3),
        DamagePercent.physical4: (0, 4),
        DamagePercent.physical5: (0, 5),
        DamagePercent.physical6: (0, 6),
        DamagePercent.physical7: (0, 7),
        DamagePercent.physical8: (0, 8),
    }
    magical, physical = mapping[value]
    return magical if damage_type == "magical" else physical


def equipment_percent(value: EquipmentMaterial, damage_type: str) -> float:
    if value == EquipmentMaterial.cloth:
        magical, physical = 3, 2
    elif value == EquipmentMaterial.leather:
        magical, physical = 2, 3
    else:
        magical, physical = 0, 0
    return magical if damage_type == "magical" else physical


def castle_enum_value(value: CastleSector) -> int:
    return {
        CastleSector.empty: 0,
        CastleSector.first: 2,
        CastleSector.second: 3,
        CastleSector.third: 4,
        CastleSector.fourth: 5,
        CastleSector.fifth: 6,
    }[value]


def castle_coefficient(value: CastleSector) -> float:
    return coeff(2.5 * castle_enum_value(value))


def weapon_settings(value: WeaponType) -> tuple[bool, float]:
    if value == WeaponType.staff:
        return True, 3.1
    if value == WeaponType.spear:
        return False, 3.4
    return False, 3.2


@dataclass
class SkillRuntime:
    blessing_crit: int = 0
    blessing_penetration: int = 0
    double_crit_damage: float = 0
    double_skill_cooldown: float = 0
    double_attack_speed: float = 0
    bestial_time_active: int = 0
    bestial_damage_multiplier: float = 1
    bestial_attack_speed: float = 0


@dataclass
class CalcState:
    dataset: DataSetBM
    configs: SkillConfigs
    breakdown: SkillBreakdown
    skill: SkillRuntime
    staff: bool
    attack_delay_base: float
    coefficient_triton: float = 0
    max_penetration_hero: float = StatsLimit.MAX_PENETRATION_HERO
    skill_cooldown_final: float = 0
    attack_speed_final: float = 0
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
    piercing_attack_final: float = 0
    rage_final: float = 0
    facilitation_final: float = 0
    facilitation_luna: float = 0
    skill_power_final: float = 0
    depths_fury_final: float = 0
    harmonious_mdd: float = 0
    harmonious_pdd: float = 0
    percent_mdd_start: float = 0
    percent_pdd_start: float = 0
    percent_mdd_final: float = 0
    percent_pdd_final: float = 0
    bestial_rage_coef: float = 1
    predatory_delirium_coef: float = 1
    moment_of_power_coef: float = 1
    long_death_coef: float = 1
    animal_rage_add: float = 0
    continuous_fury_add: float = 0
    consumable_stats: dict[str, float] = field(default_factory=dict)
    consumable_mdd_percent: float = 0
    consumable_pdd_percent: float = 0
    consumable_mdd_flat: float = 0
    consumable_pdd_flat: float = 0


class BeastMasterCalculator:
    def __init__(self, configs: SkillConfigs | None = None) -> None:
        self.configs = configs or SkillConfigs()

    def calculate(self, dataset: DataSetBM) -> CalculationResult:
        staff, attack_delay_base = weapon_settings(dataset.weapon)
        state = CalcState(
            dataset=dataset,
            configs=self.configs,
            breakdown=SkillBreakdown(),
            skill=self._build_skill_runtime(dataset),
            staff=staff,
            attack_delay_base=attack_delay_base,
            coefficient_triton=0.3 if dataset.mods.crushing_will else 0,
            max_penetration_hero=51.5 if dataset.talents.dual_rage_active else 50,
        )

        self._apply_talent_coefficients(state)
        self._apply_consumables(state, include_timed_pet=False)
        self._calc_stats(state)
        self._apply_consumables(state, include_timed_pet=True)
        self._calc_stats(state)
        self._calc_percents(state)

        magicdd = int(dataset.stats.main.magical_damage)
        physdd = int(dataset.stats.main.physical_damage)

        coef_rage = self._coef_rage(state)
        pure_magic = cint(magicdd / coeff(state.percent_mdd_start))
        pure_phys = cint(physdd / coeff(state.percent_pdd_start))

        if dataset.start_power_mods.harmonious_power:
            pure_magic = cint(pure_magic / coeff(state.harmonious_mdd))
            pure_phys = cint(pure_phys / coeff(state.harmonious_pdd))

        pure_magic = cint(pure_magic + state.consumable_mdd_flat)
        pure_phys = cint(pure_phys + state.consumable_pdd_flat)

        magicdd = cint(
            pure_magic * (state.coefficient_triton * self._merman_duration(state) + coef_rage)
            + pure_magic * coeff(state.percent_mdd_final)
        )
        physdd = cint(pure_phys * coef_rage + pure_phys * coeff(state.percent_pdd_final))

        if dataset.talents.harmonious_power:
            magicdd = cint(magicdd * coeff(state.harmonious_mdd))
            physdd = cint(physdd * coeff(state.harmonious_pdd))

        dpm_attack = self._calc_attack(state, magicdd, physdd)
        dpm_moon_touch = self._calc_moon_touch(state, magicdd)
        dpm_beast = self._calc_beast_awakening(state, magicdd, physdd)
        dpm_order = self._calc_order_to_attack(state, magicdd, physdd)
        dpm_chain = self._calc_chain_lightning(state, magicdd, physdd)
        dpm_bestial = self._calc_bestial_rampage(state, magicdd, physdd)
        aura_luna, aura_hero = self._calc_aura(state, magicdd)
        dpm_moonlight = self._calc_moonlight(state, magicdd, pure_magic)
        sym_luna, sym_hero = self._calc_symbiosis(state, magicdd, physdd)

        hero = 0
        luna = 0
        skills = dataset.skills

        if skills.attack.active:
            hero += dpm_attack
        else:
            state.breakdown.attack = DamageLine()

        if skills.moon_touch.active:
            hero += dpm_moon_touch
        else:
            state.breakdown.moon_touch = DamageLine()

        if skills.beast_awakening.active:
            if skills.bestial_rampage.active:
                luna += cint(dpm_beast * self._time_without_bestial_rampage(state) + dpm_bestial * self._time_bestial_rampage(state))
                state.breakdown.bestial_rampage.dpm = cint(dpm_bestial * self._time_bestial_rampage(state))
                state.breakdown.beast_awakening.dpm = cint(dpm_beast * self._time_without_bestial_rampage(state))
            else:
                luna += dpm_beast
                state.breakdown.beast_awakening.dpm = dpm_beast
                state.breakdown.bestial_rampage = DamageLine()

            if skills.order_to_attack.active:
                luna += dpm_order
            else:
                state.breakdown.order_to_attack = DamageLine()

            if dataset.talents.symbiosis:
                hero += sym_hero
                luna += sym_luna
                state.breakdown.symbiosis_hero = sym_hero
                state.breakdown.symbiosis_luna = sym_luna
            else:
                state.breakdown.symbiosis_hero = 0
                state.breakdown.symbiosis_luna = 0
        else:
            state.breakdown.beast_awakening = DamageLine()
            state.breakdown.bestial_rampage = DamageLine()
            state.breakdown.order_to_attack = DamageLine()
            state.breakdown.symbiosis_hero = 0
            state.breakdown.symbiosis_luna = 0

        if skills.chain_lightning.active:
            hero += dpm_chain
        else:
            state.breakdown.chain_lightning = DamageLine()

        if skills.aura_of_the_forest.active:
            luna += aura_luna
            hero += aura_hero
        else:
            state.breakdown.aura_luna = DamageLine()
            state.breakdown.aura_hero = DamageLine()

        hero += dpm_moonlight

        total = hero + luna
        final_stats = FinalStats(
            skill_cooldown=state.skill_cooldown_final,
            attack_speed=state.attack_speed_final,
            critical_hit_hero=state.critical_hit_hero,
            critical_hit_luna=state.critical_hit_luna,
            critical_damage_hero=state.critical_damage_hero,
            critical_damage_luna=state.critical_damage_luna,
            penetration_hero=state.penetration_hero,
            penetration_luna=state.penetration_luna,
            accuracy_hero=state.accuracy_hero,
            accuracy_luna=state.accuracy_luna,
            attack_strength_hero=state.attack_strength_hero,
            attack_strength_luna=state.attack_strength_luna,
            piercing_attack=state.piercing_attack_final,
            rage=state.rage_final,
            facilitation_hero=state.facilitation_final,
            facilitation_luna=state.facilitation_luna,
            skill_power=state.skill_power_final,
            depths_fury=state.depths_fury_final,
            effective_magical_damage=magicdd,
            effective_physical_damage=physdd,
            pure_magical_damage=pure_magic,
            pure_physical_damage=pure_phys,
        )

        return CalculationResult(
            totals=DamageTotals(hero=hero, luna=luna, total=total),
            skills=state.breakdown,
            final_stats=final_stats,
        )

    def _build_skill_runtime(self, dataset: DataSetBM) -> SkillRuntime:
        blessing = level_row(self.configs.blessing, dataset.skills.blessing_of_the_moon.level)
        blessing_crit = int(blessing.get("AdditionCriticalHit", 8))
        blessing_pen = int(blessing.get("AdditionPenetration", 5))
        blessing_talents = self.configs.blessing.get("Talents", {})
        if dataset.skills.blessing_of_the_moon.talent_plus_penetration:
            blessing_pen += int(blessing_talents.get("PlusPenetration", 1))
        elif dataset.skills.blessing_of_the_moon.talent_plus_critical_hit:
            blessing_crit += int(blessing_talents.get("PlusCriticalHit", 2))

        double_row = level_row(self.configs.double_concentration, dataset.skills.double_concentration.level)
        double_cd = float(double_row.get("AdditionSkillCooldown", 16))
        raw_factor = float(self.configs.double_concentration.get("TalentDeadlyDexterityAttackSpeedFactor", 60))
        dexterity_factor = (100 - raw_factor) / 100
        has_dexterity = dataset.skills.double_concentration.talent_deadly_dexterity

        bestial_row = level_row(self.configs.bestial_rampage, dataset.skills.bestial_rampage.level)
        bestial_attack_speed = float(bestial_row.get("AttackSpeedPercents", 10))
        if dataset.skills.bestial_rampage.talent:
            bestial_attack_speed += float(self.configs.bestial_rampage.get("TalentAttackSpeedPercents", 2))

        return SkillRuntime(
            blessing_crit=blessing_crit,
            blessing_penetration=blessing_pen,
            double_crit_damage=float(double_row.get("AdditionCriticalDamage", 8)),
            double_skill_cooldown=0 if has_dexterity else double_cd,
            double_attack_speed=double_cd * dexterity_factor if has_dexterity else 0,
            bestial_time_active=int(bestial_row.get("TimeActive", 8)),
            bestial_damage_multiplier=float(bestial_row.get("DamagePercents", 110)) / 100,
            bestial_attack_speed=bestial_attack_speed,
        )

    def _apply_talent_coefficients(self, state: CalcState) -> None:
        talents = state.dataset.talents
        state.bestial_rage_coef = {0: 1, 1: 1.01, 2: 1.02, 3: 1.03}.get(talents.bestial_rage_level, 1)
        state.predatory_delirium_coef = {0: 1, 1: 1.01, 2: 1.015, 3: 1.02}.get(talents.predatory_delirium_level, 1)
        state.animal_rage_add = {0: 0, 1: 1, 2: 2, 3: 3}.get(talents.animal_rage_level, 0)
        state.moment_of_power_coef = {0: 1, 1: 1.005, 2: 1.01, 3: 1.015, 4: 1.02}.get(
            talents.moment_of_power_level, 1
        )
        state.long_death_coef = {0: 1, 1: 1.005, 2: 1.01, 3: 1.015, 4: 1.02}.get(talents.long_death_level, 1)
        state.continuous_fury_add = {0: 0, 1: 0.5, 2: 1, 3: 1.5}.get(talents.continuous_fury_level, 0)

    def _apply_consumables(self, state: CalcState, *, include_timed_pet: bool) -> None:
        state.consumable_stats = {}
        state.consumable_mdd_percent = 0
        state.consumable_pdd_percent = 0
        state.consumable_mdd_flat = 0
        state.consumable_pdd_flat = 0

        for item in get_selected_consumables(state.dataset.consumables):
            for effect in item.effects:
                multiplier = 1.0
                if item.type == "pet":
                    passive = effect.passive or item.passive
                    if passive:
                        multiplier = 1.0
                    elif include_timed_pet:
                        duration = effect.duration or item.duration
                        cooldown = effect.cooldown or item.cooldown
                        multiplier = self._pet_effect_uptime(state, duration, cooldown)
                    else:
                        multiplier = 0.0

                value = self._scaled_consumable_value(effect.value, multiplier)
                if effect.stat == "magical_power_percent":
                    state.consumable_mdd_percent += value
                elif effect.stat == "physical_power_percent":
                    state.consumable_pdd_percent += value
                elif effect.stat == "magical_power_flat":
                    state.consumable_mdd_flat += value
                elif effect.stat == "physical_power_flat":
                    state.consumable_pdd_flat += value
                else:
                    state.consumable_stats[effect.stat] = state.consumable_stats.get(effect.stat, 0) + value

    def _pet_effect_uptime(self, state: CalcState, duration: float, cooldown: float) -> float:
        if duration <= 0 or cooldown <= 0:
            return 0
        return min(max(duration * coeff(state.facilitation_final) / cooldown, 0), 1)

    @staticmethod
    def _scaled_consumable_value(value: float, multiplier: float) -> float:
        scaled = value * multiplier
        if value >= 0:
            return min(scaled, value)
        return max(scaled, value)

    @staticmethod
    def _consumable_stat(state: CalcState, stat: str) -> float:
        return state.consumable_stats.get(stat, 0)

    def _calc_stats(self, state: CalcState) -> None:
        self._calc_skill_cooldown(state)
        self._calc_attack_speed(state)
        self._calc_critical_hit(state)
        self._calc_critical_damage(state)
        self._calc_penetration(state)
        self._calc_accuracy(state)
        self._calc_attack_strength(state)
        self._calc_piercing_attack(state)
        self._calc_rage(state)
        self._calc_facilitation(state)
        self._calc_skill_power(state)
        self._calc_depths_fury(state)

    def _calc_skill_cooldown(self, state: CalcState) -> None:
        stats = state.dataset.stats
        mods = state.dataset.mods
        final_mods = state.dataset.final_power_mods
        value = stats.main.skill_cooldown + stats.pot.skill_cooldown + stats.scroll.skill_cooldown + stats.pet.skill_cooldown
        value += self._consumable_stat(state, "skill_cooldown")
        if final_mods.castle_damage:
            value += 5
        if state.dataset.skills.double_concentration.active:
            value += state.skill.double_skill_cooldown
        if mods.druid_active:
            value += 20
        if state.dataset.start_power_mods.castle_damage:
            value -= 5
        state.skill_cooldown_final = clamp(value, StatsLimit.MAX_SKILL_COOLDOWN)

    def _calc_attack_speed(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.attack_speed + stats.pot.attack_speed + stats.scroll.attack_speed + stats.pet.attack_speed
        value += self._consumable_stat(state, "attack_speed")
        if state.dataset.final_power_mods.castle_damage:
            value += 5
        if state.dataset.skills.double_concentration.active:
            value += state.skill.double_attack_speed
        if state.dataset.mods.gods_aid_hero:
            value += 12
        if state.dataset.start_power_mods.castle_damage:
            value -= 5
        state.attack_speed_final = clamp(value, StatsLimit.MAX_ATTACK_SPEED)

    def _calc_critical_hit(self, state: CalcState) -> None:
        stats = state.dataset.stats
        mods = state.dataset.mods
        value = stats.main.critical_hit + stats.pot.critical_hit + stats.scroll.critical_hit
        value += self._consumable_stat(state, "critical_hit")
        if state.dataset.final_power_mods.castle_damage:
            value += 5
        if state.dataset.skills.blessing_of_the_moon.active:
            value += state.skill.blessing_crit
        if mods.crushing_will:
            value += 20
        if mods.gods_aid_hero:
            value += 10
        if state.dataset.start_power_mods.castle_damage:
            value -= 5
        value = max(value, 0)
        state.critical_hit_hero = min(clamp(value, StatsLimit.MAX_CRITICAL_HIT_HERO), StatsLimit.MAX_CRITICAL_HIT_HERO)
        self._calc_luna_blessing_dependent_stats(state)

    def _calc_critical_damage(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.critical_damage + stats.pot.critical_damage + stats.scroll.critical_damage + stats.pet.critical_damage
        value += self._consumable_stat(state, "critical_damage")
        if state.dataset.skills.double_concentration.active:
            value += state.skill.double_crit_damage
        if state.dataset.mods.gods_aid_hero:
            value += 30
        if state.dataset.mods.roar_talent_almahad:
            value += 18
        luna = value
        if state.dataset.mods.crushing_will:
            luna += 30
        if state.dataset.mods.gods_aid_luna:
            luna += 30
        state.critical_damage_hero = clamp(value, StatsLimit.MAX_CRITICAL_DAMAGE)
        state.critical_damage_luna = luna

    def _calc_penetration(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.penetration + stats.pot.penetration + stats.scroll.penetration + stats.pet.penetration
        value += self._consumable_stat(state, "penetration")
        if state.dataset.final_power_mods.castle_damage:
            value += 5
        if state.dataset.skills.blessing_of_the_moon.active:
            value += state.skill.blessing_penetration
        if state.dataset.mods.irreversible_anger:
            value += 15
        if state.dataset.mods.druid_active:
            value += 16
        if state.dataset.start_power_mods.castle_damage:
            value -= 5
        value = max(value, 0)
        state.penetration_hero = min(clamp(value, state.max_penetration_hero), state.max_penetration_hero)
        self._calc_luna_blessing_dependent_stats(state)

    def _calc_luna_blessing_dependent_stats(self, state: CalcState) -> None:
        crit = state.critical_hit_hero
        pen = state.penetration_hero
        skills = state.dataset.skills
        if skills.blessing_of_the_moon.active and skills.blessing_of_the_moon.use_on_luna:
            crit += state.skill.blessing_crit
            pen += state.skill.blessing_penetration
        if state.dataset.mods.gods_aid_luna:
            crit += 10
        if state.dataset.mods.predatory_bond_talent_almahad:
            pen += min(state.penetration_hero, StatsLimit.MAX_PENETRATION_HERO) * 0.16
        state.critical_hit_luna = clamp(crit, StatsLimit.MAX_CRITICAL_HIT_HERO)
        state.penetration_luna = clamp(pen, state.max_penetration_hero)

    def _calc_accuracy(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.accuracy + stats.pot.accuracy + stats.scroll.accuracy + stats.pet.accuracy
        value += self._consumable_stat(state, "accuracy")
        if state.dataset.final_power_mods.castle_damage:
            value += 5
        if state.dataset.mods.irreversible_anger:
            value += 15
        if state.dataset.start_power_mods.castle_damage:
            value -= 5
        if state.dataset.mods.dragon_eye_level > 0:
            value += self._dragon_eye_accuracy(state.dataset.mods.dragon_eye_level)
        if state.dataset.skills.blessing_of_the_moon.active and state.dataset.mods.blago_talent:
            value += 10
        value = max(value, 0)
        final = clamp(value, StatsLimit.MAX_ACCURACY_HERO)
        state.accuracy_hero = final
        state.accuracy_luna = final

    def _calc_attack_strength(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.attack_strength + stats.pot.attack_strength + stats.scroll.attack_strength + stats.pet.attack_strength
        value += self._consumable_stat(state, "attack_strength")
        state.attack_strength_luna = value
        state.attack_strength_hero = clamp(value, StatsLimit.MAX_ATTACK_STRENGTH)
        if state.dataset.mods.predatory_bond_talent_almahad:
            state.attack_strength_luna += state.attack_strength_hero * 0.16

    def _calc_piercing_attack(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.piercing_attack + stats.pot.piercing_attack + stats.scroll.piercing_attack
        value += self._consumable_stat(state, "piercing_attack")
        state.piercing_attack_final = clamp(value, StatsLimit.MAX_PIERCING_ATTACK)

    def _calc_rage(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.rage + stats.pot.rage + stats.scroll.rage + stats.pet.rage
        value += self._consumable_stat(state, "rage")
        state.rage_final = clamp(value, StatsLimit.MAX_RAGE)

    def _calc_facilitation(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.facilitation + stats.pot.facilitation + stats.scroll.facilitation + stats.pet.facilitation
        value += self._consumable_stat(state, "facilitation")
        state.facilitation_luna = value
        state.facilitation_final = clamp(value, StatsLimit.MAX_FACILITATION)

    def _calc_skill_power(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.skill_power
        start_castle_coef = castle_coefficient(state.dataset.start_power_mods.castle_sector)
        final_castle_coef = castle_coefficient(state.dataset.final_power_mods.castle_sector)
        value -= round((start_castle_coef - 1) * 100, 1)
        value = max(value, 0)
        value += stats.pot.skill_power
        value += self._consumable_stat(state, "skill_power")
        if state.dataset.mods.dragon_eye_level > 0:
            value += 14
        value += round((final_castle_coef - 1) * 100, 1)
        state.skill_power_final = clamp(value, StatsLimit.MAX_SKILL_POWER)

    def _calc_depths_fury(self, state: CalcState) -> None:
        stats = state.dataset.stats
        value = stats.main.depths_fury + stats.scroll.depths_fury
        value += self._consumable_stat(state, "depths_fury")
        state.depths_fury_final = clamp(value, StatsLimit.MAX_DEPTH_FURY)

    def _calc_percents(self, state: CalcState) -> None:
        self._calc_harmonious_power(state)
        state.percent_mdd_start = self._percent_damage(state, "magical", start=True)
        state.percent_pdd_start = self._percent_damage(state, "physical", start=True)
        state.percent_mdd_final = self._percent_damage(state, "magical", start=False)
        state.percent_pdd_final = self._percent_damage(state, "physical", start=False)

    def _calc_harmonious_power(self, state: CalcState) -> None:
        equipment = state.dataset.equipment
        pieces = [equipment.helmet, equipment.body, equipment.gloves, equipment.belt, equipment.boots]
        state.harmonious_mdd = sum(equipment_percent(piece, "magical") for piece in pieces)
        state.harmonious_pdd = sum(equipment_percent(piece, "physical") for piece in pieces)

    def _jewelry_percent(self, state: CalcState, damage_type: str) -> float:
        percents = state.dataset.percents
        values = [
            percents.cloak,
            percents.amulet,
            percents.bracelet_left,
            percents.bracelet_right,
            percents.ring_left,
            percents.ring_right,
            percents.set_bonus,
        ]
        return sum(damage_percent(value, damage_type) for value in values)

    def _percent_damage(self, state: CalcState, damage_type: str, *, start: bool) -> float:
        power_mods = state.dataset.start_power_mods if start else state.dataset.final_power_mods
        value = 4 + self._jewelry_percent(state, damage_type)
        if power_mods.guild_damage:
            value += 10
        if power_mods.talent_damage:
            value += 4.75
        if power_mods.castle_damage:
            value += 7.5
        if not start:
            if state.dataset.mods.pairing_talent_almahad:
                value += 5.6 if damage_type == "magical" else 4
            if state.dataset.mods.priest_active:
                value += 20
            if state.dataset.mods.templar_active:
                value += 17.4
            value += state.consumable_mdd_percent if damage_type == "magical" else state.consumable_pdd_percent
        value += power_mods.additional_mdd if damage_type == "magical" else power_mods.additional_pdd
        return value

    def _attack_formula(self, state: CalcState, magedd: int, physdd: int) -> int:
        return magedd if state.staff else physdd

    def _moon_touch_formula(self, state: CalcState, magedd: int) -> int:
        skill = state.dataset.skills.moon_touch
        row = level_row(state.configs.moon_touch, skill.level)
        coefficient = float(row.get("PercentDamage", 100)) / 100
        if skill.talent_plus:
            coefficient += float(state.configs.moon_touch.get("TalentPlusBonus", 5)) / 100
        result = float(row.get("BaseDamage", 0)) + magedd * coefficient
        if skill.relic:
            result *= 1 + float(state.configs.moon_touch.get("RelicBonusPercent", 12)) / 100
        return cround(result)

    def _moon_touch_duration(self, state: CalcState) -> int:
        return int(level_row(state.configs.moon_touch, state.dataset.skills.moon_touch.level).get("Duration", 4))

    def _moon_touch_luna_coefficient_dd(self, state: CalcState) -> float:
        return float(level_row(state.configs.moon_touch, state.dataset.skills.moon_touch.level).get("PercentDamageLuna", 7)) / 100

    def _beast_awakening_formula(self, state: CalcState, magedd: int, physdd: int) -> int:
        skill = state.dataset.skills.beast_awakening
        row = level_row(state.configs.beast_awakening, skill.level)
        coef_m = float(row.get("CoefficientMagicalDamage", 35)) / 100
        coef_p = float(row.get("CoefficientPhysicalDamage", 70)) / 100
        if skill.talent_mage:
            coef_m += float(state.configs.beast_awakening.get("TalentMageBonus", 3)) / 100
        else:
            bonuses = state.configs.beast_awakening.get("TalentPhysBonuses", {})
            if skill.talent_physical_level > 0:
                coef_p += float(bonuses.get(str(min(max(skill.talent_physical_level, 1), 3)), 0)) / 100
        return cint(float(row.get("BaseDamage", 20)) + coef_m * magedd + coef_p * physdd)

    def _order_to_attack_formula(self, state: CalcState, magedd: int, physdd: int) -> int:
        skill = state.dataset.skills.order_to_attack
        row = level_row(state.configs.order_to_attack, skill.level)
        coefficient = float(row.get("Percents", 5)) / 100
        talents = state.configs.order_to_attack.get("Talents", {})
        guardian = max_level_row(talents.get("GuardianUnity", {}).get("Levels", []), skill.talent_guardian_unity_level)
        dual = max_level_row(talents.get("DualRage", {}).get("Levels", []), skill.talent_dual_rage_level)
        if skill.talent_guardian_unity_level > 0 and guardian:
            coefficient += float(guardian.get("Percents", 0)) / 100
        elif skill.talent_dual_rage_level > 0 and dual:
            coefficient += float(dual.get("Percents", 0)) / 100
        return cint(self._beast_awakening_formula(state, magedd, physdd) * coefficient)

    def _chain_lightning_formula(self, state: CalcState, magedd: int, physdd: int) -> int:
        skill = state.dataset.skills.chain_lightning
        row = level_row(state.configs.chain_lightning, skill.level)
        if magedd >= physdd:
            result = float(row.get("MagicalPercents", 100)) / 100 * magedd
        else:
            result = float(row.get("PhysicalPercents", 55)) / 100 * physdd
        if skill.relic:
            result *= 1 + float(state.configs.chain_lightning.get("RelicBonusPercent", 12)) / 100
        return cint(result)

    def _aura_formula(self, state: CalcState, magedd: int) -> int:
        skill = state.dataset.skills.aura_of_the_forest
        row = level_row(state.configs.aura, skill.level)
        result = magedd * (float(row.get("Percents", 35)) / 100)
        if skill.talent_power_of_nature:
            result *= (1 + float(state.configs.aura.get("TalentPowerOfNature", 15)) / 100) * (
                1 + float(state.configs.aura.get("BaseIncrease", 20)) / 100
            )
        return cround(result)

    def _bestial_rampage_formula(self, state: CalcState, magedd: int, physdd: int) -> int:
        return cint(self._beast_awakening_formula(state, magedd, physdd) * state.skill.bestial_damage_multiplier)

    def _moonlight_formula(self, state: CalcState, magedd: int) -> int:
        skill = state.dataset.skills.moonlight
        row = level_row(state.configs.moonlight, skill.level)
        coefficient = float(row.get("Percents", 20)) / 100
        if skill.talent_level > 0:
            talent_row = max_level_row(state.configs.moonlight.get("Talents", {}).get("Levels", []), skill.talent_level)
            if talent_row:
                coefficient += float(talent_row.get("Percents", 0)) / 100
        return cint(magedd * coefficient)

    def _cooldown(self, base: float, state: CalcState) -> float:
        return base / coeff(state.skill_cooldown_final) + TIME_CAST

    def _moon_touch_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.moon_touch.get("BaseCooldown", 11)), state)

    def _chain_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.chain_lightning.get("BaseCooldown", 19)), state)

    def _bestial_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.bestial_rampage.get("BaseCooldown", 26)), state)

    def _aura_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.aura.get("BaseCooldown", 24)), state)

    def _moonlight_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.moonlight.get("BaseCooldown", 14)), state)

    def _order_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.order_to_attack.get("BaseCooldown", 10)), state)

    def _blessing_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.blessing.get("BaseCooldown", 25)), state)

    def _double_concentration_cooldown(self, state: CalcState) -> float:
        return self._cooldown(float(state.configs.double_concentration.get("BaseCooldown", 22)), state)

    def _healing_cooldown(self, state: CalcState) -> float:
        return self._cooldown(14, state)

    def _legendary_chain(self, state: CalcState) -> float:
        return 1 - state.skill_cooldown_final / 250

    def _legendary_moonlight(self, state: CalcState) -> float:
        return 0.65 * (1 - state.skill_cooldown_final / 130)

    def _legendary_attack_speed(self, state: CalcState) -> float:
        skills = state.dataset.skills
        s = 0.0
        if skills.moon_touch.active:
            s += 1 / self._moon_touch_cooldown(state)
        if skills.order_to_attack.active:
            s += 1 / self._order_cooldown(state)
        if skills.healing.active:
            s += 1 / self._healing_cooldown(state)
        if skills.chain_lightning.active:
            s += 1 / self._chain_cooldown(state)
        if skills.bestial_rampage.active:
            s += 1 / self._bestial_cooldown(state)
        if skills.aura_of_the_forest.active:
            s += 1 / self._aura_cooldown(state)
        if skills.moonlight.non_permanent_active:
            s += 1 / self._moonlight_cooldown(state)
        if skills.blessing_of_the_moon.active:
            s += 1 / self._blessing_cooldown(state)
        if skills.double_concentration.active:
            s += 1 / self._double_concentration_cooldown(state)
        s = min(max(s * 1.55, 0), 1)
        return -0.3 * s + 1

    def _attack_delay(self, state: CalcState) -> float:
        return (state.attack_delay_base * (100 - state.attack_speed_final) / 100) / self._legendary_attack_speed(state)

    def _time_bestial_rampage(self, state: CalcState) -> float:
        value = state.skill.bestial_time_active * coeff(state.facilitation_luna) / self._bestial_cooldown(state)
        return min(max(value, 0), 1)

    def _time_without_bestial_rampage(self, state: CalcState) -> float:
        value = (self._bestial_cooldown(state) - state.skill.bestial_time_active * coeff(state.facilitation_luna)) / self._bestial_cooldown(state)
        return min(max(value, 0), 1)

    def _attack_delay_luna_with_bestial_rampage(self, state: CalcState) -> float:
        gods = 12 if state.dataset.mods.gods_aid_luna else 0
        return 2.5 * ((100 - state.skill.bestial_attack_speed - gods) / 100)

    def _merman_duration(self, state: CalcState) -> float:
        return 10 * coeff(state.facilitation_final) / 15 * 0.9

    def _coefficient_of_moon_touch_for_luna(self, state: CalcState) -> float:
        if not state.dataset.skills.moon_touch.active:
            return 1
        return (
            self._moon_touch_duration(state)
            * self._coef_counterstand(state)
            / self._moon_touch_cooldown(state)
            * self._moon_touch_luna_coefficient_dd(state)
            + 1
        )

    def _coef_counterstand(self, state: CalcState) -> float:
        return 0.67 if state.dataset.mods.counterstand else 1

    def _coef_bp(self, state: CalcState) -> float:
        return 1.1 if state.dataset.mods.bp_dungeon else 1

    def _coef_sacred_hero(self, state: CalcState) -> float:
        return 1.15 if state.dataset.mods.sacred_shield_hero else 1

    def _coef_sacred_luna(self, state: CalcState) -> float:
        return 1.15 if state.dataset.mods.sacred_shield_luna else 1

    def _coef_critical_hit_auto(self, state: CalcState) -> float:
        addition = 20 * (1 - state.critical_hit_hero / 100) if state.dataset.mods.irreversible_anger else 0
        crit = ((state.critical_hit_hero + addition) - state.dataset.stats.main.resilience) / 100
        crit = min(max(crit, 0), 1)
        res = state.dataset.stats.main.resilience
        depth = coeff(state.depths_fury_final)
        return ((1 - res / 100) * (1 - crit) + (1 - res / 100) ** 2 * crit * (2 + state.critical_damage_hero / 100) * depth) * depth

    def _coef_critical_hit_luna(self, state: CalcState) -> float:
        crit = (state.critical_hit_luna - state.dataset.stats.main.resilience) / 100
        crit = min(max(crit, 0), 1)
        res = state.dataset.stats.main.resilience
        depth = coeff(state.depths_fury_final)
        return ((1 - res / 100) * (1 - crit) + (1 - res / 100) ** 2 * crit * (2 + state.critical_damage_luna / 100) * depth) * depth

    def _coef_critical_hit_skill(self, state: CalcState) -> float:
        crit = (state.critical_hit_hero - state.dataset.stats.main.resilience) / 100
        crit = min(max(crit, 0), 1)
        res = state.dataset.stats.main.resilience
        crit_damage = state.critical_damage_hero + (30 if state.dataset.mods.crushing_will else 0)
        depth = coeff(state.depths_fury_final)
        return (
            (1 - res / 100) * (1 - crit)
            + (1 - res / 100) ** 2 * crit * (2 + (crit_damage + state.animal_rage_add) / 100) * depth
        ) * depth

    def _coef_penetration(self, state: CalcState) -> float:
        return 1 - max(0, state.dataset.stats.main.protection - state.penetration_hero) / 100

    def _coef_penetration_luna(self, state: CalcState) -> float:
        return 1 - max(0, state.dataset.stats.main.protection - state.penetration_luna) / 100

    def _coef_accuracy(self, state: CalcState) -> float:
        return 1 - max(0, state.dataset.stats.main.dodge - state.accuracy_hero) / 100

    def _coef_accuracy_luna(self, state: CalcState) -> float:
        return 1 - max(0, state.dataset.stats.main.dodge - state.accuracy_luna) / 100

    def _coef_piercing(self, state: CalcState) -> float:
        piercing_raw = state.dataset.stats.main.piercing_attack
        return 1 - max(0, (state.dataset.stats.main.protection - state.penetration_hero) * (1 - piercing_raw / 100)) / 100

    def _coef_piercing_luna(self, state: CalcState) -> float:
        piercing_raw = state.dataset.stats.main.piercing_attack
        return 1 - max(0, (state.dataset.stats.main.protection - state.penetration_luna) * (1 - piercing_raw / 100)) / 100

    def _coef_rage(self, state: CalcState) -> float:
        t = (10 + state.continuous_fury_add) * coeff(state.facilitation_final)
        s = 0.0
        if state.dataset.skills.attack.active:
            s += 1 / self._attack_delay(state)
        if state.dataset.skills.moon_touch.active:
            s += 1 / self._moon_touch_cooldown(state)
        if state.dataset.skills.chain_lightning.active:
            s += 1 / self._chain_cooldown(state)
        if s == 0 or state.rage_final == 0:
            return 0
        result = t * state.rage_final / 100 * s
        return min(max(result, 0), 1) * 0.1

    def _calc_attack(self, state: CalcState, magedd: int, physdd: int) -> int:
        coeffs_start = coeff(state.attack_strength_hero) * self._coef_piercing(state) * state.predatory_delirium_coef
        coeffs_final = self._coef_critical_hit_auto(state) * self._coef_accuracy(state) * self._coef_bp(state) * self._coef_sacred_hero(state)
        hit = cint(self._attack_formula(state, magedd, physdd) * coeffs_start)
        dpm = cint(hit / self._attack_delay(state) * 60)
        final_dpm = cint(dpm * coeffs_final)
        state.breakdown.attack = DamageLine(hit=hit, dpm=final_dpm)
        return final_dpm

    def _calc_moon_touch(self, state: CalcState, magedd: int) -> int:
        coeffs_start = coeff(state.skill_power_final) * state.bestial_rage_coef * state.predatory_delirium_coef * state.moment_of_power_coef * self._coef_penetration(state)
        coeffs_final = self._coef_critical_hit_skill(state) * self._coef_accuracy(state) * self._coef_bp(state) * self._coef_sacred_hero(state)
        hit = cint(self._moon_touch_formula(state, magedd) * coeffs_start)
        dpm = cint(hit * 60 / self._moon_touch_cooldown(state))
        dpm = cint(dpm * coeffs_final)
        state.breakdown.moon_touch = DamageLine(hit=hit, dpm=dpm)
        return dpm

    def _calc_chain_lightning(self, state: CalcState, magedd: int, physdd: int) -> int:
        coeffs_start = coeff(state.skill_power_final) * state.bestial_rage_coef * state.predatory_delirium_coef * state.moment_of_power_coef * self._coef_penetration(state)
        coeffs_final = self._coef_critical_hit_skill(state) * self._coef_accuracy(state) * self._coef_bp(state) * self._coef_sacred_hero(state)
        hit = cint(self._chain_lightning_formula(state, magedd, physdd) * coeffs_start)
        dpm = cint(hit * 60 / self._chain_cooldown(state) * self._legendary_chain(state))
        final_dpm = cint(dpm * coeffs_final)
        state.breakdown.chain_lightning = DamageLine(hit=hit, dpm=final_dpm)
        return final_dpm

    def _calc_beast_awakening(self, state: CalcState, magedd: int, physdd: int) -> int:
        coeffs_start = coeff(state.attack_strength_luna) * self._coef_piercing_luna(state)
        coeffs_final = self._coefficient_of_moon_touch_for_luna(state) * self._coef_critical_hit_luna(state) * self._coef_accuracy_luna(state) * self._coef_sacred_luna(state)
        hit = cint(self._beast_awakening_formula(state, magedd, physdd) * coeffs_start)
        gods = 12 if state.dataset.mods.gods_aid_luna else 0
        dpm = cint(hit * 60 / (2.5 * ((100 - gods) / 100)))
        state.breakdown.beast_awakening = DamageLine(hit=hit, dpm=dpm)
        return cint(dpm * coeffs_final)

    def _calc_bestial_rampage(self, state: CalcState, magedd: int, physdd: int) -> int:
        coeffs_start = coeff(state.attack_strength_luna) * self._coef_piercing_luna(state)
        coeffs_final = self._coefficient_of_moon_touch_for_luna(state) * self._coef_critical_hit_luna(state) * self._coef_accuracy_luna(state) * self._coef_sacred_luna(state)
        hit = cint(self._bestial_rampage_formula(state, magedd, physdd) * coeffs_start)
        gods = 12 if state.dataset.mods.gods_aid_luna else 0
        increase_attack_speed = (100 - (state.skill.bestial_attack_speed + gods)) / 100
        dpm = cint(hit * 60 / (2.5 * increase_attack_speed))
        state.breakdown.bestial_rampage = DamageLine(hit=hit, dpm=dpm)
        return cint(dpm * coeffs_final)

    def _calc_order_to_attack(self, state: CalcState, magedd: int, physdd: int) -> int:
        coeffs_start = coeff(state.attack_strength_luna) * self._coef_piercing_luna(state)
        coeffs_final = self._coefficient_of_moon_touch_for_luna(state) * self._coef_critical_hit_luna(state) * self._coef_accuracy_luna(state) * self._coef_sacred_luna(state)
        hit = cint(self._order_to_attack_formula(state, magedd, physdd) * coeffs_start)
        dpm = cint(hit * 60 / self._order_cooldown(state))
        if state.dataset.skills.bestial_rampage.active:
            dpm = cint(dpm * (1 + (state.skill.bestial_damage_multiplier - 1) * self._time_bestial_rampage(state)))
        final_dpm = cint(dpm * coeffs_final)
        state.breakdown.order_to_attack = DamageLine(hit=hit, dpm=final_dpm)
        return final_dpm

    def _calc_aura(self, state: CalcState, magedd: int) -> tuple[int, int]:
        result_luna = 0
        result_hero = 0
        skill = state.dataset.skills.aura_of_the_forest
        coef_lotus = 0.75
        coeffs_luna_start = coeff(state.skill_power_final) * state.bestial_rage_coef * state.predatory_delirium_coef * self._coef_penetration_luna(state)
        coeffs_hero_start = coeff(state.skill_power_final) * state.bestial_rage_coef * state.predatory_delirium_coef * state.long_death_coef * self._coef_penetration(state)
        coeffs_luna_final = self._coefficient_of_moon_touch_for_luna(state) * self._coef_critical_hit_luna(state) * self._coef_accuracy_luna(state) * self._coef_sacred_luna(state)
        coeffs_hero_final = self._coef_critical_hit_skill(state) * self._coef_accuracy(state) * self._coef_bp(state) * self._coef_sacred_hero(state)
        time_active = int(state.configs.aura.get("TimeActive", 10))
        delay = int(state.configs.aura.get("Delay", 2))
        count_hero = cint(time_active * coeff(state.facilitation_final) / delay)
        count_luna = cint(time_active * coeff(state.facilitation_luna) / delay)
        luna_hit = cint(self._aura_formula(state, magedd) * coeffs_luna_start)
        hero_hit = cint(self._aura_formula(state, magedd) * coeffs_hero_start)

        if skill.talent_grandeur_of_lotus:
            if state.dataset.skills.beast_awakening.active:
                luna_hit = cint(luna_hit * (1 if skill.talent_abuse else coef_lotus))
                luna_dpm = cint(luna_hit * 60 / self._aura_cooldown(state) * count_luna)
                luna_final_dpm = cint(luna_dpm * coeffs_luna_final)
                result_luna += luna_final_dpm
                state.breakdown.aura_luna = DamageLine(hit=luna_hit, dpm=luna_final_dpm)
            else:
                state.breakdown.aura_luna = DamageLine()
            hero_hit = cint(hero_hit * (1 if skill.talent_abuse else coef_lotus))
            hero_dpm = cint(hero_hit * 60 / self._aura_cooldown(state) * count_hero)
            hero_final_dpm = cint(hero_dpm * coeffs_hero_final)
            result_hero += hero_final_dpm
            state.breakdown.aura_hero = DamageLine(hit=hero_hit, dpm=hero_final_dpm)
            return result_luna, result_hero

        if state.dataset.skills.beast_awakening.active:
            luna_dpm = cint(luna_hit * 60 / self._aura_cooldown(state) * count_luna)
            luna_final_dpm = cint(luna_dpm * coeffs_luna_final)
            result_luna += luna_final_dpm
            state.breakdown.aura_luna = DamageLine(hit=luna_hit, dpm=luna_final_dpm)
            state.breakdown.aura_hero = DamageLine()
            return result_luna, result_hero

        hero_dpm = cint(hero_hit * 60 / self._aura_cooldown(state) * count_hero)
        hero_final_dpm = cint(hero_dpm * coeffs_hero_final)
        result_hero += hero_final_dpm
        state.breakdown.aura_hero = DamageLine(hit=hero_hit, dpm=hero_final_dpm)
        state.breakdown.aura_luna = DamageLine()
        return result_luna, result_hero

    def _calc_moonlight(self, state: CalcState, magedd: int, pure_magedd: int) -> int:
        parts: list[tuple[str, int, int]] = []
        skill = state.dataset.skills.moonlight
        coeffs_start = coeff(state.skill_power_final) * state.bestial_rage_coef * state.predatory_delirium_coef * state.long_death_coef * self._coef_penetration(state)
        coeffs_final = self._coef_critical_hit_skill(state) * self._coef_bp(state) * self._coef_sacred_hero(state)
        if skill.permanent_active:
            hit = cint(3 * self._moonlight_formula(state, cint(pure_magedd * state.coefficient_triton + magedd)) * coeffs_start)
            dpm = hit * 30
            parts.append(("permanent", hit, dpm))
        else:
            state.breakdown.moonlight_permanent = DamageLine()
        if skill.non_permanent_active:
            hit = cint(self._moonlight_formula(state, magedd) * coeffs_start)
            dpm = cint((hit * 4) / self._moonlight_cooldown(state) * 60 * self._legendary_moonlight(state))
            parts.append(("non_permanent", hit, cint(dpm * self._coef_accuracy(state))))
        else:
            state.breakdown.moonlight_non_permanent = DamageLine()

        total = cint(sum(dpm for _, _, dpm in parts) * coeffs_final)
        distributed = 0
        for index, (kind, hit, dpm) in enumerate(parts):
            final_dpm = total - distributed if index == len(parts) - 1 else cint(dpm * coeffs_final)
            distributed += final_dpm
            if kind == "permanent":
                state.breakdown.moonlight_permanent = DamageLine(hit=hit, dpm=final_dpm)
            else:
                state.breakdown.moonlight_non_permanent = DamageLine(hit=hit, dpm=final_dpm)
        return total

    def _calc_symbiosis(self, state: CalcState, magedd: int, physdd: int) -> tuple[int, int]:
        coeffs_for_luna_start = (
            self._coef_critical_hit_auto(state)
            * self._coef_piercing(state)
            * self._coef_accuracy(state)
            * coeff(state.attack_strength_hero)
            * self._coef_sacred_hero(state)
        )
        coeffs_for_hero_start = (
            self._coef_critical_hit_luna(state)
            * self._coef_piercing_luna(state)
            * self._coef_accuracy_luna(state)
            * coeff(state.attack_strength_luna)
            * self._coef_sacred_luna(state)
        )
        coeffs_for_luna_final = (
            state.predatory_delirium_coef
            * self._coefficient_of_moon_touch_for_luna(state)
            * self._coef_bp(state)
            * self._coef_piercing_luna(state)
            * self._coef_sacred_luna(state)
        )
        coeffs_for_hero_final = (
            state.predatory_delirium_coef
            * self._coefficient_of_moon_touch_for_luna(state)
            * self._coef_bp(state)
            * self._coef_piercing(state)
            * self._coef_sacred_hero(state)
        )
        tp = self._attack_delay(state)
        tl = 2.5 * (1 - (12 if state.dataset.mods.gods_aid_luna else 0) / 100)
        t = max(tp, tl)
        dpm_hero = 0.15 * 60 / t * (self._beast_awakening_formula(state, magedd, physdd) * coeffs_for_hero_start)
        dpm_luna = 0.15 * 60 / t * (self._attack_formula(state, magedd, physdd) * coeffs_for_luna_start)
        if state.dataset.skills.bestial_rampage.active:
            tbr = self._attack_delay_luna_with_bestial_rampage(state)
            t = max(tp, tbr)
            dpm_br_hero = 0.15 * 60 / t * (self._bestial_rampage_formula(state, magedd, physdd) * coeffs_for_hero_start)
            dpm_br_luna = 0.15 * 60 / t * (self._attack_formula(state, magedd, physdd) * coeffs_for_luna_start)
            hero = cint((dpm_hero * self._time_without_bestial_rampage(state) + dpm_br_hero * self._time_bestial_rampage(state)) * coeffs_for_hero_final)
            luna = cint((dpm_luna * self._time_without_bestial_rampage(state) + dpm_br_luna * self._time_bestial_rampage(state)) * coeffs_for_luna_final)
            return luna, hero
        hero = cint(dpm_hero * coeffs_for_hero_final)
        luna = cint(dpm_luna * coeffs_for_luna_final)
        return luna, hero

    def _dragon_eye_accuracy(self, level: int) -> int:
        return {1: 7, 2: 10, 3: 13, 4: 18}.get(level, 0)


calculator = BeastMasterCalculator()
