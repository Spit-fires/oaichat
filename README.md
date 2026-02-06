# oaichat

A beautiful CLI for testing and interacting with OpenAI-compatible chat APIs.

## Features

- 🎨 **Beautiful CLI** with Rich-powered formatting and markdown rendering
- 🔌 **Multi-provider support** - OpenAI, Ollama, Groq, Together AI, LM Studio, and more
- 💾 **Persistent conversations** - Resume chats anytime with SQLite storage
- 🎯 **Named profiles** - Easily switch between different API providers
- 🌊 **Streaming responses** - See tokens as they arrive (or wait for complete responses)
- 📊 **Token usage tracking** - Monitor your API usage
- 🎭 **System prompts** - Customize model behavior per profile or conversation
- 📤 **Export conversations** - Save to JSON or Markdown
- 🤖 **Auto-generated titles** - Conversations name themselves

## Installation

```bash
pip install oaichat
```

Or install from source:

```bash
git clone https://github.com/yourusername/oaichat.git
cd oaichat
pip install -e .
```

## Quick Start

### 1. Add a profile

```bash
# OpenAI
oaichat profile add openai --base-url https://api.openai.com/v1 --api-key sk-... --model gpt-4o

# Ollama (local)
oaichat profile add ollama --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# Groq
oaichat profile add groq --base-url https://api.groq.com/openai/v1 --api-key gsk-... --model llama-3.1-70b-versatile
```

### 2. Chat!

```bash
# Start an interactive chat session
oaichat chat

# Send a one-off message
oaichat send "Explain quantum computing in simple terms"

# Use a specific profile and model
oaichat chat --profile ollama --model llama3
```

### 3. Manage conversations

```bash
# List all conversations
oaichat convo list

# Resume a previous conversation
oaichat convo resume <conversation-id>

# Export to markdown
oaichat convo export <conversation-id> --format md
```

## Commands

### Profile Management

```bash
oaichat profile add <name>           # Add a new API profile
oaichat profile list                 # List all profiles
oaichat profile show <name>          # Show profile details
oaichat profile set-default <name>   # Set default profile
oaichat profile remove <name>        # Remove a profile
```

### Model Management

```bash
oaichat model list                   # List available models from current profile
oaichat model list --profile <name>  # List models from specific profile
oaichat model set <model-name>       # Set default model for current profile
```

### Chatting

```bash
oaichat chat                         # Start interactive chat
oaichat chat --profile <name>        # Use specific profile
oaichat chat --model <name>          # Use specific model
oaichat chat --system "You are..."   # Set system prompt
oaichat chat --temperature 0.7       # Set temperature
oaichat chat --max-tokens 2000       # Set max tokens
oaichat chat --no-stream             # Wait for complete response

oaichat send "message"               # Send one-off message
oaichat send "message" --save        # Save one-off message to history
```

### Interactive Chat Commands

While in an interactive chat session:

- `/exit` - Exit the chat
- `/clear` - Clear conversation history (start fresh)
- `/system <prompt>` - Change system prompt
- `/model <name>` - Switch model
- `/save` - Force save and generate title
- `/usage` - Show session token usage

### Conversation Management

```bash
oaichat convo list                   # List all conversations
oaichat convo list --profile <name>  # Filter by profile
oaichat convo list --limit 50        # Show more conversations
oaichat convo show <id>              # Display full conversation
oaichat convo resume <id>            # Resume interactive chat
oaichat convo delete <id>            # Delete conversation
oaichat convo export <id> --format json  # Export to JSON
oaichat convo export <id> --format md    # Export to Markdown
```

## Configuration

Profiles and settings are stored in your platform's app directory:
- **Linux**: `~/.config/oaichat/`
- **macOS**: `~/Library/Application Support/oaichat/`
- **Windows**: `%APPDATA%\oaichat\`

### Environment Variables

Override profile settings with environment variables:

```bash
export OAICHAT_API_KEY=sk-...
export OAICHAT_BASE_URL=https://api.openai.com/v1
export OAICHAT_MODEL=gpt-4o
```

## Supported Providers

oaichat works with any OpenAI-compatible API:

| Provider | Base URL | Notes |
|----------|----------|-------|
| OpenAI | `https://api.openai.com/v1` | Requires API key |
| Ollama | `http://localhost:11434/v1` | Local, free |
| LM Studio | `http://localhost:1234/v1` | Local, free |
| Groq | `https://api.groq.com/openai/v1` | Requires API key |
| Together AI | `https://api.together.xyz/v1` | Requires API key |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or PR.
