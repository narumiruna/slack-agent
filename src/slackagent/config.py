from __future__ import annotations

import json
from pathlib import Path

from mcp import StdioServerParameters
from pydantic import BaseModel


class BotConfig(BaseModel):
    mcp_servers: dict[str, StdioServerParameters] = []
    client_session_timeout_seconds: float = 10.0

    @classmethod
    def from_json(cls, f: str | Path) -> BotConfig:
        path = Path(f)
        if path.suffix != ".json":
            raise ValueError(f"File {path} is not a JSON file")

        with path.open() as fp:
            data = json.load(fp)

        return cls.model_validate(data)
