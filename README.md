# chatcli

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
pip install chatcli
```

Or install from source:

```bash
git clone https://github.com/yourusername/chatcli.git
cd chatcli
pip install -e .
```

## Quick Start

### 1. Add a profile

```bash
# OpenAI
chatcli profile add openai --base-url https://api.openai.com/v1 --api-key sk-... --model gpt-4o

# Ollama (local)
chatcli profile add ollama --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# Groq
chatcli profile add groq --base-url https://api.groq.com/openai/v1 --api-key gsk-... --model llama-3.1-70b-versatile
```

### 2. Chat!

```bash
# Start an interactive chat session
chatcli chat

# Send a one-off message
chatcli send "Explain quantum computing in simple terms"

# Use a specific profile and model
chatcli chat --profile ollama --model llama3
```

### 3. Manage conversations

```bash
# List all conversations
chatcli convo list

# Resume a previous conversation
chatcli convo resume <conversation-id>

# Export to markdown
chatcli convo export <conversation-id> --format md
```

## Commands

### Profile Management

```bash
chatcli profile add <name>           # Add a new API profile
chatcli profile list                 # List all profiles
chatcli profile show <name>          # Show profile details
chatcli profile set-default <name>   # Set default profile
chatcli profile remove <name>        # Remove a profile
```

### Model Management

```bash
chatcli model list                   # List available models from current profile
chatcli model list --profile <name>  # List models from specific profile
chatcli model set <model-name>       # Set default model for current profile
```

### Chatting

```bash
chatcli chat                         # Start interactive chat
chatcli chat --profile <name>        # Use specific profile
chatcli chat --model <name>          # Use specific model
chatcli chat --system "You are..."   # Set system prompt
chatcli chat --temperature 0.7       # Set temperature
chatcli chat --max-tokens 2000       # Set max tokens
chatcli chat --no-stream             # Wait for complete response

chatcli send "message"               # Send one-off message
chatcli send "message" --save        # Save one-off message to history
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
chatcli convo list                   # List all conversations
chatcli convo list --profile <name>  # Filter by profile
chatcli convo list --limit 50        # Show more conversations
chatcli convo show <id>              # Display full conversation
chatcli convo resume <id>            # Resume interactive chat
chatcli convo delete <id>            # Delete conversation
chatcli convo export <id> --format json  # Export to JSON
chatcli convo export <id> --format md    # Export to Markdown
```

## Configuration

Profiles and settings are stored in your platform's app directory:
- **Linux**: `~/.config/chatcli/`
- **macOS**: `~/Library/Application Support/chatcli/`
- **Windows**: `%APPDATA%\chatcli\`

### Environment Variables

Override profile settings with environment variables:

```bash
export CHATCLI_API_KEY=sk-...
export CHATCLI_BASE_URL=https://api.openai.com/v1
export CHATCLI_MODEL=gpt-4o
```

## Supported Providers

chatcli works with any OpenAI-compatible API:

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
