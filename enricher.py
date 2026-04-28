"""CSV product enricher using Anthropic Claude API."""
import argparse, json, sys, time
from pathlib import Path
import anthropic
import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from prompts import build_prompt

load_dotenv()
console = Console()


def load_csv(path: str) -> pd.DataFrame:
    """Load CSV and validate required columns exist."""
    df = pd.read_csv(path)
    if missing := {"sku", "title", "description"} - set(df.columns):
        raise ValueError(f"Missing columns: {missing}")
    return df


def call_claude(client: anthropic.Anthropic, prompt: str, model: str, verbose: bool) -> str:
    """Call Claude with exponential backoff retry (max 2 attempts)."""
    if verbose:
        console.print(f"[dim]--- Prompt ---\n{prompt}[/dim]")
    for attempt in range(2):
        try:
            msg = client.messages.create(
                model=model, max_tokens=512, messages=[{"role": "user", "content": prompt}]
            )
            raw = msg.content[0].text
            if verbose:
                console.print(f"[dim]--- Response ---\n{raw}[/dim]")
            return raw
        except (anthropic.APIError, anthropic.APITimeoutError) as e:
            wait = 2 ** attempt
            console.print(f"[yellow]Retry {attempt + 1}/2 in {wait}s ({e})[/yellow]")
            if attempt < 1:
                time.sleep(wait)
            else:
                raise


def parse_response(raw: str) -> dict:
    """Parse and strictly validate Claude JSON response fields and types."""
    data = json.loads(raw)
    for f in ("seo_tags", "category", "enhanced_description"):
        if not isinstance(data.get(f), str) or not data[f]:
            raise ValueError(f"Invalid type for {f}: got {type(data.get(f)).__name__}")
    score = data.get("readability_score")
    if not isinstance(score, (int, float)) or not (0 <= score <= 10):
        raise ValueError(f"Invalid type for readability_score: got {type(score).__name__}")
    return data


def enrich_row(client: anthropic.Anthropic, row: pd.Series, model: str, verbose: bool) -> dict | None:
    """Enrich one row; returns None and logs a warning on any failure."""
    try:
        return parse_response(call_claude(client, build_prompt(row), model, verbose))
    except Exception as e:
        console.print(f"[yellow]Skipped '{row.get('sku', '?')}': {e}[/yellow]")
        return None


def _apply_results(df: pd.DataFrame, results: list[dict | None]) -> None:
    """Write enrichment results into df columns in place."""
    for col in ("seo_tags", "category", "enhanced_description", "readability_score"):
        df[col] = [r.get(col) if r else None for r in results]


def main() -> None:
    """
    Parse CLI args, enrich each CSV row via Claude,
    save output, and print a summary.
    """
    p = argparse.ArgumentParser(description="Enrich product CSVs with Claude AI.")
    p.add_argument("--input", required=True, help="Input CSV path")
    p.add_argument("--output", required=True, help="Output CSV path")
    p.add_argument("--model", default="claude-haiku-4-5-20251001", help="Anthropic model ID")
    p.add_argument("--verbose", "-v", action="store_true", help="Print prompts and responses")
    args = p.parse_args()
    if Path(args.output).exists():
        console.print(f"[yellow]Warning: overwriting {args.output}[/yellow]")
    df = load_csv(args.input)
    client = anthropic.Anthropic(timeout=30.0)
    results: list[dict | None] = []
    start = time.time()
    try:
        with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as prog:
            task = prog.add_task(f"Enriching {len(df)} rows...", total=len(df))
            for _, row in df.iterrows():
                result = enrich_row(client, row, args.model, args.verbose)
                if result:
                    console.print(f"[green]OK[/green] {row.get('sku', '?')}")
                results.append(result)
                prog.advance(task)
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted — saving partial results...[/yellow]")
        partial = df.iloc[: len(results)].copy()
        _apply_results(partial, results)
        partial.to_csv(args.output + ".partial.csv", index=False)
        console.print(f"[yellow]Partial output: {args.output}.partial.csv[/yellow]")
        sys.exit(1)
    _apply_results(df, results)
    df.to_csv(args.output, index=False)
    n_ok = sum(1 for r in results if r)
    n_skip = len(results) - n_ok
    elapsed = round(time.time() - start, 1)
    console.rule("Summary")
    console.print(f"[green]✓ Successfully enriched: {n_ok}/{len(df)} rows[/green]")
    if n_skip:
        console.print(f"[red]✗ Skipped (errors): {n_skip}/{len(df)} rows[/red]")
    console.print(f"[cyan]⏱  Total elapsed: {elapsed}s[/cyan]")
    console.print(f"[cyan]📁 Output saved to: {args.output}[/cyan]")
    console.rule()


if __name__ == "__main__":
    main()
