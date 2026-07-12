# Cuinn Bot

A Discord bot powered by AI, built with discord.py and the OpenAI API.

## Development

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

### Setup

```bash
# Install dependencies
uv sync

# Configure environment variables
cp config/config.properties.example config/config.properties
# Edit config/config.properties and add your DISCORD_TOKEN and other settings
```

### Running

```bash
uv run cuinn-bot.py
```

## Deployment

### Docker Build

```bash
docker build -t cuinn-bot:latest .
```

### Kubernetes

The bot is configured to run on Kubernetes. Create a ConfigMap with your environment variables:

```bash
kubectl create configmap cuinn-bot-env --from-file=config/config.properties
```

Then deploy:

```bash
kubectl apply -k .
```

## Configuration

Configuration is managed via `config/config.properties`. The following variables are available:

- `DISCORD_TOKEN` (required): Your Discord bot token
- `MAX_CONTEXT_MESSAGES` (optional, default: 6): Maximum number of context messages to keep in memory
- `WAKE_WINDOW_SECONDS` (optional, default: 180): Time window for the bot to stay active after being mentioned
- `RAMALAMA_URL` (optional, default: `http://127.0.0.1:8080/v1`): URL for the Ramalama API
