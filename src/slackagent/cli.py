import asyncio
from typing import Annotated

import typer
from dotenv import find_dotenv
from dotenv import load_dotenv

from .bot import init_slack_app
from .config import BotConfig


def run(config_file: Annotated[str, typer.Option("-c", "--config-file")] = "mcp_servers.json") -> None:
    load_dotenv(find_dotenv(), override=True)

    config = BotConfig.from_json(config_file)
    asyncio.run(init_slack_app(config))


def main() -> None:
    typer.run(run)
