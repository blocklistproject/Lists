"""Pipeline orchestration for building blocklists.

This module ties together all the components:
1. Load configuration
2. Parse existing blocklist files (normalize)
3. Merge and deduplicate domains
4. Validate domains
5. Generate output in all formats
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Support both relative and absolute imports
try:
    from .config import get_format_config, get_list_names, load_config
    from .format import write_output
    from .merge import apply_allowlist, sort_domains
    from .normalize import extract_allowlist_from_hosts, parse_file_to_set
    from .validate import validate_domain_set
except ImportError:
    from config import get_format_config, get_list_names, load_config
    from format import write_output
    from merge import apply_allowlist, sort_domains
    from normalize import extract_allowlist_from_hosts, parse_file_to_set
    from validate import validate_domain_set


@dataclass
class BuildResult:
    """Result of building a single list."""
    
    name: str
    domain_count: int
    validation_errors: int
    output_files: dict[str, Path]  # format -> path


@dataclass
class PipelineResult:
    """Result of a full pipeline run."""
    
    total_lists: int
    successful: int
    failed: int
    results: list[BuildResult]
    errors: list[str]


def get_output_path(
    base_dir: Path,
    list_name: str,
    format_name: str,
    format_config: dict[str, Any],
) -> Path:
    """Determine the output path for a list in a given format.
    
    Uses the directory structure from config to preserve existing URLs.
    
    Args:
        base_dir: Base directory (project root)
        list_name: Name of the list (e.g., 'ads', 'malware')
        format_name: Format identifier
        format_config: Format configuration from lists.yml
        
    Returns:
        Path where the output file should be written
    """
    # Config uses output_dir and extension
    directory = format_config.get("output_dir", ".")
    extension = format_config.get("extension", ".txt")
    
    if directory and directory != ".":
        return base_dir / directory / f"{list_name}{extension}"
    else:
        return base_dir / f"{list_name}{extension}"


def build_list(
    config: dict[str, Any],
    list_name: str,
    base_dir: Path,
    source_path: Path | None = None,
    allowlist_path: Path | None = None,
    validate: bool = True,
    dry_run: bool = False,
) -> BuildResult:
    """Build a single blocklist in all output formats.
    
    Args:
        config: Loaded configuration dictionary
        list_name: Name of the list to build
        base_dir: Base directory for output files
        source_path: Override path to source file (default: base_dir/{list_name}.txt)
        allowlist_path: Path to allowlist file (domains to exclude)
        validate: Whether to validate domains
        dry_run: If True, don't write files
        
    Returns:
        BuildResult with statistics and output paths
    """
    list_config = config.get("lists", {}).get(list_name, {})
    
    # Determine source file
    if source_path is None:
        source_path = base_dir / f"{list_name}.txt"
    
    # Parse source domains
    if source_path.exists():
        domains = parse_file_to_set(source_path)
        
        # Also extract allowlist from comments if present
        inline_allowlist = extract_allowlist_from_hosts(source_path)
        if inline_allowlist:
            domains = apply_allowlist(domains, inline_allowlist)
    else:
        domains = set()
    
    # Apply external allowlist if provided
    if allowlist_path and allowlist_path.exists():
        ext_allowlist = parse_file_to_set(allowlist_path)
        domains = apply_allowlist(domains, ext_allowlist)
    
    # Validate domains
    validation_errors = 0
    if validate and domains:
        valid_domains, errors = validate_domain_set(
            domains,
            check_syntax=True,
            check_tld=True,
            check_critical=True,
            strict_tld=False,
        )
        validation_errors = len(errors)
        domains = valid_domains
    
    # Sort for deterministic output
    sorted_domains = sort_domains(domains)
    
    # Get list metadata
    title = list_config.get("title", f"{list_name.title()} Block List")
    description = list_config.get("description", f"Domains blocked for {list_name}")
    
    # Generate outputs in all formats
    output_files: dict[str, Path] = {}
    
    for format_name in ["hosts", "domains", "adguard", "dnsmasq"]:
        format_config = get_format_config(config, format_name)
        if not format_config:
            continue
        
        output_path = get_output_path(base_dir, list_name, format_name, format_config)
        
        # Build URL for header
        url_template = format_config.get("url_template", "")
        url = url_template.replace("{name}", list_name) if url_template else ""
        
        if not dry_run:
            write_output(
                sorted_domains,
                output_path,
                format_name,
                title=title,
                description=description,
                url=url,
            )
        
        output_files[format_name] = output_path
    
    return BuildResult(
        name=list_name,
        domain_count=len(sorted_domains),
        validation_errors=validation_errors,
        output_files=output_files,
    )


def run_pipeline(
    config_path: Path,
    base_dir: Path | None = None,
    source_dir: Path | None = None,
    lists: list[str] | None = None,
    validate: bool = True,
    dry_run: bool = False,
) -> PipelineResult:
    """Run the full build pipeline.
    
    Args:
        config_path: Path to lists.yml configuration
        base_dir: Base directory for output (defaults to config_path's parent)
        source_dir: Directory containing source files (defaults to base_dir)
        lists: Specific lists to build (None = all stable/beta lists)
        validate: Whether to validate domains
        dry_run: If True, don't write files
        
    Returns:
        PipelineResult with statistics and per-list results
    """
    if base_dir is None:
        base_dir = config_path.parent.parent  # Go up from config/ to project root
    
    if source_dir is None:
        source_dir = config_path.parent.parent  # Source files are in project root
    
    config = load_config(config_path)
    
    # Determine which lists to build
    if lists:
        list_names = lists
    else:
        # Build all stable and beta lists by default
        list_names = get_list_names(config, status=["stable", "beta"])
    
    results: list[BuildResult] = []
    errors: list[str] = []
    successful = 0
    failed = 0
    
    for list_name in list_names:
        try:
            # Source file is in source_dir, output goes to base_dir
            source_path = source_dir / f"{list_name}.txt"
            result = build_list(
                config,
                list_name,
                base_dir,
                source_path=source_path,
                validate=validate,
                dry_run=dry_run,
            )
            results.append(result)
            successful += 1
        except Exception as e:
            errors.append(f"{list_name}: {e}")
            failed += 1
    
    return PipelineResult(
        total_lists=len(list_names),
        successful=successful,
        failed=failed,
        results=results,
        errors=errors,
    )


def verify_output_consistency(base_dir: Path) -> list[tuple[str, str]]:
    """Verify that all format versions of each list have the same domain count.
    
    This is a sanity check to ensure the pipeline produced consistent output.
    
    Args:
        base_dir: Base directory containing output files
        
    Returns:
        List of (list_name, error_message) tuples for any inconsistencies
    """
    inconsistencies: list[tuple[str, str]] = []
    
    # Find all hosts files in root
    for hosts_file in base_dir.glob("*.txt"):
        if hosts_file.name.startswith(".") or hosts_file.name in ["README.md", "LICENSE"]:
            continue
        
        list_name = hosts_file.stem
        
        # Get domain counts for each format
        counts: dict[str, int] = {}
        
        # hosts (root)
        if hosts_file.exists():
            counts["hosts"] = len(parse_file_to_set(hosts_file))
        
        # adguard
        adguard_file = base_dir / "adguard" / f"{list_name}-ags.txt"
        if adguard_file.exists():
            counts["adguard"] = len(parse_file_to_set(adguard_file))
        
        # domains
        domains_file = base_dir / "alt-version" / f"{list_name}-nl.txt"
        if domains_file.exists():
            counts["domains"] = len(parse_file_to_set(domains_file))
        
        # dnsmasq
        dnsmasq_file = base_dir / "dnsmasq-version" / f"{list_name}-dnsmasq.txt"
        if dnsmasq_file.exists():
            counts["dnsmasq"] = len(parse_file_to_set(dnsmasq_file))
        
        # Check consistency
        if len(set(counts.values())) > 1:
            inconsistencies.append(
                (list_name, f"Inconsistent counts: {counts}")
            )
    
    return inconsistencies
