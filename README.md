# clichat

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
pip install clichat
```

Or install from source:

```bash
git clone https://github.com/yourusername/clichat.git
cd clichat
pip install -e .
```

## Quick Start

### 1. Add a profile

```bash
# OpenAI
clichat profile add openai --base-url https://api.openai.com/v1 --api-key sk-... --model gpt-4o

# Ollama (local)
clichat profile add ollama --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# Groq
clichat profile add groq --base-url https://api.groq.com/openai/v1 --api-key gsk-... --model llama-3.1-70b-versatile
```

### 2. Chat!

```bash
# Start an interactive chat session
clichat chat

# Send a one-off message
clichat send "Explain quantum computing in simple terms"

# Use a specific profile and model
clichat chat --profile ollama --model llama3
```

### 3. Manage conversations

```bash
# List all conversations
clichat convo list

# Resume a previous conversation
clichat convo resume <conversation-id>

# Export to markdown
clichat convo export <conversation-id> --format md
```

## Commands

### Profile Management

```bash
clichat profile add <name>           # Add a new API profile
clichat profile list                 # List all profiles
clichat profile show <name>          # Show profile details
clichat profile set-default <name>   # Set default profile
clichat profile remove <name>        # Remove a profile
```

### Model Management

```bash
clichat model list                   # List available models from current profile
clichat model list --profile <name>  # List models from specific profile
clichat model set <model-name>       # Set default model for current profile
```

### Chatting

```bash
clichat chat                         # Start interactive chat
clichat chat --profile <name>        # Use specific profile
clichat chat --model <name>          # Use specific model
clichat chat --system "You are..."   # Set system prompt
clichat chat --temperature 0.7       # Set temperature
clichat chat --max-tokens 2000       # Set max tokens
clichat chat --no-stream             # Wait for complete response

clichat send "message"               # Send one-off message
clichat send "message" --save        # Save one-off message to history
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
clichat convo list                   # List all conversations
clichat convo list --profile <name>  # Filter by profile
clichat convo list --limit 50        # Show more conversations
clichat convo show <id>              # Display full conversation
clichat convo resume <id>            # Resume interactive chat
clichat convo delete <id>            # Delete conversation
clichat convo export <id> --format json  # Export to JSON
clichat convo export <id> --format md    # Export to Markdown
```

## Configuration

Profiles and settings are stored in your platform's app directory:
- **Linux**: `~/.config/clichat/`
- **macOS**: `~/Library/Application Support/clichat/`
- **Windows**: `%APPDATA%\clichat\`

### Environment Variables

Override profile settings with environment variables:

```bash
export CLICHAT_API_KEY=sk-...
export CLICHAT_BASE_URL=https://api.openai.com/v1
export CLICHAT_MODEL=gpt-4o
```

## Supported Providers

clichat works with any OpenAI-compatible API:

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
