from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.domain.models import CalculationResult, DataSetBM, PresetRequest
from app.services.build_io import export_legacy_build, import_build
from app.services.calculator import calculator
from app.services.state_rules import normalize_dataset


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Warspear Beastmaster DPM Calculator")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def default_dataset() -> DataSetBM:
    data = DataSetBM()
    data.stats.main.magical_damage = 1200
    data.stats.main.physical_damage = 900
    data.stats.main.critical_hit = 35
    data.stats.main.critical_damage = 50
    data.stats.main.penetration = 25
    data.stats.main.accuracy = 30
    data.stats.main.attack_strength = 20
    data.stats.main.piercing_attack = 10
    data.stats.main.skill_cooldown = 45
    data.stats.main.attack_speed = 35
    data.stats.main.protection = 45
    data.stats.main.dodge = 20
    data.stats.main.resilience = 0

    data.skills.attack.active = True
    data.skills.moon_touch.active = True
    data.skills.beast_awakening.active = True
    data.skills.order_to_attack.active = True
    data.skills.chain_lightning.active = True
    data.skills.bestial_rampage.active = True
    data.skills.aura_of_the_forest.active = True
    data.skills.moonlight.non_permanent_active = True
    data.skills.blessing_of_the_moon.active = True
    data.skills.double_concentration.active = True
    return data


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/default", response_model=DataSetBM)
def get_default() -> DataSetBM:
    return normalize_dataset(default_dataset())


@app.post("/api/preset", response_model=DataSetBM)
def get_preset(request: PresetRequest) -> DataSetBM:
    if request.preset == "empty":
        return normalize_dataset(DataSetBM())
    return normalize_dataset(default_dataset())


@app.post("/api/calculate", response_model=CalculationResult)
def calculate(dataset: DataSetBM) -> CalculationResult:
    return calculator.calculate(normalize_dataset(dataset))


@app.post("/api/build/import", response_model=DataSetBM)
def import_build_json(payload: Any = Body(...)) -> DataSetBM:
    return import_build(payload)


@app.post("/api/build/export")
def export_build_json(dataset: DataSetBM) -> dict[str, Any]:
    normalized = normalize_dataset(dataset)
    result = calculator.calculate(normalized)
    return export_legacy_build(normalized, result.totals.total)
