"""OpenAI client factory and API utilities."""

from typing import Optional
from openai import OpenAI
from chatcli.config import get_profile, get_env_overrides
from chatcli.core.models import Profile


def get_client(profile_name: Optional[str] = None, 
               base_url: Optional[str] = None,
               api_key: Optional[str] = None) -> tuple[OpenAI, Profile]:
    """
    Get an OpenAI client configured for the specified profile.
    
    Returns (client, profile) tuple.
    
    Args:
        profile_name: Name of the profile to use. If None, uses default profile.
        base_url: Override base URL from profile
        api_key: Override API key from profile
    
    Raises:
        ValueError: If no profile is configured or profile not found
    """
    # Get the profile
    profile = get_profile(profile_name)
    
    if not profile:
        if profile_name:
            raise ValueError(f"Profile '{profile_name}' not found")
        else:
            raise ValueError(
                "No default profile configured. "
                "Create one with: chatcli profile add <name>"
            )
    
    # Apply environment variable overrides
    env_overrides = get_env_overrides()
    
    final_base_url = base_url or env_overrides.get("base_url") or profile.base_url
    final_api_key = api_key or env_overrides.get("api_key") or profile.api_key
    
    client = OpenAI(
        base_url=final_base_url,
        api_key=final_api_key,
        timeout=600.0  # 10 minutes
    )
    
    return client, profile


def list_models(client: OpenAI) -> list[dict]:
    """
    List available models from the API.
    
    Returns list of model dicts with at least 'id' field.
    """
    try:
        response = client.models.list()
        
        # Handle different response types
        if isinstance(response, list):
            # Some APIs return a plain list
            models = [{"id": getattr(model, "id", str(model)), "object": getattr(model, "object", "model")} 
                     for model in response]
        else:
            # Standard OpenAI response with .data attribute
            models = [{"id": model.id, "object": getattr(model, "object", "model")} 
                     for model in response.data]
        
        return sorted(models, key=lambda m: m["id"])
    except Exception as e:
        raise RuntimeError(f"Failed to list models: {str(e)}")


def generate_title(client: OpenAI, messages: list[dict], model: str) -> str:
    """
    Generate a conversation title using the LLM.
    
    Args:
        client: OpenAI client
        messages: First few messages from the conversation
        model: Model to use for generation
    
    Returns:
        Generated title string, or fallback timestamp-based title if generation fails
    """
    from datetime import datetime
    
    try:
        # Take first 4 messages for context (or all if fewer)
        context_messages = messages[:4]
        
        title_prompt = [
            {
                "role": "system",
                "content": "Generate a concise 3-6 word title for this conversation. Respond with only the title, no quotes or extra text."
            },
            *context_messages,
            {
                "role": "user",
                "content": "What would be a good title for this conversation?"
            }
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=title_prompt,
            max_tokens=20,
            temperature=0.7
        )
        
        title = (response.choices[0].message.content or "").strip()
        # Remove quotes if present
        title = title.strip('"\'')
        
        # Limit length
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title if title else f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    except (Exception, KeyboardInterrupt) as e:
        # Fallback to timestamp-based title on any error or interruption
        return f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
