"""DPX-CSharp CLI — Hexagonal Architecture Scanner for C# / .NET."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from pattern_detector.adapters.outbound.persistence.html_report_formatter import HtmlReportFormatter
from pattern_detector.application.detection_service import DetectionService
from pattern_detector.domain.detection import DetectionReport

app = typer.Typer(
    name="dpx-csharp",
    help="🎯 DPX-CSharp — Hexagonal Architecture, GoF Patterns & Concurrency Scanner for C# / .NET",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


def _print_detection_summary(report: DetectionReport, verbose: bool = False) -> None:
    project = Path(report.project_path).name

    console.print(Panel.fit(
        f"[bold magenta]DPX-CSharp Architecture & Pattern Engine[/bold magenta]\n"
        f"[dim]Target:[/dim] [yellow]{project}[/yellow]",
        border_style="magenta",
    ))

    console.print(
        f" [dim]Scan Summary:[/dim] [bold]{report.scanned_files_count}[/bold] files in "
        f"[bold green]{report.elapsed_seconds:.4f}s[/bold green]  "
    )

    summary = report.summary_by_category
    if not summary:
        console.print("[yellow]No patterns detected.[/yellow]")
        return

    t = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    t.add_column("Category", style="dim", width=28)
    t.add_column("Detections", justify="right")
    for cat, cnt in sorted(summary.items(), key=lambda x: -x[1]):
        t.add_row(cat, str(cnt))
    console.print(t)

    for i, d in enumerate(report.detections[:40 if not verbose else 200], 1):
        loc_str = f"{d.primary_location}" if d.primary_location else "N/A"
        console.print(
            f"\n[bold]#{i} {d.pattern_type.value}[/bold] on [cyan]{d.target_kind}[/cyan] "
            f"[yellow]{d.target_name}[/yellow]"
        )
        console.print(f"├── 📍 Location: {loc_str}")
        console.print(f"├── 🎯 Confidence: [bold]{d.confidence.percentage_str}[/bold] [{d.level.value}]")
        console.print(f"├── 📝 Summary: {d.summary}")
        console.print(f"└── 🔎 Evidence Trail ({len(d.evidences)} heuristics):")
        for ev in d.evidences:
            console.print(f"    └── +{int(ev.weight * 100)}% ({ev.rule_code}) {ev.description}")


@app.command("scan")
def scan(
    target: str = typer.Argument(..., help="Path to C# project directory (.sln, .csproj, or source folder)"),
    html: Optional[Path] = typer.Option(None, "-H", "--html", help="Output HTML Architecture HUD report path"),
    exclude: Optional[list[str]] = typer.Option(None, "-e", "--exclude", help="Directories to exclude (repeatable)"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Show all detections"),
) -> None:
    """Scan C# / .NET project for architectural patterns, safety hazards, and code smells."""
    service = DetectionService()
    report = service.scan(target, excludes=list(exclude) if exclude else None, verbose=verbose)
    _print_detection_summary(report, verbose=verbose)

    if html:
        formatter = HtmlReportFormatter()
        html_content = formatter.format(report)
        html.parent.mkdir(parents=True, exist_ok=True)
        html.write_text(html_content, encoding="utf-8")
        console.print(f"\n[bold green]✓[/bold green] Architecture HUD saved → [cyan]{html}[/cyan]")


@app.command("rules")
def list_rules() -> None:
    """List all 46 C# / .NET architecture pattern rules."""
    from pattern_detector.domain.pattern import PATTERN_CATALOG

    t = Table(title="🎯 DPX-CSharp Rules Catalog (46 Rules)", box=box.ROUNDED, header_style="bold magenta")
    t.add_column("Category", style="cyan", width=24)
    t.add_column("Rule Name", style="bold yellow", width=36)
    t.add_column("Description", style="white")

    for ptype, entry in PATTERN_CATALOG.items():
        t.add_row(entry.category.value, entry.name, entry.description)
    console.print(t)


@app.command("version")
def show_version() -> None:
    """Show DPX-CSharp version."""
    console.print("[bold magenta]DPX-CSharp[/bold magenta] version [bold green]0.1.0[/bold green] (46 rules, GoF 23/23)")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
