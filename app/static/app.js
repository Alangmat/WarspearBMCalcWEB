const tabs = [
  { id: "skills", title: "Навыки" },
  { id: "stats", title: "Характеристики" },
  { id: "mods", title: "Модификаторы" },
  { id: "gear", title: "Экипировка" },
  { id: "talents", title: "Таланты" },
];

let state = null;
let activeTab = "skills";
let calculateTimer = null;

const icon = (path) => `/static/icons/${path}`;

const skillMeta = {
  moon_touch: { icon: "base/MoonTouchFramed.png", title: "Лунное касание", activePath: "skills.moon_touch.active", levelPath: "skills.moon_touch.level", maxLevel: 5 },
  beast_awakening: { icon: "base/BeastAwakeningFramed.png", title: "Пробуждение зверя", activePath: "skills.beast_awakening.active", levelPath: "skills.beast_awakening.level", maxLevel: 5 },
  order_to_attack: { icon: "base/OrderToAttackFramed.png", title: "Приказ к атаке", activePath: "skills.order_to_attack.active", levelPath: "skills.order_to_attack.level", maxLevel: 5 },
  chain_lightning: { icon: "base/ChainLightningFramed.png", title: "Цепная молния", activePath: "skills.chain_lightning.active", levelPath: "skills.chain_lightning.level", maxLevel: 5 },
  bestial_rampage: { icon: "expert/BestialRampageFramed.png", title: "Звериное буйство", activePath: "skills.bestial_rampage.active", levelPath: "skills.bestial_rampage.level", maxLevel: 4 },
  aura_of_the_forest: { icon: "expert/AuraOfTheForestFramed.png", title: "Аура леса", activePath: "skills.aura_of_the_forest.active", levelPath: "skills.aura_of_the_forest.level", maxLevel: 4 },
  moonlight: { icon: "expert/MoonlightFramed.png", title: "Лунный свет", levelPath: "skills.moonlight.level", maxLevel: 4 },
  blessing_of_the_moon: { icon: "expert/BlessingOfTheMoonFramed.png", title: "Благословение луны", activePath: "skills.blessing_of_the_moon.active", levelPath: "skills.blessing_of_the_moon.level", maxLevel: 4 },
  double_concentration: { icon: "expert/DoubleConcentrationFramed.png", title: "Двойная концентрация", activePath: "skills.double_concentration.active", levelPath: "skills.double_concentration.level", maxLevel: 4 },
};

const weaponOptions = [
  ["mace", "Булава", "weapons/mace.png"],
  ["staff", "Посох", "weapons/staff.png"],
  ["spear", "Копье", "weapons/spear.png"],
  ["sword", "Меч", "weapons/sword.png"],
  ["axe", "Топор", "weapons/axe.png"],
];

const amuletOptions = [
  ["none", "0%", "amulets/empty.png"],
  ["magic6", "6% маг", "amulets/6mdd.png"],
  ["magic10", "10% маг", "amulets/10mdd.png"],
  ["magic15", "15% маг", "amulets/15mdd.png"],
  ["physical4", "4% физ", "amulets/4pdd.png"],
  ["physical7", "7% физ", "amulets/7pdd.png"],
];

const cloakOptions = [
  ["none", "0%", "cloaks/empty.png"],
  ["magic5", "5% маг", "cloaks/5mdd.png"],
  ["magic10", "10% маг", "cloaks/10mdd.png"],
  ["magic15", "15% маг", "cloaks/15mdd.png"],
  ["physical4", "4% физ", "cloaks/4pdd.png"],
  ["physical7", "7% физ", "cloaks/7pdd.png"],
];

const ringOptions = [
  ["none", "0%", "rings/empty.png"],
  ["magic5", "5% маг", "rings/5mdd.png"],
  ["magic9", "9% маг", "rings/9mdd.png"],
  ["magic10", "10% маг", "rings/10mdd.png"],
  ["physical3", "3% физ", "rings/3pdd.png"],
  ["physical6", "6% физ", "rings/6pdd.png"],
];

const braceletOptions = [
  ["none", "0%", "bracelets/empty.png"],
  ["magic6", "6% маг", "bracelets/6mdd.png"],
  ["magic7_5", "7.5% маг", "bracelets/7.5mdd.png"],
  ["physical4", "4% физ", "bracelets/4pdd.png"],
  ["physical5", "5% физ", "bracelets/5pdd.png"],
];

const setOptions = [
  ["none", "0%", "set/empty.png"],
  ["magic12", "12% маг", "set/12mdd.png"],
  ["physical8", "8% физ", "set/8pdd.png"],
];

const castleOptions = [
  ["empty", "Без замка | 0%"],
  ["first", "1 сектор | 5%"],
  ["second", "2 сектор | 7.5%"],
  ["third", "3 сектор | 10%"],
  ["fourth", "4 сектор | 12.5%"],
  ["fifth", "5 сектор | 15%"],
];

