# Slack Agent

A simple Slack agent that uses OpenAI's API to respond to messages in a Slack channel.

## Usage

```shell
export OPENAI_API_KEY=
export SLACK_BOT_TOKEN=
export SLACK_APP_TOKEN=

# Use Redis as a cache
export CACHE_URL="redis://localhost:6379/0?pool_max_size=1"

pip install uv
uv sync
uv run slackagent
```
