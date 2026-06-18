from app.domain.models import DataSetBM
from app.main import default_dataset
from app.services.build_io import export_legacy_build, import_build
from app.services.calculator import calculator
from app.services.state_rules import normalize_dataset


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
    assert result.skills.attack.dpm == 18839
    assert result.skills.beast_awakening.dpm == 24266


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
