"""Export conversations to different formats."""

import json
from pathlib import Path
from oaichat.core.models import Conversation


def export_to_json(conversation: Conversation, output_path: Path) -> None:
    """Export conversation to JSON format."""
    data = {
        "id": conversation.id,
        "profile": conversation.profile,
        "model": conversation.model,
        "title": conversation.title,
        "system_prompt": conversation.system_prompt,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "token_usage_prompt": msg.token_usage_prompt,
                "token_usage_completion": msg.token_usage_completion,
                "created_at": msg.created_at.isoformat()
            }
            for msg in conversation.messages
        ]
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_to_markdown(conversation: Conversation, output_path: Path) -> None:
    """Export conversation to Markdown format."""
    lines = []
    
    # Header
    lines.append(f"# {conversation.title or 'Conversation'}\n")
    lines.append(f"**Model:** {conversation.model}  ")
    lines.append(f"**Profile:** {conversation.profile}  ")
    lines.append(f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}  ")
    lines.append(f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}  \n")
    
    # System prompt
    if conversation.system_prompt:
        lines.append("## System Prompt\n")
        lines.append(f"> {conversation.system_prompt}\n")
    
    # Messages
    lines.append("## Conversation\n")
    
    for msg in conversation.messages:
        if msg.role == "user":
            lines.append("### 👤 User\n")
        elif msg.role == "assistant":
            lines.append("### 🤖 Assistant\n")
        elif msg.role == "system":
            lines.append("### ⚙️ System\n")
        
        lines.append(f"{msg.content}\n")
        
        # Add token usage if available
        if msg.token_usage_prompt or msg.token_usage_completion:
            lines.append(
                f"*Tokens: {msg.token_usage_prompt or 0} prompt + "
                f"{msg.token_usage_completion or 0} completion*\n"
            )
        
        lines.append("---\n")
    
    # Footer with totals
    prompt_tokens, completion_tokens, total_tokens = conversation.total_tokens()
    if total_tokens > 0:
        lines.append(f"\n**Total Tokens:** {total_tokens} "
                    f"({prompt_tokens} prompt + {completion_tokens} completion)")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def get_export_filename(conversation: Conversation, format: str) -> str:
    """Generate a safe filename for export."""
    title = conversation.title or "conversation"
    
    # Sanitize title for filename
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
    safe_title = safe_title.strip().replace(' ', '_')
    
    # Limit length
    if len(safe_title) > 50:
        safe_title = safe_title[:50]
    
    # Add ID suffix to ensure uniqueness
    short_id = conversation.id[:8]
    
    return f"{safe_title}_{short_id}.{format}"
