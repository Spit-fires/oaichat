# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/oaichat.git
cd oaichat

# Install in editable mode
pip install -e .

# Or install from PyPI (once published)
pip install oaichat
```

## First Time Setup

### 1. Add your first profile

For **OpenAI**:
```bash
oaichat profile add openai \
  --base-url https://api.openai.com/v1 \
  --api-key sk-your-key-here \
  --model gpt-4o
```

For **Ollama** (local):
```bash
oaichat profile add ollama \
  --base-url http://localhost:11434/v1 \
  --api-key ollama \
  --model llama3
```

For **Groq**:
```bash
oaichat profile add groq \
  --base-url https://api.groq.com/openai/v1 \
  --api-key gsk-your-key-here \
  --model llama-3.1-70b-versatile
```

### 2. List available models

```bash
oaichat model list
```

### 3. Start chatting!

```bash
oaichat chat
```

## Common Commands

### Interactive Chat
```bash
# Start a chat with default profile
oaichat chat

# Use a specific profile
oaichat chat --profile ollama

# Use a specific model
oaichat chat --model gpt-4o

# Set a custom system prompt
oaichat chat --system "You are a helpful coding assistant"

# Disable streaming
oaichat chat --no-stream

# Resume a previous conversation
oaichat chat --resume <conversation-id>
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
oaichat send "What is the capital of France?"

# Save the conversation
oaichat send "Explain quantum computing" --save

# Use no-stream mode
oaichat send "Count to 10" --no-stream
```

### Manage Conversations
```bash
# List all conversations
oaichat convo list

# Show a specific conversation
oaichat convo show <id>

# Resume a conversation
oaichat convo resume <id>

# Delete a conversation
oaichat convo delete <id>

# Export to Markdown
oaichat convo export <id> --format md

# Export to JSON
oaichat convo export <id> --format json
```

### Manage Profiles
```bash
# List all profiles
oaichat profile list

# Show profile details
oaichat profile show <name>

# Set default profile
oaichat profile set-default <name>

# Remove a profile
oaichat profile remove <name>
```

### Manage Models
```bash
# List models from current profile
oaichat model list

# List models from specific profile
oaichat model list --profile ollama

# Set default model for current profile
oaichat model set llama3
```

## Tips & Tricks

### Environment Variables

Override profile settings with environment variables:
```bash
export CLICHAT_API_KEY=sk-...
export CLICHAT_BASE_URL=https://api.openai.com/v1
export CLICHAT_MODEL=gpt-4o

oaichat chat  # Will use environment variables
```

### Configuration Location

Your config and data are stored in:
- **Linux**: `~/.config/oaichat/`
- **macOS**: `~/Library/Application Support/oaichat/`
- **Windows**: `%APPDATA%\oaichat\`

Files:
- `config.toml` - Profile configurations
- `oaichat.db` - SQLite database with conversations

### Multiple Profiles

Switch between different API providers easily:
```bash
# Set up multiple profiles
oaichat profile add openai --base-url ... --api-key ... --model gpt-4o
oaichat profile add claude --base-url ... --api-key ... --model claude-3-5-sonnet
oaichat profile add local --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# Use them
oaichat chat --profile openai
oaichat chat --profile claude
oaichat chat --profile local
```

### Advanced Features

**Custom system prompts per profile**:
```bash
oaichat profile add coding \
  --base-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4o \
  --system "You are an expert programmer. Always provide concise, working code."
```

**Temperature and token limits**:
```bash
oaichat chat --temperature 0.9 --max-tokens 2000
```

**Export conversations for documentation**:
```bash
# Export as markdown for sharing
oaichat convo export <id> --format md --output conversation.md
```

## Troubleshooting

### Can't connect to API
```bash
# Test with model list
oaichat model list

# Check profile configuration
oaichat profile show <name>
```

### No profiles configured
```bash
# The first added profile becomes the default
oaichat profile add myprofile --base-url ... --api-key ... --model ...
```

### Conversation not found
```bash
# Use full ID or first 8 characters
oaichat convo list  # Shows short IDs
oaichat convo show <short-id>
```

## Examples

### Code Review Assistant
```bash
oaichat profile add codereview \
  --base-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4o \
  --system "You are a code reviewer. Provide constructive feedback on code quality, security, and best practices."

oaichat chat --profile codereview
```

### Creative Writing
```bash
oaichat chat \
  --profile openai \
  --system "You are a creative writing assistant" \
  --temperature 1.5
```

### Quick Questions
```bash
# One-shot for quick answers
oaichat send "What is the time complexity of quicksort?" --no-stream
```

### Local Development
```bash
# Use Ollama for free local LLMs
ollama pull llama3
oaichat profile add local --base-url http://localhost:11434/v1 --api-key ollama --model llama3
oaichat chat --profile local
```
