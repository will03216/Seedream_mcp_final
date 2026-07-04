"""seedream auth — credential management commands."""
from __future__ import annotations

import typer
from rich.prompt import Prompt

from seedream import SeedreamClient
from seedream.credentials import (
    clear_credentials,
    credentials_configured,
    write_credentials,
)
from seedream.exceptions import SeedreamError

from ..console import console, err, info, ok, warn

app = typer.Typer(help="Manage BytePlus credentials.")


@app.command("login")
def login(
    profile: str = typer.Option("default", help="Credentials profile name."),
) -> None:
    """Interactively store ARK_API_KEY (and optional ARK_AK/ARK_SK) in ~/.seedream/credentials."""
    console.print("\n[bold]Seedream — credential setup[/bold]")
    console.print("Credentials are stored in [cyan]~/.seedream/credentials[/cyan] (chmod 600).\n")
    console.print("Find your keys at: [url]https://console.byteplus.com/iam/[/url]\n")

    api_key = Prompt.ask("  ARK_API_KEY  (ModelArk bearer token)", password=True)
    ak = Prompt.ask("  ARK_AK       (IAM Access Key — for local reference uploads, optional)",
                    default="", show_default=False)
    sk = Prompt.ask("  ARK_SK       (IAM Secret Key — for local reference uploads, optional)",
                    password=True, default="", show_default=False)

    if not api_key:
        err("ARK_API_KEY is required. Aborting.")
        raise typer.Exit(1)

    write_credentials(api_key.strip(), ak.strip(), sk.strip(), profile=profile)
    ok(f"Credentials saved to ~/.seedream/credentials  [profile: {profile}]")

    info("Verifying credentials with seedream ping…")
    try:
        result = SeedreamClient(api_key=api_key.strip()).ping()
        ok(f"Connection OK  (SDK v{result['version']})")
    except SeedreamError as exc:
        warn(f"Saved, but ping failed: {exc}")


@app.command("check")
def check(
    profile: str = typer.Option("default", help="Credentials profile name."),
) -> None:
    """Check which credentials are currently configured."""
    status = credentials_configured(profile=profile)
    console.print(f"\n[bold]Credential status[/bold]  (profile: [cyan]{profile}[/cyan])\n")

    for key, label in [
        ("api_key", "ARK_API_KEY  (image generation) "),
        ("ak",      "ARK_AK       (TOS upload, optional)"),
        ("sk",      "ARK_SK       (TOS upload, optional)"),
    ]:
        mark = "[success]✔[/success]" if status[key] else "[error]✖[/error]"
        state = "configured" if status[key] else "missing"
        console.print(f"  {mark}  {label}  [dim]{state}[/dim]")

    if status["api_key"]:
        console.print("\n  [success]Ready to generate.[/success]")
        if not (status["ak"] and status["sk"]):
            console.print("  [dim]ARK_AK/ARK_SK unset — needed only to upload local reference images.[/dim]\n")
    else:
        console.print("\n  [error]Missing:[/error] ARK_API_KEY")
        console.print("  Run [cyan]seedream auth login[/cyan] to configure.\n")
        raise typer.Exit(1)


@app.command("logout")
def logout(
    profile: str = typer.Option("default", help="Credentials profile to remove."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
) -> None:
    """Remove stored credentials for a profile."""
    if not yes:
        typer.confirm(f"Remove credentials for profile '{profile}'?", abort=True)
    existed = clear_credentials(profile=profile)
    if existed:
        ok(f"Credentials removed for profile '{profile}'.")
    else:
        warn("No credentials file found — nothing to remove.")
