"""seedream tos — TOS object storage commands (upload local files, list buckets)."""
from __future__ import annotations

import typer
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table

from seedream import SeedreamClient
from seedream.exceptions import SeedreamError

from ..console import console, err, info, ok

app = typer.Typer(help="Upload local files to TOS object storage.")


@app.command("buckets")
def buckets(
    profile: str = typer.Option("default", "--profile", help="Credentials profile."),
) -> None:
    """List the TOS buckets available to your AK/SK."""
    client = SeedreamClient(profile=profile)
    try:
        found = client.list_tos_buckets()
    except SeedreamError as exc:
        err(str(exc))
        raise typer.Exit(1)

    console.print()
    if not found:
        info("No buckets found for these credentials.")
        return

    table = Table(title="TOS buckets", show_edge=False, header_style="cyan")
    table.add_column("Name", style="blue")
    table.add_column("Location")
    table.add_column("Created")
    for b in found:
        table.add_row(b.get("name", ""), b.get("location", ""), b.get("creation_date", ""))
    console.print(table)
    console.print("\n  Upload to one:  [cyan]seedream tos upload <file> --bucket <name>[/cyan]\n")


@app.command("upload")
def upload(
    file_path: str = typer.Argument(..., help="Path to a local file to upload."),
    bucket: str = typer.Option("", "--bucket", "-b", help="Target bucket (or set SEEDREAM_TOS_BUCKET)."),
    key: str = typer.Option("", "--key", "-k", help="Object key. Defaults to the filename."),
    private: bool = typer.Option(False, "--private", help="Do not set a public-read ACL."),
    profile: str = typer.Option("default", "--profile", help="Credentials profile."),
) -> None:
    """Upload a local file to a TOS bucket and print its public URL."""
    client = SeedreamClient(profile=profile)

    console.print()
    with Live(Spinner("dots", text="  Uploading to TOS…", style="cyan"),
              console=console, refresh_per_second=4, transient=True):
        try:
            result = client.upload_to_tos(file_path, bucket, key, public=not private)
        except SeedreamError as exc:
            err(str(exc))
            raise typer.Exit(1)

    ok(f"Uploaded to [blue]{result.bucket}[/blue]/{result.key}")
    console.print(f"\n  url: [cyan]{result.url}[/cyan]")
    console.print(f"\n  Use in generate:  [cyan]seedream generate -p '...' --ref {result.url}[/cyan]\n")
