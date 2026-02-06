# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/chatcli.git
cd chatcli

# Install in editable mode
pip install -e .

# Or install from PyPI (once published)
pip install chatcli
```

## First Time Setup

### 1. Add your first profile

For **OpenAI**:
```bash
chatcli profile add openai \
  --base-url https://api.openai.com/v1 \
  --api-key sk-your-key-here \
  --model gpt-4o
```

For **Ollama** (local):
```bash
chatcli profile add ollama \
  --base-url http://localhost:11434/v1 \
  --api-key ollama \
  --model llama3
```

For **Groq**:
```bash
chatcli profile add groq \
  --base-url https://api.groq.com/openai/v1 \
  --api-key gsk-your-key-here \
  --model llama-3.1-70b-versatile
```

### 2. List available models

```bash
chatcli model list
```

### 3. Start chatting!

```bash
chatcli chat
```

## Common Commands

### Interactive Chat
```bash
# Start a chat with default profile
chatcli chat

# Use a specific profile
chatcli chat --profile ollama

# Use a specific model
chatcli chat --model gpt-4o

# Set a custom system prompt
chatcli chat --system "You are a helpful coding assistant"

# Disable streaming
chatcli chat --no-stream

# Resume a previous conversation
chatcli chat --resume <conversation-id>
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
chatcli send "What is the capital of France?"

# Save the conversation
chatcli send "Explain quantum computing" --save

# Use no-stream mode
chatcli send "Count to 10" --no-stream
```

### Manage Conversations
```bash
# List all conversations
chatcli convo list

# Show a specific conversation
chatcli convo show <id>

# Resume a conversation
chatcli convo resume <id>

# Delete a conversation
chatcli convo delete <id>

# Export to Markdown
chatcli convo export <id> --format md

# Export to JSON
chatcli convo export <id> --format json
```

### Manage Profiles
```bash
# List all profiles
chatcli profile list

# Show profile details
chatcli profile show <name>

# Set default profile
chatcli profile set-default <name>

# Remove a profile
chatcli profile remove <name>
```

### Manage Models
```bash
# List models from current profile
chatcli model list

# List models from specific profile
chatcli model list --profile ollama

# Set default model for current profile
chatcli model set llama3
```

## Tips & Tricks

### Environment Variables

Override profile settings with environment variables:
```bash
export CHATCLI_API_KEY=sk-...
export CHATCLI_BASE_URL=https://api.openai.com/v1
export CHATCLI_MODEL=gpt-4o

chatcli chat  # Will use environment variables
```

### Configuration Location

Your config and data are stored in:
- **Linux**: `~/.config/chatcli/`
- **macOS**: `~/Library/Application Support/chatcli/`
- **Windows**: `%APPDATA%\chatcli\`

Files:
- `config.toml` - Profile configurations
- `chatcli.db` - SQLite database with conversations

### Multiple Profiles

Switch between different API providers easily:
```bash
# Set up multiple profiles
chatcli profile add openai --base-url ... --api-key ... --model gpt-4o
chatcli profile add claude --base-url ... --api-key ... --model claude-3-5-sonnet
chatcli profile add local --base-url http://localhost:11434/v1 --api-key ollama --model llama3

# Use them
chatcli chat --profile openai
chatcli chat --profile claude
chatcli chat --profile local
```

### Advanced Features

**Custom system prompts per profile**:
```bash
chatcli profile add coding \
  --base-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4o \
  --system "You are an expert programmer. Always provide concise, working code."
```

**Temperature and token limits**:
```bash
chatcli chat --temperature 0.9 --max-tokens 2000
```

**Export conversations for documentation**:
```bash
# Export as markdown for sharing
chatcli convo export <id> --format md --output conversation.md
```

## Troubleshooting

### Can't connect to API
```bash
# Test with model list
chatcli model list

# Check profile configuration
chatcli profile show <name>
```

### No profiles configured
```bash
# The first added profile becomes the default
chatcli profile add myprofile --base-url ... --api-key ... --model ...
```

### Conversation not found
```bash
# Use full ID or first 8 characters
chatcli convo list  # Shows short IDs
chatcli convo show <short-id>
```

## Examples

### Code Review Assistant
```bash
chatcli profile add codereview \
  --base-url https://api.openai.com/v1 \
  --api-key sk-... \
  --model gpt-4o \
  --system "You are a code reviewer. Provide constructive feedback on code quality, security, and best practices."

chatcli chat --profile codereview
```

### Creative Writing
```bash
chatcli chat \
  --profile openai \
  --system "You are a creative writing assistant" \
  --temperature 1.5
```

### Quick Questions
```bash
# One-shot for quick answers
chatcli send "What is the time complexity of quicksort?" --no-stream
```

### Local Development
```bash
# Use Ollama for free local LLMs
ollama pull llama3
chatcli profile add local --base-url http://localhost:11434/v1 --api-key ollama --model llama3
chatcli chat --profile local
```