const statIcons = {
  "stats.main.magical_damage": "stats/mdd.png",
  "stats.main.physical_damage": "stats/pdd.png",
  "stats.main.skill_cooldown": "stats/SkillCooldown.png",
  "stats.main.attack_speed": "stats/AttackSpeed.png",
  "stats.main.critical_hit": "stats/CriticalHit.png",
  "stats.main.critical_damage": "stats/CriticalDamage.png",
  "stats.main.penetration": "stats/Penetration.png",
  "stats.main.accuracy": "stats/Accuracy.png",
  "stats.main.attack_strength": "stats/AttackStrength.png",
  "stats.main.piercing_attack": "stats/PiercingAttack.png",
  "stats.main.rage": "stats/Rage.png",
  "stats.main.facilitation": "stats/Facilitation.png",
  "stats.main.skill_power": "stats/SkillPower.png",
  "stats.main.depths_fury": "stats/DepthsFury.png",
  "stats.main.protection": "stats/Protection.png",
  "stats.main.dodge": "stats/Dodge.png",
  "stats.main.resilience": "stats/Resilience.png",
};

const statIconByName = {
  magical_damage: "stats/mdd.png",
  physical_damage: "stats/pdd.png",
  skill_cooldown: "stats/SkillCooldown.png",
  attack_speed: "stats/AttackSpeed.png",
  critical_hit: "stats/CriticalHit.png",
  critical_damage: "stats/CriticalDamage.png",
  penetration: "stats/Penetration.png",
  accuracy: "stats/Accuracy.png",
  attack_strength: "stats/AttackStrength.png",
  piercing_attack: "stats/PiercingAttack.png",
  rage: "stats/Rage.png",
  facilitation: "stats/Facilitation.png",
  skill_power: "stats/SkillPower.png",
  depths_fury: "stats/DepthsFury.png",
  protection: "stats/Protection.png",
  dodge: "stats/Dodge.png",
  resilience: "stats/Resilience.png",
};

const finalStatIcons = {
  skill_cooldown: "stats/SkillCooldown.png",
  attack_speed: "stats/AttackSpeed.png",
  critical_hit_hero: "stats/CriticalHit.png",
  critical_hit_luna: "stats/CriticalHit.png",
  critical_damage_hero: "stats/CriticalDamage.png",
  critical_damage_luna: "stats/CriticalDamage.png",
  penetration_hero: "stats/Penetration.png",
  penetration_luna: "stats/Penetration.png",
  accuracy_hero: "stats/Accuracy.png",
  accuracy_luna: "stats/Accuracy.png",
  attack_strength_hero: "stats/AttackStrength.png",
  attack_strength_luna: "stats/AttackStrength.png",
  piercing_attack: "stats/PiercingAttack.png",
  rage: "stats/Rage.png",
  facilitation_hero: "stats/Facilitation.png",
  facilitation_luna: "stats/Facilitation.png",
  skill_power: "stats/SkillPower.png",
  depths_fury: "stats/DepthsFury.png",
  effective_magical_damage: "stats/mdd.png",
  effective_physical_damage: "stats/pdd.png",
};

const limits = {
  "skills.moon_touch.level": [1, 5],
  "skills.beast_awakening.level": [1, 5],
  "skills.beast_awakening.talent_physical_level": [0, 3],
  "skills.order_to_attack.level": [1, 5],
  "skills.order_to_attack.talent_dual_rage_level": [0, 3],
  "skills.order_to_attack.talent_guardian_unity_level": [0, 3],
  "skills.chain_lightning.level": [1, 5],
  "skills.bestial_rampage.level": [1, 4],
  "skills.aura_of_the_forest.level": [1, 4],
  "skills.moonlight.level": [1, 4],
  "skills.moonlight.talent_level": [0, 3],
  "skills.blessing_of_the_moon.level": [1, 4],
  "skills.double_concentration.level": [1, 4],
  "mods.dragon_eye_level": [0, 4],
  "talents.bestial_rage_level": [0, 3],
  "talents.predatory_delirium_level": [0, 3],
  "talents.animal_rage_level": [0, 3],
  "talents.moment_of_power_level": [0, 4],
  "talents.long_death_level": [0, 4],
  "talents.continuous_fury_level": [0, 3],
};

function get(path) {
  return path.split(".").reduce((acc, key) => acc?.[key], state);
}

