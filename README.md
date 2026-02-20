# FlagGuessr

Desktop game in Python/Pygame where you guess the country from its flag.

## Requirements

- Python 3.10+
- `pip`

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Run

```bash
python3 main.py
```

## Test

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Notes:
- `tests/test_ui_smoke.py` runs only if `pygame` is installed.
- Core tests do not require a graphical environment.

## Build (PyInstaller)

```bash
python3 build.py
```

This bundles the app from `main.py`, collects all submodules under `flagguessr`, and includes assets from `data/`.

If PyInstaller is missing, `build.py` exits with a clear message. You can install it with:

```bash
python3 -m pip install pyinstaller
```

## Project Architecture

The project is refactored into layers under `flagguessr/`:

- `flagguessr/domain/`: entities and game rules
- `flagguessr/application/`: use cases and ports
- `flagguessr/infrastructure/`: SQLite/audio/asset adapters
- `flagguessr/presentation/`: controller, state machine, and UI
- `flagguessr/app/`: bootstrap and wiring
- `flagguessr/shared/`: shared path utilities

Patterns used:
- State Pattern for screens/flow
- Strategy Pattern for game modes
- Repository Pattern for persistence

## Assets and Data

- Runtime SQLite databases are created in the user data directory (`get_user_data_path(...)`): `scores.db`, `flags.db`.
- Static assets (flags/music/fonts/icon) are loaded from `data/`.
