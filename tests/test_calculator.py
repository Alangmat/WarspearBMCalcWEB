from app.domain.models import DataSetBM
from app.main import default_dataset
from app.services.build_io import export_legacy_build, import_build
from app.services.calculator import calculator
from app.services.consumables import ConsumableEffect, ConsumableItem, load_consumable_catalog
from app.services.state_rules import normalize_dataset


def source_sum(result) -> int:
    return sum(
        [
            result.skills.attack.dpm,
            result.skills.moon_touch.dpm,
            result.skills.chain_lightning.dpm,
            result.skills.beast_awakening.dpm,
            result.skills.bestial_rampage.dpm,
            result.skills.order_to_attack.dpm,
            result.skills.aura_luna.dpm,
            result.skills.aura_hero.dpm,
            result.skills.moonlight_permanent.dpm,
            result.skills.moonlight_non_permanent.dpm,
            result.skills.symbiosis_hero,
            result.skills.symbiosis_luna,
        ]
    )


def test_empty_dataset_has_zero_dpm() -> None:
    result = calculator.calculate(DataSetBM())

    assert result.totals.total == 0
    assert result.totals.hero == 0
    assert result.totals.luna == 0


def test_default_dataset_snapshot() -> None:
    result = calculator.calculate(default_dataset())

    assert result.totals.total == 128646
    assert result.totals.hero == 61913
    assert result.totals.luna == 66733
    assert result.skills.attack.dpm == 31638
    assert result.skills.beast_awakening.dpm == 24266


def test_source_breakdown_matches_total_dpm() -> None:
    result = calculator.calculate(default_dataset())

    assert source_sum(result) == result.totals.total


def test_branch_normalization_clears_disabled_talents() -> None:
    data = DataSetBM()
    data.talents.dual_rage_active = True
    data.talents.guardian_unity_active = True
    data.skills.order_to_attack.talent_guardian_unity_level = 3
    data.talents.harmonious_power = True
    data.skills.bestial_rampage.talent = True

    normalized = normalize_dataset(data)

    assert normalized.talents.dual_rage_active is True
    assert normalized.talents.guardian_unity_active is False
    assert normalized.skills.order_to_attack.talent_guardian_unity_level == 0
    assert normalized.talents.harmonious_power is False
    assert normalized.skills.bestial_rampage.talent is True


def test_almahad_roar_and_predatory_bond_are_exclusive() -> None:
    data = DataSetBM()
    data.mods.roar_talent_almahad = True
    data.mods.predatory_bond_talent_almahad = True

    normalized = normalize_dataset(data)

    assert normalized.mods.roar_talent_almahad is True
    assert normalized.mods.predatory_bond_talent_almahad is False


def test_import_legacy_build_maps_core_fields() -> None:
    imported = import_build(
        {
            "Name": "Old build",
            "MagicalDamage": "1200",
            "PhysicalDamage": "900",
            "SkillCooldown": 45,
            "MoonTouch": {"Level": 5, "HasRelic": True},
            "MoonTouchActive": True,
            "StaffSelected": True,
            "DualRageActive": True,
            "BestialRampage": {"Level": 4, "HasTalant": True},
            "RoarTalentAlmahadActive": True,
            "PredatoryBondTalentAlmahadActive": True,
            "SelectedAmuletNew": 2,
            "SelectedHelmetNew": 1,
        }
    )

    assert imported.name == "Old build"
    assert imported.weapon == "staff"
    assert imported.stats.main.magical_damage == 1200
    assert imported.skills.moon_touch.level == 5
    assert imported.skills.moon_touch.relic is True
    assert imported.skills.bestial_rampage.talent is True
    assert imported.mods.roar_talent_almahad is True
    assert imported.mods.predatory_bond_talent_almahad is False
    assert imported.percents.amulet == "magic6"
    assert imported.equipment.helmet == "cloth"


def test_export_legacy_build_contains_old_shape() -> None:
    data = default_dataset()
    data.talents.guardian_unity_active = True
    data.talents.harmonious_power = True

    exported = export_legacy_build(data, result_dd=123)

    assert exported["ResultDD"] == 123
    assert exported["MoonTouch"]["Level"] == 1
    assert exported["MaceSelected"] is True
    assert exported["GuardianUnityActive"] is True
    assert exported["HasTalentHarmoniousPower"] is True


def test_consumable_stat_is_added_before_final_cap(monkeypatch) -> None:
    data = DataSetBM()
    data.stats.main.critical_hit = 50
    data.consumables.potion = "crit_potion"
    item = ConsumableItem(
        id="crit_potion",
        type="potion",
        name="Crit potion",
        effects=[ConsumableEffect(stat="critical_hit", value=10)],
    )
    monkeypatch.setattr("app.services.calculator.get_selected_consumables", lambda selection: [item])

    result = calculator.calculate(data)

    assert result.final_stats.critical_hit_hero == 53


def test_scroll_flat_power_is_added_before_final_percents(monkeypatch) -> None:
    data = DataSetBM()
    data.stats.main.magical_damage = 1040
    data.consumables.scroll = "magic_scroll"
    item = ConsumableItem(
        id="magic_scroll",
        type="scroll",
        name="Magic scroll",
        effects=[ConsumableEffect(stat="magical_power_flat", value=100)],
    )
    monkeypatch.setattr("app.services.calculator.get_selected_consumables", lambda selection: [item])

    result = calculator.calculate(data)

    assert result.final_stats.pure_magical_damage == 1100
    assert result.final_stats.effective_magical_damage == 1144


def test_timed_pet_bonus_uses_facilitation_uptime(monkeypatch) -> None:
    data = DataSetBM()
    data.stats.main.facilitation = 50
    data.consumables.pet = "speed_pet"
    item = ConsumableItem(
        id="speed_pet",
        type="pet",
        name="Speed pet",
        effects=[ConsumableEffect(stat="attack_speed", value=20, duration=10, cooldown=20)],
    )
    monkeypatch.setattr("app.services.calculator.get_selected_consumables", lambda selection: [item])

    result = calculator.calculate(data)

    assert result.final_stats.attack_speed == 15


def test_pet_consumable_catalog_allows_skill_power(tmp_path) -> None:
    path = tmp_path / "consumables.json"
    path.write_text(
        """
        {
          "version": 1,
          "items": [
            {
              "id": "skill_pet",
              "type": "pet",
              "name": "Skill pet",
              "effects": [
                {"stat": "skill_power", "value": 10, "passive": true}
              ]
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    catalog = load_consumable_catalog(path)

    assert catalog.items[0].effects[0].stat == "skill_power"