function set(path, value) {
  const keys = path.split(".");
  let node = state;
  for (const key of keys.slice(0, -1)) node = node[key];
  node[keys.at(-1)] = value;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function image(src, className = "") {
  const img = el("img", className);
  img.src = icon(src);
  img.alt = "";
  return img;
}

function levelIconPath(value, max) {
  if (value <= 0) return null;
  return `numbers/${value}.${max}.png`;
}

function iconWithLevel(iconPath, className, levelPath, maxLevel) {
  const wrap = el("span", `leveled-icon ${className || ""}`.trim());
  wrap.append(image(iconPath, "base-icon"));
  if (levelPath && maxLevel) {
    const value = Number(get(levelPath) || 0);
    const badgePath = levelIconPath(value, maxLevel);
    if (badgePath) wrap.append(image(badgePath, "level-badge"));
  }
  return wrap;
}

function clearBranchTalents(branch) {
  if (branch === "guardian") {
    set("skills.order_to_attack.talent_guardian_unity_level", 0);
    set("skills.blessing_of_the_moon.talent_plus_penetration", false);
    set("talents.harmonious_power", false);
  }
  if (branch === "dual") {
    set("skills.bestial_rampage.talent", false);
    set("skills.beast_awakening.talent_physical_level", 0);
    set("skills.double_concentration.talent_deadly_dexterity", false);
    set("skills.order_to_attack.talent_dual_rage_level", 0);
    set("skills.blessing_of_the_moon.talent_plus_critical_hit", false);
    set("talents.symbiosis", false);
  }
  if (branch === "forest") {
    set("skills.moonlight.talent_level", 0);
    set("skills.beast_awakening.talent_mage", false);
    set("skills.aura_of_the_forest.talent_grandeur_of_lotus", false);
    set("skills.aura_of_the_forest.talent_abuse", false);
  }
}

function sanitizeState() {
  const activeBranches = [
    ["dual", "talents.dual_rage_active"],
    ["forest", "talents.forest_inspiration_active"],
    ["guardian", "talents.guardian_unity_active"],
  ].filter(([, path]) => Boolean(get(path)));
  const keep = activeBranches.length ? activeBranches[0][0] : null;
  for (const [branch, path] of [
    ["guardian", "talents.guardian_unity_active"],
    ["dual", "talents.dual_rage_active"],
    ["forest", "talents.forest_inspiration_active"],
  ]) {
    const active = branch === keep;
    set(path, active);
    if (!active) clearBranchTalents(branch);
  }
  if (!get("skills.aura_of_the_forest.talent_grandeur_of_lotus")) {
    set("skills.aura_of_the_forest.talent_abuse", false);
  }
  if (get("mods.roar_talent_almahad") && get("mods.predatory_bond_talent_almahad")) {
    set("mods.predatory_bond_talent_almahad", false);
  }
}

function selectBranch(branch) {
  const paths = {
    guardian: "talents.guardian_unity_active",
    dual: "talents.dual_rage_active",
    forest: "talents.forest_inspiration_active",
  };
  const shouldActivate = !get(paths[branch]);
  for (const key of Object.keys(paths)) {
    set(paths[key], key === branch && shouldActivate);
    if (key !== branch || !shouldActivate) clearBranchTalents(key);
  }
  render();
  scheduleCalculate();
}

function section(title, children, className = "") {
  const node = el("section", `form-section ${className}`.trim());
  node.append(el("h2", null, title));
  const body = el("div", "fields");
  body.append(...children);
  node.append(body);
  return node;
}

function numberField(path, label, opts = {}) {
  const wrap = el("label", `field number-field ${opts.full ? "full" : ""}`.trim());
  const caption = el("span", "field-label");
  const statIcon = opts.icon || statIcons[path] || statIconByName[path.split(".").at(-1)];
  if (statIcon) caption.append(image(statIcon, "label-icon"));
  caption.append(el("span", null, label));
  wrap.append(caption);

  const input = el("input");
  input.type = "number";
  input.step = opts.step || "0.1";
  input.min = opts.min ?? 0;
  input.inputMode = "decimal";
  input.size = 5;
  input.value = get(path);
  input.addEventListener("input", () => {
    set(path, Number(input.value || 0));
    scheduleCalculate();
  });
  wrap.append(input);
  return wrap;
}

function selectField(path, label, options, opts = {}) {
  const wrap = el("label", `field ${opts.full ? "full" : ""}`.trim());
  wrap.append(el("span", "field-label", label));
  const select = el("select");
  for (const [value, text] of options) {
    const option = el("option", null, text);
    option.value = value;
    select.append(option);
  }
  select.value = get(path);
  select.addEventListener("change", () => {
    set(path, select.value);
    scheduleCalculate();
  });
  wrap.append(select);
  return wrap;
}

function toggle(path, label, opts = {}) {
  const wrap = el("button", `toggle-line ${opts.full ? "full" : ""}`.trim());
  wrap.type = "button";
  wrap.title = label;
  wrap.disabled = Boolean(opts.disabled);
  wrap.classList.toggle("disabled", wrap.disabled);
  const sync = () => wrap.classList.toggle("on", Boolean(get(path)));
  sync();
  if (opts.icon) wrap.append(image(opts.icon, "toggle-icon"));
  wrap.append(el("span", "toggle-text", label));
  wrap.addEventListener("click", () => {
    if (wrap.disabled) return;
    set(path, !get(path));
    if (opts.exclusiveWith && get(path)) set(opts.exclusiveWith, false);
    if (opts.afterChange) opts.afterChange();
    sync();
    render();
    scheduleCalculate();
  });
  return wrap;
}

function stepper(path, label, min, max, opts = {}) {
  limits[path] = [min, max];
  const wrap = el("div", `step-field ${opts.full ? "full" : ""}`.trim());
  const caption = el("span", "field-label");
  if (opts.icon) caption.append(image(opts.icon, "label-icon"));
  caption.append(el("span", null, label));
  wrap.append(caption);

  const controls = el("div", `stepper icon-stepper ${opts.showValue ? "with-value" : ""}`.trim());
  const minus = el("button", "step-button");
  minus.type = "button";
  minus.title = "Уменьшить";
  minus.append(image("buttons/minus.png"));
  const display = el("div", "level-display");
  const plus = el("button", "step-button");
  plus.type = "button";
  plus.title = "Увеличить";
  plus.append(image("buttons/plus.png"));
  const maxButton = el("button", "step-button step-max", "MAX");
  maxButton.type = "button";
  maxButton.title = "Максимальный уровень";

  const sync = (value) => {
    const next = Math.round(Math.min(Math.max(Number(value || min), min), max));
    set(path, next);
    minus.disabled = Boolean(opts.disabled) || next <= min;
    plus.disabled = Boolean(opts.disabled) || next >= max;
    maxButton.disabled = Boolean(opts.disabled) || next >= max;
    display.textContent = opts.format ? opts.format(next, max) : `${next}/${max}`;
  };

  const commit = (value) => {
    const next = Math.round(Math.min(Math.max(Number(value || min), min), max));
    sync(next);
    if (opts.afterChange) opts.afterChange(next);
    render();
    scheduleCalculate();
  };

  minus.addEventListener("click", () => commit(Number(get(path)) - 1));
  plus.addEventListener("click", () => commit(Number(get(path)) + 1));
  maxButton.addEventListener("click", () => commit(max));
  sync(get(path));
  if (opts.showValue) controls.append(minus, display, plus, maxButton);
  else controls.append(minus, plus, maxButton);
  wrap.append(controls);
  return wrap;
}

function iconToggle(path, iconPath, title, opts = {}) {
  const button = el("button", `icon-toggle ${opts.className || ""}`.trim());
  button.type = "button";
  button.title = title;
  button.disabled = Boolean(opts.disabled);
  button.append(iconWithLevel(iconPath, "", opts.levelPath, opts.maxLevel));
  const sync = () => button.classList.toggle("active", Boolean(get(path)));
  sync();
  button.addEventListener("click", () => {
    if (button.disabled) return;
    set(path, !get(path));
    if (opts.afterChange) opts.afterChange();
    sync();
    render();
    scheduleCalculate();
  });
  return button;
}

function skillCard(key, controls) {
  const meta = skillMeta[key];
  const node = el("section", "skill-card");
  const header = el("div", "skill-header");
  const left = el("div", "skill-title");
  if (meta.activePath) {
    left.append(iconToggle(meta.activePath, meta.icon, meta.title, { levelPath: meta.levelPath, maxLevel: meta.maxLevel }));
  } else {
    const badge = el("div", "skill-icon-static");
    badge.append(iconWithLevel(meta.icon, "", meta.levelPath, meta.maxLevel));
    left.append(badge);
  }
  left.append(el("h2", null, meta.title));
  header.append(left);
  if (meta.activePath) {
    header.append(el("span", `skill-status ${get(meta.activePath) ? "on" : ""}`, get(meta.activePath) ? "Включено" : "Выключено"));
  }
  const body = el("div", "skill-controls");
  body.append(...controls);
  node.append(header, body);
  return node;
}

function skillGroup(title, cards) {
  const node = el("section", "form-section wide skill-group");
  node.append(el("h2", null, title));
  const body = el("div", "skill-group-grid");
  body.append(...cards);
  node.append(body);
  return node;
}

function weaponSelector() {
  const wrap = el("div", "weapon-grid full");
  for (const [value, title, iconPath] of weaponOptions) {
    const button = el("button", `weapon-option ${get("weapon") === value ? "active" : ""}`);
    button.type = "button";
    button.title = title;
    button.append(image(iconPath), el("span", null, title));
    button.addEventListener("click", () => {
      set("weapon", value);
      render();
      scheduleCalculate();
    });
    wrap.append(button);
  }
  return wrap;
}

function iconChoiceGrid(path, label, options, opts = {}) {
  const wrap = el("div", `choice-field ${opts.full ? "full" : ""}`.trim());
  const caption = el("div", "field-label");
  if (opts.icon) caption.append(image(opts.icon, "label-icon"));
  caption.append(el("span", null, label));
  wrap.append(caption);
  const grid = el("div", `icon-choice-grid ${opts.small ? "small" : ""}`.trim());
  for (const [value, title, iconPath] of options) {
    const button = el("button", `icon-choice ${get(path) === value ? "active" : ""}`);
    button.type = "button";
    button.title = title;
    button.append(image(iconPath), el("span", null, title));
    button.addEventListener("click", () => {
      set(path, value);
      render();
      scheduleCalculate();
    });
    grid.append(button);
  }
  wrap.append(grid);
  return wrap;
}

function equipmentSlot(path, label, slotIcon) {
  const options = [
    ["none", "Пусто", slotIcon],
    ["cloth", "Ткань", "equipments/cloth.png"],
    ["leather", "Кожа", "equipments/leather.png"],
  ];
  const wrap = el("div", "equipment-slot");
  const head = el("div", "equipment-head");
  head.append(image(slotIcon), el("span", null, label));
  wrap.append(head);
  wrap.append(iconChoiceGrid(path, "", options, { small: true }));
  return wrap;
}

function talentToggle(path, label, iconPath, opts = {}) {
  const button = el("button", `talent-card ${get(path) ? "active" : ""}`);
  button.type = "button";
  button.title = label;
  button.disabled = Boolean(opts.disabled);
  button.classList.toggle("disabled", button.disabled);
  button.append(iconWithLevel(iconPath, "talent-icon-wrap"), el("span", "talent-name", label));
  button.addEventListener("click", () => {
    if (button.disabled) return;
    set(path, !get(path));
    if (opts.exclusiveWith && get(path)) set(opts.exclusiveWith, false);
    if (opts.afterChange) opts.afterChange();
    render();
    scheduleCalculate();
  });
  return button;
}

function talentLevel(path, label, iconPath, min, max, opts = {}) {
  const card = el("div", "talent-card level-card");
  card.classList.toggle("active", Number(get(path) || 0) > min);
  card.classList.toggle("disabled", Boolean(opts.disabled));
  card.append(
    iconWithLevel(iconPath, "talent-icon-wrap", path, max),
    el("span", "talent-name", label),
    stepper(path, "Уровень", min, max, { full: true, disabled: opts.disabled })
  );
  return card;
}

function talentBranch(title, branchIcon, activePath, branchKey, children) {
  const active = Boolean(get(activePath));
  const node = el("section", `talent-branch ${active ? "active" : "inactive"}`);
  const head = el("div", "branch-head");
  const button = el("button", `branch-toggle ${active ? "active" : ""}`);
  button.type = "button";
  button.title = title;
  button.append(image(branchIcon));
  button.addEventListener("click", () => selectBranch(branchKey));
  head.append(button, el("h2", null, title));
  node.append(head);
  const grid = el("div", "talent-grid");
  grid.append(...children);
  node.append(grid);
  return node;
}

function talentBranches(branches) {
  const node = el("div", "talent-branches wide");
  node.append(...branches);
  return node;
}

function renderTabs() {
  const nav = document.getElementById("tabs");
  nav.innerHTML = "";
  for (const tab of tabs) {
    const button = el("button", `tab ${tab.id === activeTab ? "active" : ""}`, tab.title);
    button.type = "button";
    button.addEventListener("click", () => {
      activeTab = tab.id;
      render();
    });
    nav.append(button);
  }
}

function renderSkills() {
  return [
    section("Оружие и автоатака", [
      weaponSelector(),
      toggle("skills.attack.active", "Автоатака", { icon: "weapons/mace.png" }),
      toggle("skills.healing.active", "Лечение учитывается в темпе автоатаки", { icon: "base/HealingFramed.png" }),
    ], "wide"),
    skillGroup("Базовые навыки", [
      skillCard("moon_touch", [
        stepper("skills.moon_touch.level", "Уровень", 1, 5),
        toggle("skills.moon_touch.relic", "Реликвия 12%", { icon: "other/Relic12percent.png" }),
      ]),
      skillCard("beast_awakening", [
        stepper("skills.beast_awakening.level", "Уровень", 1, 5),
      ]),
      skillCard("order_to_attack", [
        stepper("skills.order_to_attack.level", "Уровень", 1, 5),
      ]),
      skillCard("chain_lightning", [
        stepper("skills.chain_lightning.level", "Уровень", 1, 5),
        toggle("skills.chain_lightning.relic", "Реликвия 12%", { icon: "other/Relic12percent.png" }),
      ]),
    ]),
    skillGroup("Экспертные навыки", [
      skillCard("bestial_rampage", [
        stepper("skills.bestial_rampage.level", "Уровень", 1, 4),
      ]),
      skillCard("aura_of_the_forest", [
        stepper("skills.aura_of_the_forest.level", "Уровень", 1, 4),
      ]),
      skillCard("moonlight", [
        toggle("skills.moonlight.permanent_active", "Постоянный"),
        toggle("skills.moonlight.non_permanent_active", "Нажимной"),
        stepper("skills.moonlight.level", "Уровень", 1, 4),
      ]),
      skillCard("blessing_of_the_moon", [
        stepper("skills.blessing_of_the_moon.level", "Уровень", 1, 4),
        toggle("skills.blessing_of_the_moon.use_on_luna", "Наложить на Луну"),
      ]),
      skillCard("double_concentration", [
        stepper("skills.double_concentration.level", "Уровень", 1, 4),
      ]),
    ]),
  ];
}

function renderStats() {
  const attackMain = [
    ["stats.main.magical_damage", "Магический урон"],
    ["stats.main.physical_damage", "Физический урон"],
    ["stats.main.skill_cooldown", "Перезарядка навыков"],
    ["stats.main.attack_speed", "Скорость атаки"],
    ["stats.main.critical_hit", "Критический удар"],
    ["stats.main.critical_damage", "Критический урон"],
    ["stats.main.penetration", "Пробивная способность"],
    ["stats.main.accuracy", "Точность"],
    ["stats.main.attack_strength", "Сила атаки"],
    ["stats.main.piercing_attack", "Пронзающая атака"],
    ["stats.main.rage", "Ярость"],
    ["stats.main.facilitation", "Содействие"],
    ["stats.main.skill_power", "Сила навыков"],
    ["stats.main.depths_fury", "Гнев глубин"],
  ];
  const defenseMain = [
    ["stats.main.protection", "Защита цели"],
    ["stats.main.dodge", "Уклонение цели"],
    ["stats.main.resilience", "Устойчивость цели"],
  ];
  const pot = [
    ["stats.pot.skill_cooldown", "Перезарядка навыков"],
    ["stats.pot.attack_speed", "Скорость атаки"],
    ["stats.pot.critical_hit", "Критический удар"],
    ["stats.pot.critical_damage", "Критический урон"],
    ["stats.pot.penetration", "Пробивная способность"],
    ["stats.pot.accuracy", "Точность"],
    ["stats.pot.attack_strength", "Сила атаки"],
    ["stats.pot.piercing_attack", "Пронзающая атака"],
    ["stats.pot.rage", "Ярость"],
    ["stats.pot.facilitation", "Содействие"],
    ["stats.pot.skill_power", "Сила навыков"],
  ];
  const scroll = [
    ["stats.scroll.skill_cooldown", "Перезарядка навыков"],
    ["stats.scroll.attack_speed", "Скорость атаки"],
    ["stats.scroll.critical_hit", "Критический удар"],
    ["stats.scroll.critical_damage", "Критический урон"],
    ["stats.scroll.penetration", "Пробивная способность"],
    ["stats.scroll.accuracy", "Точность"],
    ["stats.scroll.attack_strength", "Сила атаки"],
    ["stats.scroll.piercing_attack", "Пронзающая атака"],
    ["stats.scroll.rage", "Ярость"],
    ["stats.scroll.facilitation", "Содействие"],
    ["stats.scroll.depths_fury", "Гнев глубин"],
  ];
  const pet = [
    ["stats.pet.skill_cooldown", "Перезарядка навыков"],
    ["stats.pet.attack_speed", "Скорость атаки"],
    ["stats.pet.critical_damage", "Критический урон"],
    ["stats.pet.penetration", "Пробивная способность"],
    ["stats.pet.accuracy", "Точность"],
    ["stats.pet.attack_strength", "Сила атаки"],
    ["stats.pet.rage", "Ярость"],
    ["stats.pet.facilitation", "Содействие"],
  ];
  return [
    section("Атакующие характеристики", attackMain.map(([path, label]) => numberField(path, label))),
    section("Защитные характеристики", defenseMain.map(([path, label]) => numberField(path, label))),
    section("Эликсир", pot.map(([path, label]) => numberField(path, label))),
    section("Свиток", scroll.map(([path, label]) => numberField(path, label))),
    section("Пет", pet.map(([path, label]) => numberField(path, label))),
  ];
}

function renderMods() {
  return [
    section("Исходные проценты урона", [
      toggle("start_power_mods.guild_damage", "Гильдия 10%", { icon: "other/GuildDamage.png" }),
      toggle("start_power_mods.talent_damage", "Пассивный талант урона 4.75%", { icon: "talents/PowerAttack.png" }),
      toggle("start_power_mods.castle_damage", "Замок 7.5%", { icon: "castle/CastleSword.png" }),
      toggle("start_power_mods.harmonious_power", "Гармоничная сила до расчета", { icon: "talents/HarmoniousPower.png" }),
      numberField("start_power_mods.additional_mdd", "Дополнительный магический урон %", { icon: "stats/mdd.png" }),
      numberField("start_power_mods.additional_pdd", "Дополнительный физический урон %", { icon: "stats/pdd.png" }),
      selectField("start_power_mods.castle_sector", "Замок навыков", castleOptions, { full: true }),
    ]),
    section("Финальные проценты урона", [
      toggle("final_power_mods.guild_damage", "Гильдия 10%", { icon: "other/GuildDamage.png" }),
      toggle("final_power_mods.talent_damage", "Пассивный талант урона 4.75%", { icon: "talents/PowerAttack.png" }),
      toggle("final_power_mods.castle_damage", "Меч замка", { icon: "castle/CastleSword.png" }),
      numberField("final_power_mods.additional_mdd", "Дополнительный магический урон %", { icon: "stats/mdd.png" }),
      numberField("final_power_mods.additional_pdd", "Дополнительный физический урон %", { icon: "stats/pdd.png" }),
      selectField("final_power_mods.castle_sector", "Замок навыков", castleOptions, { full: true }),
    ]),
    section("Баффы и дебаффы", [
      toggle("mods.crushing_will", "Сокрушительная воля", { icon: "other/CrushingWillFramed.png" }),
      toggle("mods.irreversible_anger", "Необратимый гнев", { icon: "other/IrreversibleAngerFramed.png" }),
      toggle("mods.bp_dungeon", "Боевой пропуск в подземелье", { icon: "other/bp.png" }),
      toggle("mods.sacred_shield_hero", "Сакральный щит паладина на персонажа", { icon: "stats/Protection.png" }),
      toggle("mods.sacred_shield_luna", "Сакральный щит паладина на Луну", { icon: "stats/Protection.png" }),
      toggle("mods.gods_aid_hero", "Крылья жреца на герое", { icon: "other/GodsAid.png" }),
      toggle("mods.gods_aid_luna", "Крылья жреца на Луне", { icon: "other/GodsAid.png" }),
      toggle("mods.counterstand", "Снижение длительности эффектов у босса", { icon: "stats/rbreduction.png" }),
      toggle("mods.priest_active", "Аура жреца", { icon: "classes/priest.png" }),
      toggle("mods.druid_active", "Помощь друида", { icon: "classes/druid.png" }),
      toggle("mods.templar_active", "Благословение храмовника", { icon: "classes/templ.png" }),
      stepper("mods.dragon_eye_level", "Глаз дракона", 0, 4, { icon: "other/dragoneye.png", showValue: true }),
    ]),
  ];
}

function renderGear() {
  return [
    section("Проценты урона с бижутерии", [
      iconChoiceGrid("percents.amulet", "Амулет", amuletOptions, { icon: "amulets/empty.png" }),
      iconChoiceGrid("percents.cloak", "Плащ", cloakOptions, { icon: "cloaks/empty.png" }),
      iconChoiceGrid("percents.ring_left", "Кольцо левое", ringOptions, { icon: "rings/empty.png" }),
      iconChoiceGrid("percents.ring_right", "Кольцо правое", ringOptions, { icon: "rings/empty.png" }),
      iconChoiceGrid("percents.bracelet_left", "Браслет левый", braceletOptions, { icon: "bracelets/empty.png" }),
      iconChoiceGrid("percents.bracelet_right", "Браслет правый", braceletOptions, { icon: "bracelets/empty.png" }),
      iconChoiceGrid("percents.set_bonus", "Сет", setOptions, { icon: "set/empty.png", full: true }),
    ], "wide"),
    section("Шмот для Гармоничной силы", [
      equipmentSlot("equipment.helmet", "Шлем", "equipments/helmet.png"),
      equipmentSlot("equipment.body", "Доспех", "equipments/body.png"),
      equipmentSlot("equipment.gloves", "Перчатки", "equipments/gloves.png"),
      equipmentSlot("equipment.belt", "Пояс", "equipments/belt.png"),
      equipmentSlot("equipment.boots", "Ботинки", "equipments/boots.png"),
    ], "wide equipment-section"),
  ];
}

function renderTalents() {
  const guardianActive = Boolean(get("talents.guardian_unity_active"));
  const dualActive = Boolean(get("talents.dual_rage_active"));
  const forestActive = Boolean(get("talents.forest_inspiration_active"));
  return [
    talentBranches([
      talentBranch("1 ветка: Единство хранителя", "talents/GuardianUnity.png", "talents.guardian_unity_active", "guardian", [
        talentLevel("skills.order_to_attack.talent_guardian_unity_level", "Приказ к атаке +", "talents/OrderToAttackPlusFramed.png", 0, 3, { disabled: !guardianActive }),
        talentToggle("skills.blessing_of_the_moon.talent_plus_penetration", "Благословение луны +", "talents/BlessingOfTheMoonPlus.png", { disabled: !guardianActive }),
        talentToggle("talents.harmonious_power", "Гармония силы", "talents/HarmoniousPowerFramed.png", { disabled: !guardianActive }),
      ]),
      talentBranch("2 ветка: Двойная ярость", "talents/DualRage.png", "talents.dual_rage_active", "dual", [
        talentToggle("skills.bestial_rampage.talent", "Звериное буйство +", "talents/BestialRampagePlusFramed.png", { disabled: !dualActive }),
        talentLevel("skills.beast_awakening.talent_physical_level", "Пробуждение зверя +", "talents/BeastAwakeningPlusFramed.png", 0, 3, { disabled: !dualActive }),
        talentToggle("skills.double_concentration.talent_deadly_dexterity", "Смертельная ловкость", "talents/DeadlyDexterityFramed.png", { disabled: !dualActive }),
        talentLevel("skills.order_to_attack.talent_dual_rage_level", "Приказ к атаке +", "talents/OrderToAttackPlusFramed.png", 0, 3, { disabled: !dualActive }),
        talentToggle("skills.blessing_of_the_moon.talent_plus_critical_hit", "Благословение луны +", "talents/BlessingOfTheMoonPlus.png", { disabled: !dualActive }),
        talentToggle("talents.symbiosis", "Симбиоз", "talents/SymbiosisFramed.png", { disabled: !dualActive }),
      ]),
      talentBranch("3 ветка: Лесное вдохновение", "talents/ForestInspiration.png", "talents.forest_inspiration_active", "forest", [
        talentLevel("skills.moonlight.talent_level", "Лунный свет +", "talents/MoonlightPlusFramed.png", 0, 3, { disabled: !forestActive }),
        talentToggle("skills.beast_awakening.talent_mage", "Пробуждение зверя +", "talents/BeastAwakeningPlusFramed.png", { disabled: !forestActive }),
        talentToggle("skills.aura_of_the_forest.talent_grandeur_of_lotus", "Величие лотоса", "talents/AuraOfTheForestUpgradeFramed.png", { disabled: !forestActive }),
        talentToggle("skills.aura_of_the_forest.talent_abuse", "Абьюз таланта на ауру", "talents/AuraOfTheForestChoiceFramed.png", { disabled: !forestActive || !get("skills.aura_of_the_forest.talent_grandeur_of_lotus") }),
      ]),
    ]),
    section("Базовые и общие таланты", [
      talentToggle("skills.moon_touch.talent_plus", "Лунное касание +", "talents/MoonTouchPlusFramed.png"),
      talentToggle("skills.aura_of_the_forest.talent_power_of_nature", "Могущество природы", "talents/AuraOfTheForestChoiceFramed.png"),
      talentLevel("talents.bestial_rage_level", "Звериная ярость", "talents/BestialRageFramed.png", 0, 3),
      talentLevel("talents.animal_rage_level", "Животный гнев", "talents/AnimalRageFramed.png", 0, 3),
      talentLevel("talents.predatory_delirium_level", "Исступление хищника", "talents/PredatoryDeliriumFramed.png", 0, 3),
      talentLevel("talents.long_death_level", "Долгая смерть", "talents/LongDeathFramed.png", 0, 4),
      talentLevel("talents.moment_of_power_level", "Момент силы", "talents/MomentOfPowerFramed.png", 0, 4),
      talentLevel("talents.continuous_fury_level", "Длительная неистовость", "talents/RageTalent.png", 0, 3),
      talentToggle("mods.blago_talent", "Талант благословения", "talents/blagoTalent.png"),
    ], "wide talent-section"),
    section("Таланты Альмахада", [
      talentToggle("mods.pairing_talent_almahad", "Сопряжение", "talents/almahad/pairing.png"),
      talentToggle("mods.roar_talent_almahad", "Рык хищника", "talents/almahad/roar.png", { exclusiveWith: "mods.predatory_bond_talent_almahad" }),
      talentToggle("mods.predatory_bond_talent_almahad", "Хищный тандем", "talents/almahad/PredatoryBond.png", { exclusiveWith: "mods.roar_talent_almahad" }),
    ], "wide talent-section"),
  ];
}

function render() {
  if (!state) return;
  sanitizeState();
  renderTabs();
  const content = document.getElementById("content");
  content.innerHTML = "";
  const grid = el("div", "section-grid");
  const sections = {
    skills: renderSkills,
    stats: renderStats,
    mods: renderMods,
    gear: renderGear,
    talents: renderTalents,
  }[activeTab]();
  grid.append(...sections);
  content.append(grid);
}

function scheduleCalculate() {
  clearTimeout(calculateTimer);
  calculateTimer = setTimeout(calculate, 120);
}

async function calculate() {
  sanitizeState();
  const response = await fetch("/api/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(state),
  });
  if (!response.ok) return;
  updateResult(await response.json());
}

