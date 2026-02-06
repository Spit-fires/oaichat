"""Configuration management for oaichat."""

import os
import sys
from pathlib import Path
from typing import Optional
import tomli_w

# For Python 3.11+, use built-in tomllib, otherwise use tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import typer
from oaichat.core.models import Profile


def get_app_dir() -> Path:
    """Get the application data directory."""
    app_dir = Path(typer.get_app_dir("oaichat"))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_path() -> Path:
    """Get the config file path."""
    return get_app_dir() / "config.toml"


def get_db_path() -> Path:
    """Get the database file path."""
    return get_app_dir() / "oaichat.db"


def load_config() -> dict:
    """Load configuration from TOML file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        return {"default_profile": None, "profiles": {}}
    
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def save_config(config: dict) -> None:
    """Save configuration to TOML file."""
    config_path = get_config_path()
    
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)
    
    # Set restrictive file permissions (owner read/write only)
    config_path.chmod(0o600)


def get_profile(name: Optional[str] = None) -> Optional[Profile]:
    """Get a profile by name, or the default profile if name is None."""
    config = load_config()
    
    # Determine which profile to load
    profile_name = name or config.get("default_profile")
    
    if not profile_name:
        return None
    
    profile_data = config.get("profiles", {}).get(profile_name)
    
    if not profile_data:
        return None
    
    # Apply environment variable overrides
    env_overrides = get_env_overrides()
    profile_data_with_overrides = {**profile_data, **env_overrides}
    
    return Profile(name=profile_name, **profile_data_with_overrides)


def list_profiles() -> list[Profile]:
    """List all configured profiles."""
    config = load_config()
    profiles = []
    
    for name, data in config.get("profiles", {}).items():
        profiles.append(Profile(name=name, **data))
    
    return profiles


def add_profile(profile: Profile) -> None:
    """Add or update a profile."""
    config = load_config()
    
    if "profiles" not in config:
        config["profiles"] = {}
    
    # Convert profile to dict, excluding the name field
    profile_dict = profile.model_dump(exclude={"name"}, exclude_none=True)
    config["profiles"][profile.name] = profile_dict
    
    # Set as default if it's the first profile
    if config.get("default_profile") is None:
        config["default_profile"] = profile.name
    
    save_config(config)


def remove_profile(name: str) -> bool:
    """Remove a profile. Returns True if removed, False if not found."""
    config = load_config()
    
    if name not in config.get("profiles", {}):
        return False
    
    del config["profiles"][name]
    
    # Update default if we removed it
    if config.get("default_profile") == name:
        remaining = list(config.get("profiles", {}).keys())
        config["default_profile"] = remaining[0] if remaining else None
    
    save_config(config)
    return True


def set_default_profile(name: str) -> bool:
    """Set the default profile. Returns True if successful, False if profile not found."""
    config = load_config()
    
    if name not in config.get("profiles", {}):
        return False
    
    config["default_profile"] = name
    save_config(config)
    return True


def get_default_profile_name() -> Optional[str]:
    """Get the name of the default profile."""
    config = load_config()
    return config.get("default_profile")


def update_profile_model(profile_name: str, model: str) -> bool:
    """Update the default model for a profile."""
    config = load_config()
    
    if profile_name not in config.get("profiles", {}):
        return False
    
    config["profiles"][profile_name]["default_model"] = model
    save_config(config)
    return True


def get_env_overrides() -> dict:
    """Get environment variable overrides."""
    overrides = {}
    
    if api_key := os.getenv("OAICHAT_API_KEY"):
        overrides["api_key"] = api_key
    
    if base_url := os.getenv("OAICHAT_BASE_URL"):
        overrides["base_url"] = base_url
    
    if model := os.getenv("OAICHAT_MODEL"):
        overrides["model"] = model
    
    return overrides
