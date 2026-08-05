"""seedream generate — submit image generation jobs."""
from __future__ import annotations

import typer
from rich.live import Live
from rich.spinner import Spinner

from seedream import SeedreamClient
from seedream.exceptions import SeedreamError

from ..console import console, err, ok
from ..formatters import images_panel

app = typer.Typer(help="Generate images with Seedream 4.5 / 5.0 Lite / 5.0 Pro.")


@app.callback(invoke_without_command=True)
def generate(
    ctx: typer.Context,
    prompt: str = typer.Option(..., "--prompt", "-p", help="Image description / edit instruction."),
    model: str = typer.Option("", "--model", "-m", help="Model or alias: 4.5 | 5.0-lite | 5.0-pro."),
    size: str = typer.Option("", "--size", "-s", help="1K | 2K | 4K | adaptive | WxH (default 2K)."),
    ref: list[str] | None = typer.Option(
        None, "--ref", "-r",
        help="Reference image (URL or local path). Repeatable. Local files auto-upload to TOS.",
    ),
    bucket: str = typer.Option("", "--bucket", help="TOS bucket for local --ref uploads (or SEEDREAM_TOS_BUCKET)."),
    seed: int | None = typer.Option(None, "--seed", help="Random seed for reproducibility."),
    guidance_scale: float | None = typer.Option(None, "--guidance-scale", "-g", help="Prompt adherence 1.0–20.0."),
    sequential: bool = typer.Option(False, "--sequential", help="Generate a consistent multi-panel image set."),
    num_images: int = typer.Option(1, "--num-images", "-n", help="Images in sequential mode."),
    optimize_prompt: bool = typer.Option(False, "--optimize-prompt", help="Let the API optimize the prompt."),
    watermark: bool = typer.Option(False, "--watermark", help="Add a watermark to outputs."),
    output_format: str = typer.Option("", "--output-format", help="png | jpeg (5.0 Pro / 5.0 Lite only)."),
    layer_decomposition: bool = typer.Option(
        False, "--layer-decomposition",
        help="Split the --ref image into separate layers (5.0 Pro only; needs --ref).",
    ),
    output: str = typer.Option("", "--output", "-o", help="Directory to download the image(s) into."),
    profile: str = typer.Option("default", "--profile", help="Credentials profile."),
) -> None:
    """Generate image(s) with Seedream. Synchronous — prints the finished URLs.

    Text-to-image needs only --prompt. For editing / reference / composition,
    pass one or more --ref (local paths are uploaded to TOS automatically).
    Use --output to also download the results locally.

    --layer-decomposition splits one --ref image into its component layers on
    Seedream 5.0 Pro; the prompt must say how many layers and give each a
    <bbox>left top right bottom</bbox> on a 0–1000 scale.
    """
    if ctx.invoked_subcommand is not None:
        return

    client = SeedreamClient(profile=profile)
    console.print()

    # Resolve reference images: local paths → TOS upload, URLs pass through.
    image_urls: list[str] = []
    for r in ref or []:
        if r.startswith(("http://", "https://")):
            image_urls.append(r)
            continue
        with Live(Spinner("dots", text=f"  Uploading {r} to TOS…", style="cyan"),
                  console=console, refresh_per_second=8, transient=True):
            try:
                up = client.upload_to_tos(r, bucket)
            except SeedreamError as exc:
                err(str(exc))
                raise typer.Exit(1)
        ok(f"Uploaded reference: [dim]{up.url}[/dim]")
        image_urls.append(up.url)

    spinner_text = "  Decomposing into layers…" if layer_decomposition else "  Generating…"
    with Live(Spinner("dots", text=spinner_text, style="cyan"),
              console=console, refresh_per_second=8, transient=True):
        try:
            if output:
                result = client.generate_and_download(
                    prompt, output,
                    model=model, size=size, image_urls=image_urls or None,
                    seed=seed, guidance_scale=guidance_scale,
                    sequential=sequential, num_images=num_images,
                    optimize_prompt=optimize_prompt, watermark=watermark,
                    output_format=output_format,
                    layer_decomposition=layer_decomposition,
                )
            else:
                result = client.generate(
                    prompt,
                    model=model, size=size, image_urls=image_urls or None,
                    seed=seed, guidance_scale=guidance_scale,
                    sequential=sequential, num_images=num_images,
                    optimize_prompt=optimize_prompt, watermark=watermark,
                    output_format=output_format,
                    layer_decomposition=layer_decomposition,
                )
        except SeedreamError as exc:
            err(str(exc))
            raise typer.Exit(1)

    ok(f"Generated {len(result.images)} image(s)  [model={result.model}  mode={result.mode}]")
    console.print()
    images_panel(result)
    console.print()
