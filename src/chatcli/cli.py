"""Main CLI entry point."""

import typer
from chatcli import __version__
from chatcli.commands import profile, model, chat, conversation


# Create main app
app = typer.Typer(
    name="chatcli",
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
        typer.echo(f"chatcli {__version__}")
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
    chatcli - A beautiful CLI for OpenAI-compatible chat APIs
    
    Start chatting with: [bold green]chatcli chat[/bold green]
    
    Configure a profile first: [bold cyan]chatcli profile add <name>[/bold cyan]
    """
    pass


if __name__ == "__main__":
    app()
