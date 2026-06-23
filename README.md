# Warspear BM Calc

Новый веб-калькулятор ДПМ ловчего.

## Запуск

```powershell
D:\WarspearBMCalc\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

После запуска откройте `http://127.0.0.1:8000`.

## Структура

- `app/domain` - входные модели, близкие к DataSet/Stats/Skills из draw.io.
- `app/services/calculator.py` - чистый расчет ДПМ, перенесенный из старого WPF ViewModel.
- `app/config/skills` - JSON-конфиги навыков из старого проекта.
- `app/config/consumables.json` - база зелий, свитков и питомцев.
- `app/static` - фронт без сборщика, обслуживается FastAPI.

## Редактор расходников

Локально собранный редактор лежит в `D:\WarspearBMCalc\dist\ConsumablesEditor.exe`.
Исходник редактора: `tools/consumables_editor.py`.

Редактор сохраняет расходники в `app/config/consumables.json`, а выбранные иконки копирует в `app/static/icons/consumables`.
