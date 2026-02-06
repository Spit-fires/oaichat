"""Profile management commands."""

from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from chatcli.config import (
    add_profile, list_profiles, remove_profile, 
    set_default_profile, get_default_profile_name, get_profile
)
from chatcli.core.models import Profile
from chatcli.core.streaming import display_success, display_error, display_info


app = typer.Typer(help="Manage API provider profiles")
console = Console()


@app.command("add")
def add_profile_cmd(
    name: str = typer.Argument(..., help="Profile name"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="API base URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
    model: Optional[str] = typer.Option(None, "--model", help="Default model"),
    system_prompt: Optional[str] = typer.Option(None, "--system", help="Default system prompt"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Default temperature (0.0-2.0)"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Default max tokens"),
):
    """Add or update an API provider profile."""
    import re
    
    # Validate profile name (alphanumeric, hyphens, underscores only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        display_error("Profile name can only contain letters, numbers, hyphens, and underscores")
        raise typer.Exit(1)
    
    # Check if profile already exists and warn
    existing_profile = get_profile(name)
    if existing_profile:
        display_info(f"Profile '{name}' already exists. This will update the existing profile.")
        if not Confirm.ask("Continue?", default=False):
            display_info("Cancelled")
            return
    
    # Interactive prompts for missing values
    if not base_url:
        console.print("\n[bold]Common base URLs:[/bold]")
        console.print("  OpenAI:     https://api.openai.com/v1")
        console.print("  Ollama:     http://localhost:11434/v1")
        console.print("  LM Studio:  http://localhost:1234/v1")
        console.print("  Groq:       https://api.groq.com/openai/v1")
        console.print("  Together:   https://api.together.xyz/v1\n")
        base_url = Prompt.ask("Base URL")
    
    if not api_key:
        console.print("\n[dim]For local providers (Ollama, LM Studio), use any value like 'not-needed'[/dim]")
        api_key = Prompt.ask("API Key", password=True)
    
    if not model:
        console.print("\n[dim]You can set this later with 'chatcli model set' after listing available models[/dim]")
        model = Prompt.ask("Default model (optional, press Enter to skip)", default="")
        model = model.strip() if model else None
    else:
        model = model.strip()
    
    # Validate temperature if provided
    if temperature is not None and not (0.0 <= temperature <= 2.0):
        display_error("Temperature must be between 0.0 and 2.0")
        raise typer.Exit(1)
    
    # Create profile
    profile = Profile(
        name=name,
        base_url=base_url,
        api_key=api_key,
        default_model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    add_profile(profile)
    display_success(f"Profile '{name}' added successfully")
    
    # Show if it's the default
    if get_default_profile_name() == name:
        display_info(f"'{name}' is now the default profile")


@app.command("list")
def list_profiles_cmd():
    """List all configured profiles."""
    profiles = list_profiles()
    
    if not profiles:
        display_info("No profiles configured. Add one with: chatcli profile add <name>")
        return
    
    default = get_default_profile_name()
    
    table = Table(title="API Profiles", show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Base URL")
    table.add_column("Default Model")
    table.add_column("Default", justify="center")
    
    for profile in profiles:
        is_default = "⭐" if profile.name == default else ""
        model = profile.default_model or "[dim]not set[/dim]"
        table.add_row(profile.name, profile.base_url, model, is_default)
    
    console.print(table)


@app.command("show")
def show_profile_cmd(name: str = typer.Argument(..., help="Profile name")):
    """Show detailed information about a profile."""
    profile = get_profile(name)
    
    if not profile:
        display_error(f"Profile '{name}' not found")
        raise typer.Exit(1)
    
    console.print(f"\n[bold]Profile: {profile.name}[/bold]")
    console.print(f"Base URL:       {profile.base_url}")
    console.print(f"API Key:        {'*' * 20} (hidden)")
    console.print(f"Default Model:  {profile.default_model or '[dim]not set[/dim]'}")
    
    if profile.system_prompt:
        console.print(f"System Prompt:  {profile.system_prompt}")
    
    if profile.temperature is not None:
        console.print(f"Temperature:    {profile.temperature}")
    
    if profile.max_tokens is not None:
        console.print(f"Max Tokens:     {profile.max_tokens}")
    
    if get_default_profile_name() == name:
        console.print("\n[green]⭐ This is the default profile[/green]")
    
    console.print()


@app.command("edit")
def edit_profile_cmd(
    name: str = typer.Argument(..., help="Profile name"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="API base URL"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key"),
    model: Optional[str] = typer.Option(None, "--model", help="Default model"),
    system_prompt: Optional[str] = typer.Option(None, "--system", help="Default system prompt"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Default temperature (0.0-2.0)"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Default max tokens"),
):
    """Edit an existing profile."""
    profile = get_profile(name)
    
    if not profile:
        display_error(f"Profile '{name}' not found")
        raise typer.Exit(1)
    
    # Validate temperature if provided
    if temperature is not None and not (0.0 <= temperature <= 2.0):
        display_error("Temperature must be between 0.0 and 2.0")
        raise typer.Exit(1)
    
    # Update only the provided fields
    if base_url is not None:
        profile.base_url = base_url
    if api_key is not None:
        profile.api_key = api_key
    if model is not None:
        profile.default_model = model.strip()
    if system_prompt is not None:
        profile.system_prompt = system_prompt
    if temperature is not None:
        profile.temperature = temperature
    if max_tokens is not None:
        profile.max_tokens = max_tokens
    
    add_profile(profile)
    display_success(f"Profile '{name}' updated successfully")


@app.command("remove")
def remove_profile_cmd(name: str = typer.Argument(..., help="Profile name")):
    """Remove a profile."""
    profile = get_profile(name)
    
    if not profile:
        display_error(f"Profile '{name}' not found")
        raise typer.Exit(1)
    
    # Confirm deletion
    if not Confirm.ask(f"Are you sure you want to remove profile '{name}'?"):
        display_info("Cancelled")
        return
    
    if remove_profile(name):
        display_success(f"Profile '{name}' removed")
    else:
        display_error(f"Failed to remove profile '{name}'")
        raise typer.Exit(1)


@app.command("set-default")
def set_default_cmd(name: str = typer.Argument(..., help="Profile name")):
    """Set the default profile."""
    if set_default_profile(name):
        display_success(f"'{name}' is now the default profile")
    else:
        display_error(f"Profile '{name}' not found")
        raise typer.Exit(1)
