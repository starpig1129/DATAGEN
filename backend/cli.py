import typer
import uvicorn
import sys
import os

# Add backend to sys.path to make it importable
backend_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

app = typer.Typer()


@app.command()
def run(
    host: str = typer.Option("0.0.0.0", help="Host to bind the server to."),
    port: int = typer.Option(8000, help="Port to run the server on."),
    reload: bool = typer.Option(True, help="Enable auto-reloading for development."),
):
    """
    Starts the FastAPI backend server.
    """
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    app()