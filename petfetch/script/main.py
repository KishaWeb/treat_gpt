import rich_click as click
from rich_click.rich_command import RichCommand
import requests
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()

def ask_box(prompt="Your question", gap_lines=1):
    term_width = shutil.get_terminal_size().columns

    console.print(f"[bold cyan]{prompt}[/bold cyan]")

    for _ in range(gap_lines):
        console.print("│")

    console.print("│     ", end="")
    question = input()

    return question

@click.command(cls=RichCommand)
def ask():
    question = ask_box()

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer Your_api",  #put in your api if your using openrouter if not you could easily fix it just ask ai how do i use my own api in this code
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": question}],
    }

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

if __name__ == "__main__":
    ask()
