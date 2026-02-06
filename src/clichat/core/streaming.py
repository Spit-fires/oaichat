"""Streaming response rendering with Rich."""

from typing import Optional
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner


console = Console()


def stream_response(client: OpenAI, messages: list[dict], model: str,
                   temperature: Optional[float] = None,
                   max_tokens: Optional[int] = None) -> tuple[str, int, int]:
    """
    Stream a chat completion response with live markdown rendering.
    
    Returns (content, prompt_tokens, completion_tokens)
    """
    accumulated = ""
    prompt_tokens = 0
    completion_tokens = 0
    
    try:
        # Create streaming request
        stream: Stream[ChatCompletionChunk] = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Use Rich Live display to update as tokens arrive
        with Live(Spinner("dots", text="Waiting for response..."), console=console, refresh_per_second=10) as live:
            first_chunk = True
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated += content
                    
                    if first_chunk:
                        # Clear spinner on first content
                        first_chunk = False
                    
                    # Update live display with markdown
                    live.update(Markdown(accumulated))
                
                # Capture token usage if available
                if hasattr(chunk, 'usage') and chunk.usage:
                    prompt_tokens = chunk.usage.prompt_tokens or 0
                    completion_tokens = chunk.usage.completion_tokens or 0
    
    except KeyboardInterrupt:
        # User interrupted - return partial response
        console.print("\n[yellow]⚠ Response interrupted by user[/yellow]")
        # Return what we have so far
    
    console.print()  # Add newline after streaming
    
    return accumulated, prompt_tokens, completion_tokens


def get_response(client: OpenAI, messages: list[dict], model: str,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None) -> tuple[str, int, int]:
    """
    Get a chat completion response without streaming (wait and render).
    
    Returns (content, prompt_tokens, completion_tokens)
    """
    with console.status("[bold green]Thinking...", spinner="dots"):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    content = response.choices[0].message.content or ""
    prompt_tokens = response.usage.prompt_tokens if response.usage else 0
    completion_tokens = response.usage.completion_tokens if response.usage else 0
    
    # Render the complete response in a panel with markdown
    console.print(Panel(Markdown(content), border_style="blue", padding=(1, 2)))
    
    return content, prompt_tokens, completion_tokens


def display_token_usage(prompt_tokens: int, completion_tokens: int) -> None:
    """Display token usage information."""
    total = prompt_tokens + completion_tokens
    console.print(
        f"[dim]Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {total} total[/dim]\n"
    )


def display_error(message: str) -> None:
    """Display an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}", style="red")


def display_success(message: str) -> None:
    """Display a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def display_info(message: str) -> None:
    """Display an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def display_warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")
