"""Rich table/output formatters for CLI commands."""
from __future__ import annotations

from rich.table import Table

from .console import console


def models_table(data: dict) -> None:
    table = Table(title="Available Models", show_lines=True, header_style="bold cyan")
    table.add_column("Model ID", style="blue", no_wrap=True)
    table.add_column("Label")
    table.add_column("Alias")
    table.add_column("Sizes")
    table.add_column("Features")

    for m in data.get("models", []):
        features = ", ".join(k for k, v in m.get("features", {}).items() if v) or "—"
        table.add_row(
            m["model_id"],
            m["label"],
            m["alias"],
            ", ".join(m["sizes"]),
            features,
        )

    console.print(table)
    console.print(f"\n  Default: [blue]{data['default_model']}[/blue]\n")


def images_panel(result) -> None:
    """Print the generated images from a GenerateResult."""
    for idx, img in enumerate(result.images, start=1):
        line = f"  [success]✔[/success]  Image {idx}"
        if img.size:
            line += f"  [dim]{img.size}[/dim]"
        console.print(line)
        if img.local_path:
            console.print(f"       saved: [blue]{img.local_path}[/blue]")
        if img.url:
            console.print(f"       [url]{img.url}[/url]")
        elif img.b64_json:
            console.print("       [dim](base64 payload)[/dim]")
