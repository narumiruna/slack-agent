from __future__ import annotations

import os
from typing import Any
from typing import cast

from agents import Agent
from agents import ModelSettings
from agents import OpenAIResponsesModel
from agents import Runner
from agents.mcp import MCPServer
from agents.mcp import MCPServerStdio
from agents.mcp import MCPServerStdioParams
from loguru import logger
from openai import AsyncOpenAI
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_bolt.context.say.async_say import AsyncSay
from slack_sdk.web.async_client import AsyncWebClient

from .cache import get_cache_from_env
from .config import MCPServerConfig
from .utils import remove_tool_messages


class Bot:
    @classmethod
    def from_conifg(cls, config: MCPServerConfig) -> Bot:
        mcp_servers: list[MCPServer] = []
        for name, params in config.mcp_servers.items():
            if params.env is not None:
                for k, v in params.env.items():
                    params.env[k] = os.getenv(k, v)

            mcp_servers.append(
                MCPServerStdio(
                    params=cast(MCPServerStdioParams, params.model_dump()),
                    cache_tools_list=config.cache_tools_list,
                    name=name,
                    client_session_timeout_seconds=config.client_session_timeout_seconds,
                )
            )
        return cls(mcp_servers)

    def __init__(self, mcp_servers: list[MCPServer]) -> None:
        self.agent = Agent(
            name="slack-agent",
            instructions="You are a Slack agent.",
            model=OpenAIResponsesModel(
                model="gpt-4o",
                openai_client=AsyncOpenAI(),
            ),
            model_settings=ModelSettings(temperature=0.0),
            mcp_servers=mcp_servers,
        )
        self.cache = get_cache_from_env()

    async def connect(self) -> None:
        for server in self.agent.mcp_servers:
            await server.connect()

    async def cleanup(self) -> None:
        for server in self.agent.mcp_servers:
            await server.cleanup()

    async def handle_app_mention(self, body: dict[str, Any], say: AsyncSay, client: AsyncWebClient) -> None:
        logger.info("type of client: {}", type(client))
        logger.info(f"Received event: {body}")

        event = cast(dict[str, str], body.get("event", {}))
        if not event:
            return

        text = event.get("text", "")
        if not text:
            return
        logger.info(f"Received message: {text}")

        channel = event.get("channel", "")
        if not channel:
            return

        key = f"slack:bot:{channel}"
        messages = await self.cache.get(key)
        if messages is None:
            messages = []

        messages.append({"role": "user", "content": text})

        result = await Runner.run(self.agent, input=messages)
        messages = result.to_input_list()
        await say(result.final_output)

        await self.cache.set(key, remove_tool_messages(messages))


async def init_slack_app(config: MCPServerConfig) -> None:
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        raise ValueError("SLACK_BOT_TOKEN is not set")

    app_token = os.getenv("SLACK_APP_TOKEN")
    if not app_token:
        raise ValueError("SLACK_APP_TOKEN is not set")

    bot = Bot.from_conifg(config)

    app = AsyncApp(token=bot_token)
    app.event("app_mention")(bot.handle_app_mention)

    handler = AsyncSocketModeHandler(app=app, app_token=app_token)

    try:
        await bot.connect()
        await handler.start_async()
    finally:
        await handler.close_async()
        await bot.cleanup()
