from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import time

console = Console()


def boot():

    console.print(
        Panel.fit(
            "[bold cyan]KAREN AI v3.0[/bold cyan]",
            border_style="cyan"
        )
    )

    tasks = [
        "Loading Identity",
        "Loading Long-Term Memory",
        "Loading Conversation",
        "Connecting to Ollama",
        "Initializing Voice"
    ]

    for task in track(tasks):

        time.sleep(0.5)

    console.print()

    console.print(
        "[bold green]Good to see you again, Sarvagna![/bold green]"
    )

    console.print(
        "[bold cyan]Karen is Online.[/bold cyan]\n"
    )