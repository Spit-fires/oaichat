"""Model management commands."""

from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from oaichat.core.client import get_client, list_models
from oaichat.config import update_profile_model, get_profile
from oaichat.core.streaming import display_success, display_error, display_info


app = typer.Typer(help="Manage models")
console = Console()


@app.command("list")
def list_models_cmd(
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile to list models from")
):
    """List available models from the API."""
    try:
        client, profile_obj = get_client(profile)
        
        display_info(f"Fetching models from profile '{profile_obj.name}'...")
        models = list_models(client)
        
        if not models:
            display_info("No models found")
            return
        
        table = Table(
            title=f"Available Models ({profile_obj.name})",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Model ID", style="green")
        table.add_column("Type", style="dim")
        
        for model in models:
            # Mark the current default
            model_id = model["id"]
            if model_id == profile_obj.default_model:
                model_id = f"⭐ {model_id}"
            
            table.add_row(model_id, model.get("object", "model"))
        
        console.print(table)
        console.print(f"\n[dim]Total: {len(models)} models[/dim]")
        
    except ValueError as e:
        display_error(str(e))
        raise typer.Exit(1)
    except RuntimeError as e:
        display_error(str(e))
        display_info("Make sure the API is accessible and your credentials are correct")
        raise typer.Exit(1)
    except Exception as e:
        display_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command("set")
def set_model_cmd(
    model: str = typer.Argument(..., help="Model name"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile to update")
):
    """Set the default model for a profile."""
    # Get the profile to update
    profile_name = profile
    if not profile_name:
        # Use default profile
        _, profile_obj = get_client()
        profile_name = profile_obj.name
    else:
        # Verify profile exists
        profile_obj = get_profile(profile_name)
        if not profile_obj:
            display_error(f"Profile '{profile_name}' not found")
            raise typer.Exit(1)
    
    # Update the model
    if update_profile_model(profile_name, model):
        display_success(f"Default model for '{profile_name}' set to '{model}'")
    else:
        display_error(f"Failed to update profile '{profile_name}'")
        raise typer.Exit(1)
