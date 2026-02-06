"""Tests for core models."""

import pytest
from clichat.core.models import Profile, Message, Conversation


def test_profile_creation():
    """Test creating a profile."""
    profile = Profile(
        name="test",
        base_url="http://localhost:11434/v1",
        api_key="test-key",
        default_model="llama2",
        temperature=0.7,
        max_tokens=1000
    )
    
    assert profile.name == "test"
    assert profile.temperature == 0.7
    assert profile.max_tokens == 1000


def test_conversation_messages():
    """Test conversation message handling."""
    conv = Conversation(
        id="test-id",
        profile="test-profile",
        model="gpt-4",
        system_prompt="You are helpful"
    )
    
    conv.add_message("user", "Hello")
    conv.add_message("assistant", "Hi there")
    
    assert len(conv.messages) == 2
    assert conv.messages[0].role == "user"
    assert conv.messages[1].role == "assistant"


def test_conversation_to_openai_messages():
    """Test conversion to OpenAI format."""
    conv = Conversation(
        id="test-id",
        profile="test-profile",
        model="gpt-4",
        system_prompt="You are helpful"
    )
    
    conv.add_message("user", "Hello")
    conv.add_message("assistant", "Hi")
    
    messages = conv.to_openai_messages()
    
    # Should include system prompt + messages
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are helpful"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
