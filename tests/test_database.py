"""Tests for database operations."""

import pytest
from chatcli.storage.database import (
    create_conversation, add_message, get_conversation,
    list_conversations, delete_conversation, find_conversation_by_prefix
)


def test_create_conversation(temp_app_dir, monkeypatch):
    """Test creating a conversation."""
    from chatcli import config
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    
    conv = create_conversation(
        profile="test-profile",
        model="gpt-4",
        system_prompt="You are helpful"
    )
    
    assert conv is not None
    assert conv.profile == "test-profile"
    assert conv.model == "gpt-4"
    assert conv.system_prompt == "You are helpful"


def test_add_and_retrieve_messages(temp_app_dir, monkeypatch):
    """Test adding and retrieving messages."""
    from chatcli import config
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    
    conv = create_conversation(profile="test", model="gpt-4")
    
    add_message(conv.id, "user", "Hello")
    add_message(conv.id, "assistant", "Hi there")
    
    retrieved = get_conversation(conv.id)
    assert retrieved is not None
    assert len(retrieved.messages) == 2
    assert retrieved.messages[0].content == "Hello"
    assert retrieved.messages[1].content == "Hi there"


def test_find_conversation_by_prefix(temp_app_dir, monkeypatch):
    """Test finding conversation by partial ID."""
    from chatcli import config
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    
    conv = create_conversation(profile="test", model="gpt-4")
    
    # Should find by first 8 characters
    found = find_conversation_by_prefix(conv.id[:8])
    assert found is not None
    assert found.id == conv.id


def test_list_conversations_with_search(temp_app_dir, monkeypatch):
    """Test searching conversations."""
    from chatcli import config
    from chatcli.storage.database import update_title
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    
    # Create conversations with different titles
    conv1 = create_conversation(profile="test", model="gpt-4")
    update_title(conv1.id, "Python programming help")
    
    conv2 = create_conversation(profile="test", model="gpt-4")
    update_title(conv2.id, "JavaScript debugging")
    
    # Search for Python
    results = list_conversations(search="Python")
    assert len(results) >= 1
    assert any("Python" in c.title for c in results)