function format(value) {
  return Number(value || 0).toLocaleString("ru-RU", { maximumFractionDigits: 1 });
}

function updateResult(result) {
  document.getElementById("total-dpm").textContent = format(result.totals.total);
  document.getElementById("hero-dpm").textContent = format(result.totals.hero);
  document.getElementById("luna-dpm").textContent = format(result.totals.luna);

  const breakdown = document.getElementById("breakdown");
  breakdown.innerHTML = "";
  const rows = [
    ["Автоатака", result.skills.attack.dpm],
    ["Лунное касание", result.skills.moon_touch.dpm],
    ["Цепная молния", result.skills.chain_lightning.dpm],
    ["Пробуждение зверя", result.skills.beast_awakening.dpm],
    ["Буйство", result.skills.bestial_rampage.dpm],
    ["Приказ к атаке", result.skills.order_to_attack.dpm],
    ["Аура Луны", result.skills.aura_luna.dpm],
    ["Аура героя", result.skills.aura_hero.dpm],
    ["Лунный свет постоянный", result.skills.moonlight_permanent.dpm],
    ["Лунный свет нажимной", result.skills.moonlight_non_permanent.dpm],
    ["Симбиоз герой", result.skills.symbiosis_hero],
    ["Симбиоз Луна", result.skills.symbiosis_luna],
  ];
  for (const [name, value] of rows.slice().sort((left, right) => Number(right[1] || 0) - Number(left[1] || 0))) {
    const row = el("div", "breakdown-row");
    row.append(el("span", null, name), el("strong", null, format(value)));
    breakdown.append(row);
  }

  const stats = document.getElementById("final-stats");
  stats.innerHTML = "";
  const statRows = [
    ["skill_cooldown", "Перезарядка навыков", result.final_stats.skill_cooldown],
    ["attack_speed", "Скорость атаки", result.final_stats.attack_speed],
    ["critical_hit_hero", "Критический удар героя", result.final_stats.critical_hit_hero],
    ["critical_hit_luna", "Критический удар Луны", result.final_stats.critical_hit_luna],
    ["critical_damage_hero", "Критический урон героя", result.final_stats.critical_damage_hero],
    ["critical_damage_luna", "Критический урон Луны", result.final_stats.critical_damage_luna],
    ["penetration_hero", "Пробивная способность героя", result.final_stats.penetration_hero],
    ["penetration_luna", "Пробивная способность Луны", result.final_stats.penetration_luna],
    ["accuracy_hero", "Точность героя", result.final_stats.accuracy_hero],
    ["accuracy_luna", "Точность Луны", result.final_stats.accuracy_luna],
    ["attack_strength_hero", "Сила атаки героя", result.final_stats.attack_strength_hero],
    ["attack_strength_luna", "Сила атаки Луны", result.final_stats.attack_strength_luna],
    ["piercing_attack", "Пронзающая атака", result.final_stats.piercing_attack],
    ["rage", "Ярость", result.final_stats.rage],
    ["facilitation_hero", "Содействие героя", result.final_stats.facilitation_hero],
    ["facilitation_luna", "Содействие Луны", result.final_stats.facilitation_luna],
    ["skill_power", "Сила навыков", result.final_stats.skill_power],
    ["depths_fury", "Гнев глубин", result.final_stats.depths_fury],
    ["effective_magical_damage", "Итоговый магический урон", result.final_stats.effective_magical_damage],
    ["effective_physical_damage", "Итоговый физический урон", result.final_stats.effective_physical_damage],
  ];
  for (const [key, name, value] of statRows) {
    const row = el("div", "stat-row");
    const label = el("span", "stat-name");
    label.append(image(finalStatIcons[key], "stat-icon"), el("span", null, name));
    row.append(label, el("strong", null, format(value)));
    stats.append(row);
  }
}

async function loadPreset(preset) {
  const response = await fetch("/api/preset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset }),
  });
  state = await response.json();
  sanitizeState();
  render();
  calculate();
}

function downloadJson(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = el("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function exportBuild() {
  sanitizeState();
  const response = await fetch("/api/build/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(state),
  });
  if (!response.ok) return;
  const build = await response.json();
  const cleanName = (build.Name || state.name || "build").replace(/[\\/:*?"<>|]+/g, "_").trim() || "build";
  downloadJson(`${cleanName}.json`, build);
}

async function importBuildFile(file) {
  if (!file) return;
  const text = await file.text();
  const payload = JSON.parse(text);
  const response = await fetch("/api/build/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) return;
  state = await response.json();
  sanitizeState();
  render();
  calculate();
}

document.getElementById("load-default").addEventListener("click", () => loadPreset("default"));
document.getElementById("load-empty").addEventListener("click", () => loadPreset("empty"));
document.getElementById("export-build").addEventListener("click", exportBuild);
document.getElementById("import-build").addEventListener("click", () => document.getElementById("import-file").click());
document.getElementById("import-file").addEventListener("change", (event) => {
  importBuildFile(event.target.files[0]);
  event.target.value = "";
});

loadPreset("default");
