"""Conversation management commands."""

from typing import Optional
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm
from chatcli.storage.database import (
    list_conversations, get_conversation, delete_conversation, get_message_count,
    find_conversation_by_prefix
)
from chatcli.storage.export import export_to_json, export_to_markdown, get_export_filename
from chatcli.core.streaming import display_success, display_error, display_info


app = typer.Typer(name="convo", help="Manage conversations")
console = Console()


@app.command("list")
def list_conversations_cmd(
    profile: Optional[str] = typer.Option(None, "--profile", help="Filter by profile"),
    limit: int = typer.Option(20, "--limit", help="Number of conversations to show"),
):
    """List all conversations."""
    conversations = list_conversations(profile=profile, limit=limit)
    
    if not conversations:
        display_info("No conversations found")
        if profile:
            display_info(f"Try without --profile filter, or create a new chat")
        return
    
    table = Table(
        title=f"Conversations{f' ({profile})' if profile else ''}",
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Model", style="green")
    table.add_column("Messages", justify="right", style="yellow")
    table.add_column("Updated", style="dim")
    
    for conv in conversations:
        # Get message count
        msg_count = get_message_count(conv.id)
        
        # Format title
        title = conv.title or "[dim]Untitled[/dim]"
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Format date
        updated = conv.updated_at.strftime("%Y-%m-%d %H:%M")
        
        # Short ID
        short_id = conv.id[:8]
        
        table.add_row(short_id, title, conv.model, str(msg_count), updated)
    
    console.print(table)
    console.print(f"\n[dim]Showing {len(conversations)} of {limit} max conversations[/dim]")


@app.command("show")
def show_conversation_cmd(
    conversation_id: str = typer.Argument(..., help="Conversation ID (full or short)")
):
    """Display a full conversation."""
    # Try to find conversation by full or partial ID
    conversation = _find_conversation(conversation_id)
    
    if not conversation:
        display_error(f"Conversation '{conversation_id}' not found")
        raise typer.Exit(1)
    
    # Display header
    console.print(Panel.fit(
        f"[bold]{conversation.title or 'Untitled Conversation'}[/bold]\n\n"
        f"ID: [cyan]{conversation.id}[/cyan]\n"
        f"Profile: [green]{conversation.profile}[/green]\n"
        f"Model: [green]{conversation.model}[/green]\n"
        f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Updated: {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        border_style="cyan"
    ))
    
    # Display system prompt if exists
    if conversation.system_prompt:
        console.print(Panel(
            conversation.system_prompt,
            title="System Prompt",
            border_style="yellow",
            padding=(1, 2)
        ))
    
    # Display messages
    console.print()
    for i, msg in enumerate(conversation.messages):
        if msg.role == "user":
            console.print(Panel(
                msg.content,
                title=f"[bold green]👤 User[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
        elif msg.role == "assistant":
            console.print(Panel(
                Markdown(msg.content),
                title=f"[bold blue]🤖 Assistant[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            ))
            # Show token usage if available
            if msg.token_usage_prompt or msg.token_usage_completion:
                console.print(
                    f"[dim]Tokens: {msg.token_usage_prompt or 0} prompt + "
                    f"{msg.token_usage_completion or 0} completion[/dim]\n"
                )
        elif msg.role == "system":
            console.print(Panel(
                msg.content,
                title=f"[bold yellow]⚙️ System[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            ))
        
        console.print()
    
    # Show totals
    prompt_tokens, completion_tokens, total_tokens = conversation.total_tokens()
    if total_tokens > 0:
        console.print(
            f"[bold]Total Tokens:[/bold] {total_tokens} "
            f"({prompt_tokens} prompt + {completion_tokens} completion)\n"
        )


@app.command("resume")
def resume_conversation_cmd(
    conversation_id: str = typer.Argument(..., help="Conversation ID (full or short)"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Don't stream responses"),
):
    """Resume an interactive chat session."""
    # Import here to avoid circular dependency
    from chatcli.commands.chat import chat_cmd
    
    # Try to find conversation
    conversation = _find_conversation(conversation_id)
    
    if not conversation:
        display_error(f"Conversation '{conversation_id}' not found")
        raise typer.Exit(1)
    
    # Call chat command with resume flag
    chat_cmd(
        profile=conversation.profile,
        model=None,  # Will use conversation's model
        system=None,  # Will use conversation's system prompt
        temperature=None,
        max_tokens=None,
        no_stream=no_stream,
        resume=conversation.id
    )


@app.command("delete")
def delete_conversation_cmd(
    conversation_id: str = typer.Argument(..., help="Conversation ID (full or short)")
):
    """Delete a conversation."""
    # Try to find conversation
    conversation = _find_conversation(conversation_id)
    
    if not conversation:
        display_error(f"Conversation '{conversation_id}' not found")
        raise typer.Exit(1)
    
    # Confirm deletion
    title = conversation.title or conversation.id
    if not Confirm.ask(f"Delete conversation '{title}'?", default=False):
        display_info("Cancelled")
        return
    
    if delete_conversation(conversation.id):
        display_success(f"Conversation deleted")
    else:
        display_error("Failed to delete conversation")
        raise typer.Exit(1)


@app.command("export")
def export_conversation_cmd(
    conversation_id: str = typer.Argument(..., help="Conversation ID (full or short)"),
    format: str = typer.Option("json", "--format", help="Export format: json or md"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Export a conversation to JSON or Markdown."""
    # Try to find conversation
    conversation = _find_conversation(conversation_id)
    
    if not conversation:
        display_error(f"Conversation '{conversation_id}' not found")
        raise typer.Exit(1)
    
    # Validate format
    if format not in ["json", "md"]:
        display_error("Format must be 'json' or 'md'")
        raise typer.Exit(1)
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        filename = get_export_filename(conversation, format)
        output_path = Path.cwd() / filename
    
    # Export
    try:
        if format == "json":
            export_to_json(conversation, output_path)
        else:
            export_to_markdown(conversation, output_path)
        
        display_success(f"Exported to: {output_path}")
    
    except Exception as e:
        display_error(f"Export failed: {str(e)}")
        raise typer.Exit(1)


@app.command("rename")
def rename_conversation_cmd(
    conversation_id: str = typer.Argument(..., help="Conversation ID (full or partial)"),
    title: str = typer.Argument(..., help="New title for the conversation"),
):
    """Rename a conversation."""
    from chatcli.storage.database import update_title
    
    conversation = _find_conversation(conversation_id)
    
    if not conversation:
        display_error(f"Conversation '{conversation_id}' not found")
        raise typer.Exit(1)
    
    try:
        update_title(conversation.id, title)
        display_success(f"Renamed conversation to: {title}")
    except Exception as e:
        display_error(f"Rename failed: {str(e)}")
        raise typer.Exit(1)


@app.command("search")
def search_conversations_cmd(
    query: str = typer.Argument(..., help="Search query (searches in title)"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Filter by profile"),
    limit: int = typer.Option(20, "--limit", help="Number of conversations to show"),
):
    """Search conversations by title."""
    conversations = list_conversations(profile=profile, limit=limit, search=query)
    
    if not conversations:
        display_info(f"No conversations found matching '{query}'")
        return
    
    table = Table(
        title=f"Search Results: '{query}'",
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    table.add_column("Model", style="green")
    table.add_column("Messages", justify="right", style="yellow")
    table.add_column("Updated", style="dim")
    
    for conv in conversations:
        # Get message count
        msg_count = get_message_count(conv.id)
        
        # Format title
        title = conv.title or "[dim]Untitled[/dim]"
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Format date
        updated = conv.updated_at.strftime("%Y-%m-%d %H:%M")
        
        # Short ID
        short_id = conv.id[:8]
        
        table.add_row(
            short_id,
            title,
            conv.model,
            str(msg_count),
            updated
        )
    
    console.print(table)


def _find_conversation(conversation_id: str):
    """Find a conversation by full or partial ID."""
    return find_conversation_by_prefix(conversation_id)
