# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/clichat.git
cd clichat

# Install in editable mode
pip install -e .

# Or install from PyPI (once published)
pip install clichat
```

## First Time Setup

### 1. Add your first profile

For **OpenAI**:
```bash
clichat profile add openai \
  --base-url https://api.openai.com/v1 \
  --api-key sk-your-key-here \
  --model gpt-4o
```

For **Ollama** (local):
```bash
clichat profile add ollama \
  --base-url http://localhost:11434/v1 \
  --api-key ollama \
  --model llama3
```

For **Groq**:
```bash
clichat profile add groq \
  --base-url https://api.groq.com/openai/v1 \
  --api-key gsk-your-key-here \
  --model llama-3.1-70b-versatile
```

### 2. List available models

```bash
clichat model list
```

### 3. Start chatting!

```bash
clichat chat
```

## Common Commands

### Interactive Chat
```bash
# Start a chat with default profile
clichat chat

# Use a specific profile
clichat chat --profile ollama

# Use a specific model
clichat chat --model gpt-4o

# Set a custom system prompt
clichat chat --system "You are a helpful coding assistant"

# Disable streaming
clichat chat --no-stream

# Resume a previous conversation
clichat chat --resume <conversation-id>
```

### In-Chat Commands

While in an interactive chat:
- `/exit` - Exit the chat
- `/clear` - Clear conversation history
- `/system <prompt>` - Change system prompt
- `/model <name>` - Switch model
- `/save` - Force save and generate title
- `/usage` - Show session token usage
- `/help` - Show help

### One-Shot Messages
```bash
# Send a single message
clichat send "What is the capital of France?"

# Save the conversation
clichat send "Explain quantum computing" --save

# Use no-stream mode
clichat send "Count to 10" --no-stream
```

### Manage Conversations
```bash
# List all conversations
clichat convo list

# Show a specific conversation
clichat convo show <id>

# Resume a conversation
clichat convo resume <id>

# Delete a conversation
clichat convo delete <id>

# Export to Markdown
clichat convo export <id> --format md

# Export to JSON
clichat convo export <id> --format json
```

### Manage Profiles
```bash
# List all profiles
clichat profile list

# Show profile details
clichat profile show <name>

# Set default profile
clichat profile set-default <name>

# Remove a profile
clichat profile remove <name>
```

### Manage Models
```bash
# List models from current profile
clichat model list

# List models from specific profile
clichat model list --profile ollama

# Set default model for current profile
clichat model set llama3
```

## Tips & Tricks

### Environment Variables

Override profile settings with environment variables:
```bash
export CLICHAT_API_KEY=sk-...
export CLICHAT_BASE_URL=https://api.openai.com/v1
export CLICHAT_MODEL=gpt-4o

clichat chat  # Will use environment variables
```

### Configuration Location

Your config and data are stored in:
- **Linux**: `~/.config/clichat/`
- **macOS**: `~/Library/Application Support/clichat/`
- **Windows**: `%APPDATA%\clichat\`

Files:
- `config.toml` - Profile configurations
- `clichat.db` - SQLite database with conversations

### Multiple Profiles

Switch between different API providers easily:
```bash
# Set up multiple profiles
clichat profile add openai --base-url ... --api-key ... --model gpt-4o
clichat profile add claude --base-url ... --api-key ... --model claude-3-5-sonnet
clichat profile add local --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# Use them
clichat chat --profile openai
clichat chat --profile claude
clichat chat --profile local
```

### Advanced Features

**Custom system prompts per profile**:
```bash
clichat profile add coding \
  --base-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4o \
  --system "You are an expert programmer. Always provide concise, working code."
```

**Temperature and token limits**:
```bash
clichat chat --temperature 0.9 --max-tokens 2000
```

**Export conversations for documentation**:
```bash
# Export as markdown for sharing
clichat convo export <id> --format md --output conversation.md
```

## Troubleshooting

### Can't connect to API
```bash
# Test with model list
clichat model list

# Check profile configuration
clichat profile show <name>
```

### No profiles configured
```bash
# The first added profile becomes the default
clichat profile add myprofile --base-url ... --api-key ... --model ...
```

### Conversation not found
```bash
# Use full ID or first 8 characters
clichat convo list  # Shows short IDs
clichat convo show <short-id>
```

## Examples

### Code Review Assistant
```bash
clichat profile add codereview \
  --base-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4o \
  --system "You are a code reviewer. Provide constructive feedback on code quality, security, and best practices."

clichat chat --profile codereview
```

### Creative Writing
```bash
clichat chat \
  --profile openai \
  --system "You are a creative writing assistant" \
  --temperature 1.5
```

### Quick Questions
```bash
# One-shot for quick answers
clichat send "What is the time complexity of quicksort?" --no-stream
```

### Local Development
```bash
# Use Ollama for free local LLMs
ollama pull llama3
clichat profile add local --base-url http://localhost:11434/v1 --api-key ollama --model llama3
clichat chat --profile local
```
