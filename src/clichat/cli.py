"""Main CLI entry point."""

import typer
from clichat import __version__
from clichat.commands import profile, model, chat, conversation


# Create main app
app = typer.Typer(
    name="clichat",
    help="A beautiful CLI for OpenAI-compatible chat APIs",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)

# Register subcommands
app.add_typer(profile.app, name="profile")
app.add_typer(model.app, name="model")
app.add_typer(conversation.app, name="convo")

# Add top-level chat and send commands
app.command(name="chat")(chat.chat_cmd)
app.command(name="send")(chat.send_cmd)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        typer.echo(f"clichat {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    clichat - A beautiful CLI for OpenAI-compatible chat APIs
    
    Start chatting with: [bold green]clichat chat[/bold green]
    
    Configure a profile first: [bold cyan]clichat profile add <name>[/bold cyan]
    """
    pass


if __name__ == "__main__":
    app()
