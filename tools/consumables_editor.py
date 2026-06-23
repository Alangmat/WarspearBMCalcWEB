from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from uuid import uuid4

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent
    return Path(__file__).resolve().parents[1]


ROOT_DIR = project_root()
JSON_PATH = ROOT_DIR / "app" / "config" / "consumables.json"
ICON_DIR = ROOT_DIR / "app" / "static" / "icons" / "consumables"

TYPE_LABELS = {
    "potion": "Зелье",
    "scroll": "Свиток",
    "pet": "Питомец",
}
LABEL_TYPES = {value: key for key, value in TYPE_LABELS.items()}

STAT_LABELS = {
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
LABEL_STATS = {value: key for key, value in STAT_LABELS.items()}

ALLOWED_STATS = {
    "potion": [
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
    ],
    "scroll": [
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
    ],
    "pet": [
        "skill_cooldown",
        "attack_speed",
        "critical_damage",
        "penetration",
        "accuracy",
        "attack_strength",
        "rage",
        "facilitation",
        "magical_power_percent",
        "physical_power_percent",
    ],
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or f"item_{uuid4().hex[:8]}"


def effect_summary(item: dict) -> str:
    parts = []
    for effect in item.get("effects", []):
        stat = STAT_LABELS.get(effect.get("stat"), effect.get("stat", ""))
        value = effect.get("value", 0)
        suffix = "%" if str(effect.get("stat", "")).endswith("_percent") else ""
        parts.append(f"{stat} +{value}{suffix}")
    return "; ".join(parts)


class ConsumablesEditor:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Редактор расходников Warspear")
        self.root.geometry("1120x680")
        self.json_path = JSON_PATH
        self.catalog: dict = {"version": 1, "items": []}
        self.selected_index: int | None = None

        self.type_var = tk.StringVar(value=TYPE_LABELS["potion"])
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.icon_var = tk.StringVar()
        self.effect_rows: list[dict[str, object]] = []

        self._build_layout()
        self.load_json(self.json_path)

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Button(toolbar, text="Открыть JSON", command=self.open_json).pack(side="left")
        ttk.Button(toolbar, text="Сохранить JSON", command=self.save_json).pack(side="left", padx=(8, 0))
        ttk.Label(toolbar, textvariable=tk.StringVar(value=str(self.json_path))).pack(side="left", padx=14)

        left = ttk.Frame(self.root, padding=(8, 0, 4, 8))
        left.grid(row=1, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        ttk.Label(left, text="Расходники").grid(row=0, column=0, sticky="w")
        self.tree = ttk.Treeview(left, columns=("type", "name", "effects"), show="headings", selectmode="browse")
        self.tree.heading("type", text="Тип")
        self.tree.heading("name", text="Название")
        self.tree.heading("effects", text="Эффекты")
        self.tree.column("type", width=80, stretch=False)
        self.tree.column("name", width=180, stretch=True)
        self.tree.column("effects", width=300, stretch=True)
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        list_buttons = ttk.Frame(left)
        list_buttons.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(list_buttons, text="Новый", command=self.new_item).pack(side="left")
        ttk.Button(list_buttons, text="Удалить", command=self.delete_item).pack(side="left", padx=(8, 0))

        form = ttk.Frame(self.root, padding=(4, 0, 8, 8))
        form.grid(row=1, column=1, sticky="nsew")
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Тип").grid(row=0, column=0, sticky="w", pady=4)
        type_box = ttk.Combobox(form, textvariable=self.type_var, values=list(TYPE_LABELS.values()), state="readonly")
        type_box.grid(row=0, column=1, sticky="ew", pady=4)
        type_box.bind("<<ComboboxSelected>>", lambda _event: self.update_effect_stat_lists())

        ttk.Label(form, text="ID").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.id_var).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Название").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.name_var).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Иконка").grid(row=3, column=0, sticky="w", pady=4)
        icon_line = ttk.Frame(form)
        icon_line.grid(row=3, column=1, sticky="ew", pady=4)
        icon_line.columnconfigure(0, weight=1)
        ttk.Entry(icon_line, textvariable=self.icon_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(icon_line, text="Выбрать", command=self.choose_icon).grid(row=0, column=1, padx=(8, 0))

        effects = ttk.LabelFrame(form, text="Характеристики")
        effects.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        for column, weight in enumerate((2, 1, 1, 1, 1)):
            effects.columnconfigure(column, weight=weight)
        ttk.Label(effects, text="Характеристика").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        ttk.Label(effects, text="Значение").grid(row=0, column=1, sticky="w", padx=6, pady=5)
        ttk.Label(effects, text="Пассивный").grid(row=0, column=2, sticky="w", padx=6, pady=5)
        ttk.Label(effects, text="Время").grid(row=0, column=3, sticky="w", padx=6, pady=5)
        ttk.Label(effects, text="Перезарядка").grid(row=0, column=4, sticky="w", padx=6, pady=5)

        for row in range(4):
            stat_var = tk.StringVar()
            value_var = tk.StringVar()
            passive_var = tk.BooleanVar()
            duration_var = tk.StringVar()
            cooldown_var = tk.StringVar()
            stat_box = ttk.Combobox(effects, textvariable=stat_var, state="readonly")
            stat_box.grid(row=row + 1, column=0, sticky="ew", padx=6, pady=5)
            ttk.Entry(effects, textvariable=value_var, width=10).grid(row=row + 1, column=1, sticky="ew", padx=6, pady=5)
            passive_box = ttk.Checkbutton(effects, variable=passive_var)
            passive_box.grid(row=row + 1, column=2, sticky="w", padx=6, pady=5)
            duration_entry = ttk.Entry(effects, textvariable=duration_var, width=10)
            duration_entry.grid(row=row + 1, column=3, sticky="ew", padx=6, pady=5)
            cooldown_entry = ttk.Entry(effects, textvariable=cooldown_var, width=10)
            cooldown_entry.grid(row=row + 1, column=4, sticky="ew", padx=6, pady=5)
            self.effect_rows.append(
                {
                    "stat": stat_var,
                    "value": value_var,
                    "passive": passive_var,
                    "duration": duration_var,
                    "cooldown": cooldown_var,
                    "stat_box": stat_box,
                    "passive_box": passive_box,
                    "duration_entry": duration_entry,
                    "cooldown_entry": cooldown_entry,
                }
            )

        actions = ttk.Frame(form)
        actions.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Сохранить расходник", command=self.save_item).pack(side="left")
        ttk.Button(actions, text="Очистить форму", command=self.new_item).pack(side="left", padx=(8, 0))

    def open_json(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if path:
            self.load_json(Path(path))

    def load_json(self, path: Path) -> None:
        self.json_path = path
        if path.exists():
            try:
                self.catalog = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                messagebox.showerror("Ошибка", f"Не удалось открыть JSON:\n{exc}")
                self.catalog = {"version": 1, "items": []}
        else:
            self.catalog = {"version": 1, "items": []}
        self.catalog.setdefault("version", 1)
        self.catalog.setdefault("items", [])
        self.refresh_tree()
        self.new_item()

    def save_json(self) -> None:
        try:
            self.json_path.parent.mkdir(parents=True, exist_ok=True)
            self.json_path.write_text(json.dumps(self.catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Ошибка", f"Не удалось сохранить JSON:\n{exc}")
            return
        messagebox.showinfo("Готово", "JSON сохранен")

    def refresh_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for index, item in enumerate(self.catalog.get("items", [])):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(TYPE_LABELS.get(item.get("type"), item.get("type", "")), item.get("name", ""), effect_summary(item)),
            )

    def new_item(self) -> None:
        self.selected_index = None
        self.type_var.set(TYPE_LABELS["potion"])
        self.id_var.set("")
        self.name_var.set("")
        self.icon_var.set("")
        for row in self.effect_rows:
            row["stat"].set("")
            row["value"].set("")
            row["passive"].set(False)
            row["duration"].set("")
            row["cooldown"].set("")
        self.update_effect_stat_lists()
        self.tree.selection_remove(self.tree.selection())

    def on_select(self, _event: tk.Event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_index = int(selected[0])
        item = self.catalog["items"][self.selected_index]
        self.type_var.set(TYPE_LABELS.get(item.get("type"), TYPE_LABELS["potion"]))
        self.id_var.set(str(item.get("id", "")))
        self.name_var.set(str(item.get("name", "")))
        self.icon_var.set(str(item.get("icon", "")))
        self.update_effect_stat_lists()
        effects = item.get("effects", [])
        for index, row in enumerate(self.effect_rows):
            effect = effects[index] if index < len(effects) else {}
            row["stat"].set(STAT_LABELS.get(effect.get("stat"), ""))
            row["value"].set(str(effect.get("value", "")) if effect else "")
            row["passive"].set(bool(effect.get("passive", False)))
            row["duration"].set(str(effect.get("duration", "")) if effect.get("duration", 0) else "")
            row["cooldown"].set(str(effect.get("cooldown", "")) if effect.get("cooldown", 0) else "")

    def update_effect_stat_lists(self) -> None:
        item_type = LABEL_TYPES.get(self.type_var.get(), "potion")
        values = [STAT_LABELS[key] for key in ALLOWED_STATS[item_type]]
        is_pet = item_type == "pet"
        for row in self.effect_rows:
            row["stat_box"]["values"] = values
            if row["stat"].get() and row["stat"].get() not in values:
                row["stat"].set("")
            state = "normal" if is_pet else "disabled"
            row["passive_box"].configure(state=state)
            row["duration_entry"].configure(state=state)
            row["cooldown_entry"].configure(state=state)
            if not is_pet:
                row["passive"].set(False)
                row["duration"].set("")
                row["cooldown"].set("")

    def choose_icon(self) -> None:
        source = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.ico"), ("All files", "*.*")]
        )
        if not source:
            return
        source_path = Path(source)
        ICON_DIR.mkdir(parents=True, exist_ok=True)
        target = ICON_DIR / source_path.name
        if target.exists() and source_path.resolve() != target.resolve():
            target = ICON_DIR / f"{source_path.stem}_{uuid4().hex[:6]}{source_path.suffix}"
        try:
            if source_path.resolve() != target.resolve():
                shutil.copy2(source_path, target)
        except OSError as exc:
            messagebox.showerror("Ошибка", f"Не удалось скопировать иконку:\n{exc}")
            return
        self.icon_var.set(f"consumables/{target.name}")

    def save_item(self) -> None:
        item_type = LABEL_TYPES.get(self.type_var.get(), "potion")
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название расходника")
            return
        item_id = self.id_var.get().strip() or slugify(name)
        effects = self.collect_effects(item_type)
        if effects is None:
            return
        duplicate = next(
            (
                index
                for index, item in enumerate(self.catalog.get("items", []))
                if item.get("id") == item_id and index != self.selected_index
            ),
            None,
        )
        if duplicate is not None:
            messagebox.showerror("Ошибка", "Расходник с таким ID уже есть")
            return
        item = {
            "id": item_id,
            "type": item_type,
            "name": name,
            "icon": self.icon_var.get().strip(),
            "effects": effects,
        }
        if self.selected_index is None:
            self.catalog["items"].append(item)
            self.selected_index = len(self.catalog["items"]) - 1
        else:
            self.catalog["items"][self.selected_index] = item
        self.id_var.set(item_id)
        self.refresh_tree()
        self.tree.selection_set(str(self.selected_index))

    def collect_effects(self, item_type: str) -> list[dict] | None:
        effects = []
        for row in self.effect_rows:
            stat_label = row["stat"].get()
            value_text = row["value"].get().strip().replace(",", ".")
            if not stat_label and not value_text:
                continue
            stat = LABEL_STATS.get(stat_label)
            if not stat or stat not in ALLOWED_STATS[item_type]:
                messagebox.showerror("Ошибка", "Выберите допустимую характеристику")
                return None
            try:
                value = float(value_text)
            except ValueError:
                messagebox.showerror("Ошибка", "Значение характеристики должно быть числом")
                return None
            effect = {"stat": stat, "value": value}
            if item_type == "pet":
                passive = bool(row["passive"].get())
                effect["passive"] = passive
                if not passive:
                    try:
                        duration = float(row["duration"].get().strip().replace(",", "."))
                        cooldown = float(row["cooldown"].get().strip().replace(",", "."))
                    except ValueError:
                        messagebox.showerror("Ошибка", "Для временного бонуса питомца нужны время и перезарядка")
                        return None
                    if duration <= 0 or cooldown <= 0:
                        messagebox.showerror("Ошибка", "Время и перезарядка должны быть больше нуля")
                        return None
                    effect["duration"] = duration
                    effect["cooldown"] = cooldown
            effects.append(effect)
        if not 1 <= len(effects) <= 4:
            messagebox.showerror("Ошибка", "У расходника должно быть от 1 до 4 характеристик")
            return None
        return effects

    def delete_item(self) -> None:
        if self.selected_index is None:
            return
        item = self.catalog["items"][self.selected_index]
        if not messagebox.askyesno("Удалить", f"Удалить {item.get('name', '')}?"):
            return
        del self.catalog["items"][self.selected_index]
        self.refresh_tree()
        self.new_item()


def main() -> None:
    root = tk.Tk()
    try:
        root.iconbitmap(str(ROOT_DIR / "app" / "static" / "icons" / "other" / "BeastAwakening.ico"))
    except tk.TclError:
        pass
    ConsumablesEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
