#!/home/arshia/petfetch/.venv/bin/python
import rich_click as click
from rich_click.rich_command import RichCommand
import requests
import shutil
import toml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from git_comits.commit import get_comits

console = Console()
DATA_FILE = Path("questions.toml")


# -----------------------------
# TOML load/save helpers
# -----------------------------
def load_questions():
    if DATA_FILE.exists():
        data = toml.load(DATA_FILE)
        return data.get("questions", 0)
    return 0

def save_questions(questions):
    with open(DATA_FILE, "w") as f:
        toml.dump({"questions": questions}, f)

# -----------------------------
# Ask box function
# -----------------------------
ASCII_FILE = Path("/home/arshia/petfetch/src/ascii-art.txt")

def ask_box(prompt="Your question", gap_lines=1):
    # Load ASCII art
    if ASCII_FILE.exists():
        with open(ASCII_FILE, "r") as f:
            ascii_art = f.read()
    else:
        ascii_art = ""

    # Display ASCII inside a panel with white border and fixed width
    console.print(Panel(ascii_art, border_style="white", expand=False))

    # Add gap lines
    for _ in range(gap_lines):
        console.print("")

    # Show prompt in a panel with white border and full width
    console.print(Panel(f"[bold cyan]{prompt}[/bold cyan]", border_style="white", expand=True))

    # Get user input
    question = console.input("│     ")
    return question
# -----------------------------
# Main CLI command
# -----------------------------
@click.command(cls=RichCommand)
def ask():
    pushes, commits = get_comits()  # separate pushes and commits
    questions = load_questions()

    # Increment questions by 5 per push event
    questions += len(pushes) * 5

    if questions <= 0:
        console.print(
            Panel("[red]Bro, go commit! You can't ask a question if you don't commit.[/red]",
                  title="⚠️ No Commits")
        )
        save_questions(questions)
        return

    # Show total available questions
    console.print(
        Panel(f"[bold green]Total Questions Available:[/bold green] {questions}", title="📊 Questions")
    )

    # Ask the user
    question = ask_box()

    # Call OpenRouter API
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer Your_api",  # put your API key here
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": question}],
    }

    try:
        response = requests.post(url, headers=headers, json=payload).json()

        if "error" in response:
            console.print(
                Panel(f"[red bold]Error:[/red bold] {response['error']['message']}",
                      title="❌ API Error",
                      border_style="red")
            )
        else:
            model = response.get("model", "unknown")
            message = response["choices"][0]["message"]["content"]

            console.rule(f"[bold green]🤖 Assistant (Model: {model})[/bold green]")

            try:
                md = Markdown(message)
                console.print(md)
            except Exception:
                console.print(message)

            console.rule("[bold blue]End[/bold blue]")

    except requests.exceptions.RequestException as e:
        console.print(Panel(f"[red]Error fetching API:[/red] {e}", title="❌ Network Error"))

    # Decrement questions after usage
    questions -= 1
    save_questions(questions)

    # Show remaining questions
    console.print(
        Panel(f"[bold yellow]Remaining Questions:[/bold yellow] {questions}", title="📌 Status")
    )

# -----------------------------
# Run CLI
# -----------------------------
if __name__ == "__main__":
    ask()

#do you like the borders around the comments?
#btw if your not using open router you could probaly easily fix it cause the creator cant afford a api key for every one
