#!/usr/bin/env python3
"""
Block List Project - Build CLI

Command-line interface for building blocklists.

Usage:
    python build.py                    # Build all lists
    python build.py --list ads         # Build specific list
    python build.py --dry-run          # Preview without writing
    python build.py --validate         # Run validation checks
    python build.py --verbose          # Show detailed output
"""

import sys
import time
from pathlib import Path

import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import (
    BuildResult,
    PipelineResult,
    build_list,
    run_pipeline,
    verify_output_consistency,
)
from config import load_config, get_list_names


# Project root is where this script lives
PROJECT_ROOT = Path(__file__).parent


@click.group(invoke_without_command=True)
@click.option("--list", "-l", "list_name", multiple=True, help="Specific list(s) to build")
@click.option("--dry-run", "-n", is_flag=True, help="Preview without writing files")
@click.option("--validate", "-v", is_flag=True, help="Run validation checks")
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.option("--strict", is_flag=True, help="Fail on warnings")
@click.option("--output-dir", "-o", type=click.Path(), help="Output directory (default: project root)")
@click.pass_context
def cli(ctx, list_name, dry_run, validate, verbose, strict, output_dir):
    """Block List Project - Build Tool
    
    Build and format blocklists for various DNS blocking applications.
    """
    ctx.ensure_object(dict)
    ctx.obj["dry_run"] = dry_run
    ctx.obj["validate"] = validate
    ctx.obj["verbose"] = verbose
    ctx.obj["strict"] = strict
    ctx.obj["output_dir"] = Path(output_dir) if output_dir else PROJECT_ROOT
    
    # If no subcommand, run build
    if ctx.invoked_subcommand is None:
        ctx.invoke(build, list_name=list_name)


@cli.command()
@click.option("--list", "-l", "list_name", multiple=True, help="Specific list(s) to build")
@click.pass_context
def build(ctx, list_name):
    """Build blocklists from source files."""
    start_time = time.time()
    
    dry_run = ctx.obj.get("dry_run", False)
    validate = ctx.obj.get("validate", False)
    verbose = ctx.obj.get("verbose", False)
    strict = ctx.obj.get("strict", False)
    output_dir = ctx.obj.get("output_dir", PROJECT_ROOT)
    
    if dry_run:
        click.secho("DRY RUN - no files will be written", fg="yellow")
    
    # Config is always in PROJECT_ROOT/config
    config_path = PROJECT_ROOT / "config" / "lists.yml"
    if not config_path.exists():
        click.secho(f"Error: Config file not found: {config_path}", fg="red")
        sys.exit(1)
    
    # Determine which lists to build
    config = load_config(config_path)
    if list_name:
        lists_to_build = list(list_name)
        # Validate list names
        available = get_list_names(config)
        for name in lists_to_build:
            if name not in available:
                click.secho(f"Error: Unknown list '{name}'", fg="red")
                click.echo(f"Available lists: {', '.join(sorted(available))}")
                sys.exit(1)
    else:
        lists_to_build = None  # Build all
    
    # Run the pipeline
    if verbose:
        click.echo(f"Building lists: {lists_to_build or 'all'}")
        click.echo(f"Output directory: {output_dir}")
    
    result = run_pipeline(
        config_path=config_path,
        base_dir=output_dir,
        lists=lists_to_build,
        dry_run=dry_run,
        validate=validate,
    )
    
    # Display results
    _display_results(result, verbose, strict)
    
    elapsed = time.time() - start_time
    click.echo(f"\nCompleted in {elapsed:.2f}s")
    
    # Exit with error if strict mode and there were warnings/errors
    if strict and (result.errors or result.warnings):
        sys.exit(1)


@cli.command()
@click.argument("list_name")
@click.pass_context
def single(ctx, list_name):
    """Build a single blocklist."""
    output_dir = ctx.obj.get("output_dir", PROJECT_ROOT)
    dry_run = ctx.obj.get("dry_run", False)
    validate = ctx.obj.get("validate", False)
    verbose = ctx.obj.get("verbose", False)
    
    config_path = PROJECT_ROOT / "config" / "lists.yml"
    config = load_config(config_path)
    available = get_list_names(config)
    
    if list_name not in available:
        click.secho(f"Error: Unknown list '{list_name}'", fg="red")
        click.echo(f"Available lists: {', '.join(sorted(available))}")
        sys.exit(1)
    
    result = build_list(
        config=config,
        list_name=list_name,
        base_dir=output_dir,
        dry_run=dry_run,
        validate=validate,
    )
    
    _display_build_result(result, verbose)


