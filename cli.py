import os
import sys
from pathlib import Path

# 調整路徑以支援模組導入
backend_path = str(Path(__file__).resolve().parent / "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from rich import print as rprint
from src.system import MultiAgentSystem

def main():
    """
    Main function to run the interactive agent CLI.
    """
    rprint("[bold green]Welcome to the Interactive Agent CLI![/bold green]")
    rprint("Type 'exit' or 'quit' to end the session.")

    # Initialize the multi-agent system
    system = MultiAgentSystem()

    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["exit", "quit"]:
                rprint("[bold yellow]Exiting interactive session.[/bold yellow]")
                break
            # Using the system's run method to get the final response from the agent
            system.run(user_input)

        except KeyboardInterrupt:
            rprint("\n[bold yellow]Interrupted by user. Exiting...[/bold yellow]")
            break
        except Exception as e:
            rprint(f"[bold red]An error occurred:[/bold red] {e}")

if __name__ == "__main__":
    main()