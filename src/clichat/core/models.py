"""Pydantic models for clichat data structures."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Profile(BaseModel):
    """API provider profile configuration."""
    
    name: str
    base_url: str
    api_key: str
    default_model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)


class Message(BaseModel):
    """Chat message."""
    
    role: str  # "system", "user", or "assistant"
    content: str
    token_usage_prompt: Optional[int] = None
    token_usage_completion: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    """Chat conversation."""
    
    id: str
    profile: str
    model: str
    title: Optional[str] = None
    system_prompt: Optional[str] = None
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, 
                   token_usage_prompt: Optional[int] = None,
                   token_usage_completion: Optional[int] = None) -> Message:
        """Add a message to the conversation."""
        message = Message(
            role=role,
            content=content,
            token_usage_prompt=token_usage_prompt,
            token_usage_completion=token_usage_completion
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def to_openai_messages(self) -> list[dict]:
        """Convert conversation to OpenAI message format."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for msg in self.messages:
            messages.append({"role": msg.role, "content": msg.content})
        return messages
    
    def total_tokens(self) -> tuple[int, int, int]:
        """Return (prompt_tokens, completion_tokens, total_tokens)."""
        prompt = sum(m.token_usage_prompt or 0 for m in self.messages)
        completion = sum(m.token_usage_completion or 0 for m in self.messages)
        return prompt, completion, prompt + completion
