"""Seedream CLI — entry point.

Usage:
    seedream auth login
    seedream generate --prompt "..." --size 2K
    seedream generate --prompt "edit ..." --ref path/to/img.png --output out/
    seedream tos buckets
    seedream tos upload ./photo.png --bucket <name>
    seedream models
    seedream ping
    seedream skill install
"""
from __future__ import annotations

import typer

from .commands import auth, generate, models, skill, tos

app = typer.Typer(
    name="seedream",
    help="BytePlus Seedream 4.5 / 5.0 Lite image generation CLI.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

app.add_typer(auth.app,     name="auth",   help="Manage BytePlus credentials.")
app.add_typer(generate.app, name="generate", help="Generate images with Seedream.")
app.add_typer(tos.app,      name="tos",    help="Upload local files to TOS object storage.")
app.add_typer(models.app,   name="models", help="List available Seedream models.")
app.add_typer(skill.app,    name="skill",  help="Install/manage the Claude Code skill.")


@app.command("ping")
def ping(
    profile: str = typer.Option("default", "--profile", help="Credentials profile."),
) -> None:
    """Verify connectivity and credential configuration."""
    from seedream import SeedreamClient
    from seedream.exceptions import SeedreamError

    from .console import console, err, info, ok

    client = SeedreamClient(profile=profile)
    try:
        result = client.ping()
    except SeedreamError as exc:
        err(str(exc))
        raise typer.Exit(1)

    console.print()
    ok(f"Connected  (SDK v{result['version']})")
    info(f"Default model: {result['default_model']}")
    creds = result.get("credentials", {})
    for key, label in [
        ("api_key", "ARK_API_KEY  (generation) "),
        ("ak",      "ARK_AK       (TOS upload) "),
        ("sk",      "ARK_SK       (TOS upload) "),
    ]:
        mark = "[success]✔[/success]" if creds.get(key) else "[error]✖[/error]"
        info(f"{mark}  {label}  {'configured' if creds.get(key) else 'missing'}")
    console.print()


if __name__ == "__main__":
    app()
