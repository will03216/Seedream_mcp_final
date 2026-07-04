"""seedream models — list available models."""
from __future__ import annotations

import typer

from seedream import SeedreamClient
from seedream.exceptions import SeedreamError

from ..console import console, err
from ..formatters import models_table

app = typer.Typer(help="List available Seedream models.")


@app.callback(invoke_without_command=True)
def models(
    ctx: typer.Context,
    profile: str = typer.Option("default", "--profile", help="Credentials profile."),
) -> None:
    """List all available Seedream models and their capabilities."""
    if ctx.invoked_subcommand is not None:
        return

    client = SeedreamClient(profile=profile)
    try:
        data = client.list_models()
    except SeedreamError as exc:
        err(str(exc))
        raise typer.Exit(1)

    console.print()
    models_table(data)
