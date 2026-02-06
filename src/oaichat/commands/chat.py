"""Chat commands for interactive and one-shot conversations."""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from oaichat.core.client import get_client, generate_title
from oaichat.core.streaming import (
    stream_response, get_response, display_token_usage,
    display_error, display_success, display_info, display_warning
)
from oaichat.storage.database import (
    create_conversation, add_message, update_title, get_conversation,
    delete_messages, update_conversation_model, update_conversation_system_prompt
)


app = typer.Typer(help="Chat with AI models")
console = Console()


@app.command("chat")
def chat_cmd(
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile to use"),
    model: Optional[str] = typer.Option(None, "--model", help="Model to use"),
    system: Optional[str] = typer.Option(None, "--system", help="System prompt"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Temperature (0.0-2.0)"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Max tokens"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Don't stream responses"),
    resume: Optional[str] = typer.Option(None, "--resume", help="Resume conversation by ID"),
):
    """Start an interactive chat session."""
    try:
        # Validate temperature if provided
        if temperature is not None and not (0.0 <= temperature <= 2.0):
            display_error("Temperature must be between 0.0 and 2.0")
            raise typer.Exit(1)
        
        # Get client and profile
        client, profile_obj = get_client(profile)
        
        # Determine model to use
        active_model = model or profile_obj.default_model
        if not active_model:
            display_error("No model specified. Set a default model or use --model")
            display_info("List available models with: oaichat model list")
            raise typer.Exit(1)
        
        # Determine system prompt
        active_system = system or profile_obj.system_prompt
        
        # Determine temperature and max_tokens
        active_temperature = temperature if temperature is not None else profile_obj.temperature
        active_max_tokens = max_tokens if max_tokens is not None else profile_obj.max_tokens
        
        # Load or create conversation
        if resume:
            conversation = get_conversation(resume)
            if not conversation:
                display_error(f"Conversation '{resume}' not found")
                raise typer.Exit(1)
            
            display_info(f"Resuming conversation: {conversation.title or conversation.id}")
            # Use conversation's settings
            active_model = conversation.model
            active_system = conversation.system_prompt
        else:
            # Create new conversation
            conversation = create_conversation(
                profile=profile_obj.name,
                model=active_model,
                system_prompt=active_system
            )
        
        # Display welcome banner
        console.print(Panel.fit(
            f"[bold cyan]oaichat Interactive Chat[/bold cyan]\n\n"
            f"Profile: [green]{profile_obj.name}[/green]\n"
            f"Model: [green]{active_model}[/green]\n"
            f"Mode: [yellow]{'no-stream' if no_stream else 'streaming'}[/yellow]\n\n"
            f"[dim]Type /exit to quit, /help for commands[/dim]",
            border_style="cyan"
        ))
        
        # Session tracking
        session_prompt_tokens = 0
        session_completion_tokens = 0
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if user_input.startswith("/"):
                    if user_input == "/exit":
                        break
                    elif user_input == "/help":
                        _show_help()
                        continue
                    elif user_input == "/clear":
                        # Clear conversation history
                        conversation.messages.clear()
                        delete_messages(conversation.id)
                        display_success("Conversation history cleared")
                        continue
                    elif user_input.startswith("/system "):
                        active_system = user_input[8:].strip()
                        conversation.system_prompt = active_system
                        update_conversation_system_prompt(conversation.id, active_system)
                        display_success(f"System prompt updated")
                        continue
                    elif user_input.startswith("/model "):
                        active_model = user_input[7:].strip()
                        update_conversation_model(conversation.id, active_model)
                        display_success(f"Switched to model: {active_model}")
                        continue
                    elif user_input == "/save":
                        _save_conversation(client, conversation, active_model)
                        continue
                    elif user_input == "/usage":
                        console.print(
                            f"\n[bold]Session Token Usage[/bold]\n"
                            f"Prompt tokens:     {session_prompt_tokens}\n"
                            f"Completion tokens: {session_completion_tokens}\n"
                            f"Total tokens:      {session_prompt_tokens + session_completion_tokens}\n"
                        )
                        continue
                    else:
                        display_warning(f"Unknown command: {user_input}")
                        display_info("Type /help for available commands")
                        continue
                
                # Add user message to conversation
                add_message(conversation.id, "user", user_input)
                conversation.add_message("user", user_input)
                
                # Prepare messages for API
                messages = conversation.to_openai_messages()
                
                # Get response
                console.print()
                console.print("[bold blue]Assistant[/bold blue]")
                
                if no_stream:
                    content, prompt_tokens, completion_tokens = get_response(
                        client, messages, active_model,
                        temperature=active_temperature,
                        max_tokens=active_max_tokens
                    )
                else:
                    content, prompt_tokens, completion_tokens = stream_response(
                        client, messages, active_model,
                        temperature=active_temperature,
                        max_tokens=active_max_tokens
                    )
                
                # Add assistant response to conversation
                add_message(
                    conversation.id, "assistant", content,
                    token_usage_prompt=prompt_tokens,
                    token_usage_completion=completion_tokens
                )
                conversation.add_message(
                    "assistant", content,
                    token_usage_prompt=prompt_tokens,
                    token_usage_completion=completion_tokens
                )
                
                # Update session totals
                session_prompt_tokens += prompt_tokens
                session_completion_tokens += completion_tokens
                
                # Display token usage
                display_token_usage(prompt_tokens, completion_tokens)
                
            except KeyboardInterrupt:
                console.print("\n")
                if typer.confirm("Exit chat?", default=True):
                    break
                continue
            except Exception as e:
                display_error(f"Error during chat: {str(e)}")
                continue
        
        # Save conversation with title on exit
        if len(conversation.messages) > 0 and not conversation.title:
            _save_conversation(client, conversation, active_model)
        
        # Display goodbye
        console.print("\n[dim]Goodbye![/dim]\n")
        
    except ValueError as e:
        display_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        display_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


@app.command("send")
def send_cmd(
    message: str = typer.Argument(..., help="Message to send"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Profile to use"),
    model: Optional[str] = typer.Option(None, "--model", help="Model to use"),
    system: Optional[str] = typer.Option(None, "--system", help="System prompt"),
    temperature: Optional[float] = typer.Option(None, "--temperature", help="Temperature (0.0-2.0)"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Max tokens"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Don't stream responses"),
    save: bool = typer.Option(False, "--save", help="Save to conversation history"),
):
    """Send a one-off message."""
    try:
        # Validate temperature if provided
        if temperature is not None and not (0.0 <= temperature <= 2.0):
            display_error("Temperature must be between 0.0 and 2.0")
            raise typer.Exit(1)
        
        # Get client and profile
        client, profile_obj = get_client(profile)
        
        # Determine model to use
        active_model = model or profile_obj.default_model
        if not active_model:
            display_error("No model specified. Set a default model or use --model")
            raise typer.Exit(1)
        
        # Determine settings
        active_system = system or profile_obj.system_prompt
        active_temperature = temperature if temperature is not None else profile_obj.temperature
        active_max_tokens = max_tokens if max_tokens is not None else profile_obj.max_tokens
        
        # Prepare messages
        messages = []
        if active_system:
            messages.append({"role": "system", "content": active_system})
        messages.append({"role": "user", "content": message})
        
        # Create conversation if saving
        conversation = None
        if save:
            conversation = create_conversation(
                profile=profile_obj.name,
                model=active_model,
                system_prompt=active_system
            )
            add_message(conversation.id, "user", message)
        
        # Get response
        console.print()
        if no_stream:
            content, prompt_tokens, completion_tokens = get_response(
                client, messages, active_model,
                temperature=active_temperature,
                max_tokens=active_max_tokens
            )
        else:
            content, prompt_tokens, completion_tokens = stream_response(
                client, messages, active_model,
                temperature=active_temperature,
                max_tokens=active_max_tokens
            )
        
        # Save response if requested
        if save and conversation:
            add_message(
                conversation.id, "assistant", content,
                token_usage_prompt=prompt_tokens,
                token_usage_completion=completion_tokens
            )
            # Generate title
            title = generate_title(client, messages, active_model)
            update_title(conversation.id, title)
            display_info(f"Saved as: {title}")
        
        # Display token usage
        display_token_usage(prompt_tokens, completion_tokens)
        
    except ValueError as e:
        display_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        display_error(f"Unexpected error: {str(e)}")
        raise typer.Exit(1)


def _show_help():
    """Show help for interactive commands."""
    console.print("""
[bold]Available Commands:[/bold]

  /exit              Exit the chat
  /help              Show this help message
  /clear             Clear conversation history (start fresh)
  /system <prompt>   Change system prompt
  /model <name>      Switch to a different model
  /save              Force save and generate title
  /usage             Show session token usage
""")


def _save_conversation(client, conversation, model):
    """Save conversation with auto-generated title."""
    try:
        display_info("Generating conversation title...")
        messages = conversation.to_openai_messages()
        title = generate_title(client, messages, model)
        update_title(conversation.id, title)
        display_success(f"Conversation saved: {title}")
    except Exception as e:
        display_warning(f"Could not generate title: {str(e)}")
        display_info(f"Conversation saved with ID: {conversation.id}")
