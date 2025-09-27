from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
DATA_ROOT = Path(os.environ.get("DATA_ROOT", DEFAULT_DATA_ROOT))


def load_json(name: str) -> Any:
    path = DATA_ROOT / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def persist_json(name: str, payload: Any) -> None:
    path = DATA_ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