@cli.command()
@click.pass_context
def verify(ctx):
    """Verify all output formats are consistent."""
    output_dir = ctx.obj.get("output_dir", PROJECT_ROOT)
    verbose = ctx.obj.get("verbose", False)
    
    config_path = PROJECT_ROOT / "config" / "lists.yml"
    config = load_config(config_path)
    lists_to_check = get_list_names(config)
    
    click.echo("Verifying output consistency...")
    
    all_consistent = True
    for list_name in lists_to_check:
        is_consistent, mismatches = verify_output_consistency(list_name, output_dir)
        
        if is_consistent:
            if verbose:
                click.secho(f"  ✓ {list_name}", fg="green")
        else:
            all_consistent = False
            click.secho(f"  ✗ {list_name}", fg="red")
            for mismatch in mismatches:
                click.echo(f"    {mismatch}")
    
    if all_consistent:
        click.secho("\nAll outputs are consistent!", fg="green")
    else:
        click.secho("\nSome outputs are inconsistent!", fg="red")
        sys.exit(1)


@cli.command("list")
def list_available():
    """Show available blocklists."""
    config_path = PROJECT_ROOT / "config" / "lists.yml"
    config = load_config(config_path)
    
    click.echo("\nAvailable blocklists:\n")
    
    lists = config.get("lists", {})
    for name, info in sorted(lists.items()):
        status = info.get("status", "unknown")
        status_color = {"stable": "green", "beta": "yellow", "deprecated": "red"}.get(status, "white")
        categories = ", ".join(info.get("categories", []))
        
        click.echo(f"  {name}")
        click.secho(f"    Status: {status}", fg=status_color)
        if categories:
            click.echo(f"    Categories: {categories}")
        if "description" in info:
            click.echo(f"    {info['description']}")
    
    click.echo(f"\nTotal: {len(lists)} lists")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show statistics for built lists."""
    output_dir = ctx.obj.get("output_dir", PROJECT_ROOT)
    
    config_path = PROJECT_ROOT / "config" / "lists.yml"
    config = load_config(config_path)
    lists = get_list_names(config)
    
    click.echo("\nBlocklist Statistics:\n")
    click.echo(f"{'List':<20} {'Domains':>12} {'Status':<10}")
    click.echo("-" * 45)
    
    total_domains = 0
    for list_name in sorted(lists):
        # Check the hosts format file (root directory)
        hosts_file = output_dir / f"{list_name}.txt"
        if hosts_file.exists():
            with open(hosts_file, "r", encoding="utf-8") as f:
                # Count non-comment, non-empty lines
                count = sum(1 for line in f if line.strip() and not line.startswith("#"))
            status = click.style("✓", fg="green")
        else:
            count = 0
            status = click.style("✗", fg="red")
        
        total_domains += count
        click.echo(f"{list_name:<20} {count:>12,} {status}")
    
    click.echo("-" * 45)
    click.echo(f"{'Total':<20} {total_domains:>12,}")


def _display_results(result: PipelineResult, verbose: bool, strict: bool):
    """Display pipeline results."""
    click.echo("\n" + "=" * 50)
    click.echo("Build Summary")
    click.echo("=" * 50)
    
    # Success count (use the pre-computed values from PipelineResult)
    successful = result.successful
    failed = result.failed
    
    if failed == 0:
        click.secho(f"✓ {successful} lists built successfully", fg="green")
    else:
        click.secho(f"✓ {successful} lists built successfully", fg="green")
        click.secho(f"✗ {failed} lists failed", fg="red")
    
    # Total domains
    total_domains = sum(r.domain_count for r in result.results)
    click.echo(f"Total domains: {total_domains:,}")
    
    # Errors
    if result.errors:
        click.secho(f"\nErrors ({len(result.errors)}):", fg="red")
        for error in result.errors[:10]:
            click.echo(f"  - {error}")
        if len(result.errors) > 10:
            click.echo(f"  ... and {len(result.errors) - 10} more")
    
    # Verbose: show each list
    if verbose:
        click.echo("\nPer-list details:")
        for r in result.results:
            _display_build_result(r, verbose=False)


def _display_build_result(result: BuildResult, verbose: bool):
    """Display a single build result."""
    # Successful if it has domains
    is_success = result.domain_count > 0
    if is_success:
        status = click.style("✓", fg="green")
    else:
        status = click.style("✗", fg="red")
    
    click.echo(f"  {status} {result.name}: {result.domain_count:,} domains")
    
    if result.validation_errors and verbose:
        click.secho(f"      {result.validation_errors} validation errors", fg="yellow")


if __name__ == "__main__":
    cli(obj={})
