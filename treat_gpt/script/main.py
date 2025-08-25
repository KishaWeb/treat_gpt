#!/home/arshia/petfetch/.venv/bin/python
import rich_click as click
from rich_click.rich_command import RichCommand
import requests
import toml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from git_comits.commit import get_comits
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

# -----------------------------
# Setup
# -----------------------------
console = Console()
DATA_FILE = Path("questions.toml")
CHAT_FILE = Path("chat_history.toml")
ASCII_FILE = Path("/home/arshia/petfetch/src/ascii-art.txt")
history = InMemoryHistory()

# -----------------------------
# Helpers
# -----------------------------
def load_questions():
    if DATA_FILE.exists():
        data = toml.load(DATA_FILE)
        return data.get("questions", 0)
    return 0

def save_questions(questions):
    with open(DATA_FILE, "w") as f:
        toml.dump({"questions": questions}, f)

def load_chat():
    if CHAT_FILE.exists():
        data = toml.load(CHAT_FILE)
        return data.get("messages", [])
    return [{"role": "system", "content": "You are a helpful assistant."}]

def save_chat(messages):
    with open(CHAT_FILE, "w") as f:
        toml.dump({"messages": messages}, f)

def ask_box(prompt_text="Your question", gap_lines=1):
    # Load ASCII art
    if ASCII_FILE.exists():
        with open(ASCII_FILE, "r") as f:
            ascii_art = f.read()
    else:
        ascii_art = ""

    if ascii_art:
        console.print(Panel(ascii_art, border_style="white", expand=False))

    for _ in range(gap_lines):
        console.print("")

    console.print(Panel(f"[bold cyan]{prompt_text}[/bold cyan]", border_style="white", expand=True))
    return prompt("│     ", history=history)

# -----------------------------
# Main CLI command
# -----------------------------
@click.command(cls=RichCommand)
def ask():
    pushes, _ = get_comits()
    questions = load_questions() + len(pushes) * 5

    if questions <= 0:
        console.print(Panel("[red]Go commit first![/red]", title="No Commits"))
        save_questions(questions)
        return

    console.print(Panel(f"[bold green]Questions Left:[/bold green] {questions}", title="Status"))

    # Load full chat memory
    messages = load_chat()

    # 🔁 Chat loop
    while questions > 0:
        question = ask_box()
        if question.lower().strip() in ["exit", "quit"]:
            console.print(Panel("[yellow]Chat ended.[/yellow]", title="Goodbye 👋"))
            break

        messages.append({"role": "user", "content": question})

        # API call
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": "Bearer place your api key here",  # put your API key
            "Content-Type": "application/json",
        }
        payload = {"model": "deepseek/deepseek-chat", "messages": messages}

        try:
            response = requests.post(url, headers=headers, json=payload).json()
        except requests.exceptions.RequestException as e:
            console.print(Panel(f"[red]Network Error:[/red] {e}", border_style="red"))
            break

        if "error" in response:
            console.print(Panel(f"[red]Error: {response['error']['message']}[/red]", border_style="red"))
            break
        else:
            ans = response["choices"][0]["message"]["content"]

            console.rule("[bold green]Assistant[/bold green]")
            try:
                console.print(Markdown(ans))
            except Exception:
                console.print(ans)
            console.rule("[bold blue]End[/bold blue]")

            # Save assistant reply
            messages.append({"role": "assistant", "content": ans})
            save_chat(messages)

            # Decrement questions
            questions -= 1
            save_questions(questions)

            console.print(Panel(f"[bold yellow]Remaining Questions:[/bold yellow] {questions}", title="Status"))

# -----------------------------
# Run CLI
# -----------------------------
if __name__ == "__main__":
    ask()
