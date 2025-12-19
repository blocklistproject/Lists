"""Tests for src/pipeline.py."""

import tempfile
from pathlib import Path

import pytest

from src.pipeline import (
    BuildResult,
    PipelineResult,
    build_list,
    get_output_path,
    run_pipeline,
    verify_output_consistency,
)


@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "lists": {
            "test": {
                "title": "Test Block List",
                "description": "Test description",
                "status": "stable",
            }
        },
        "formats": {
            "hosts": {
                "output_dir": ".",
                "extension": ".txt",
                "url_template": "https://example.com/{name}.txt",
            },
            "adguard": {
                "output_dir": "adguard",
                "extension": "-ags.txt",
                "url_template": "https://example.com/adguard/{name}-ags.txt",
            },
            "domains": {
                "output_dir": "alt-version",
                "extension": "-nl.txt",
                "url_template": "https://example.com/alt-version/{name}-nl.txt",
            },
            "dnsmasq": {
                "output_dir": "dnsmasq-version",
                "extension": "-dnsmasq.txt",
                "url_template": "https://example.com/dnsmasq-version/{name}-dnsmasq.txt",
            },
        },
    }


class TestGetOutputPath:
    """Tests for get_output_path function."""
    
    def test_hosts_format_root_directory(self, sample_config):
        """Hosts format should output to root directory."""
        path = get_output_path(
            Path("/project"),
            "ads",
            "hosts",
            sample_config["formats"]["hosts"],
        )
        assert path == Path("/project/ads.txt")
    
    def test_adguard_format_subdirectory(self, sample_config):
        """AdGuard format should output to adguard/ subdirectory."""
        path = get_output_path(
            Path("/project"),
            "ads",
            "adguard",
            sample_config["formats"]["adguard"],
        )
        assert path == Path("/project/adguard/ads-ags.txt")
    
    def test_domains_format_subdirectory(self, sample_config):
        """Domains format should output to alt-version/ subdirectory."""
        path = get_output_path(
            Path("/project"),
            "ads",
            "domains",
            sample_config["formats"]["domains"],
        )
        assert path == Path("/project/alt-version/ads-nl.txt")
    
    def test_dnsmasq_format_subdirectory(self, sample_config):
        """Dnsmasq format should output to dnsmasq-version/ subdirectory."""
        path = get_output_path(
            Path("/project"),
            "ads",
            "dnsmasq",
            sample_config["formats"]["dnsmasq"],
        )
        assert path == Path("/project/dnsmasq-version/ads-dnsmasq.txt")


class TestBuildList:
    """Tests for build_list function."""
    
    def test_build_from_hosts_file(self, sample_config):
        """Should build list from hosts format source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Create source file
            source = base_dir / "test.txt"
            source.write_text("0.0.0.0 example.com\n0.0.0.0 test.net\n")
            
            result = build_list(
                sample_config,
                "test",
                base_dir,
                validate=False,
            )
            
            assert result.name == "test"
            assert result.domain_count == 2
            assert "hosts" in result.output_files
    
    def test_build_creates_all_formats(self, sample_config):
        """Should create output files for all formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            source = base_dir / "test.txt"
            source.write_text("0.0.0.0 example.com\n")
            
            result = build_list(
                sample_config,
                "test",
                base_dir,
                validate=False,
            )
            
            assert len(result.output_files) == 4
            
            # Verify files exist
            for path in result.output_files.values():
                assert path.exists()
    
    def test_build_dry_run(self, sample_config):
        """Dry run should not create files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            source = base_dir / "test.txt"
            source.write_text("0.0.0.0 example.com\n")
            
            result = build_list(
                sample_config,
                "test",
                base_dir,
                validate=False,
                dry_run=True,
            )
            
            # Should have output paths but files shouldn't exist
            # (except the source we created)
            adguard_path = result.output_files.get("adguard")
            if adguard_path:
                assert not adguard_path.exists()
    
    def test_build_with_validation(self, sample_config):
        """Should validate domains and report errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Include some invalid domains
            source = base_dir / "test.txt"
            source.write_text(
                "0.0.0.0 valid.com\n"
                "0.0.0.0 localhost\n"  # False positive
                "0.0.0.0 -invalid.com\n"  # Bad syntax
            )
            
            result = build_list(
                sample_config,
                "test",
                base_dir,
                validate=True,
            )
            
            # Should have validation errors
            assert result.validation_errors > 0
            # Valid domains should still be counted
            assert result.domain_count == 1  # Only valid.com
    
    def test_build_applies_allowlist(self, sample_config):
        """Should exclude domains from allowlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            source = base_dir / "test.txt"
            source.write_text(
                "0.0.0.0 block.com\n"
                "0.0.0.0 allow.com\n"
            )
            
            allowlist = base_dir / "allowlist.txt"
            allowlist.write_text("allow.com\n")
            
            result = build_list(
                sample_config,
                "test",
                base_dir,
                allowlist_path=allowlist,
                validate=False,
            )
            
            assert result.domain_count == 1
    
    def test_build_handles_missing_source(self, sample_config):
        """Should handle missing source file gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            result = build_list(
                sample_config,
                "nonexistent",
                base_dir,
                validate=False,
            )
            
            assert result.domain_count == 0


class TestRunPipeline:
    """Tests for run_pipeline function."""
    
    def test_run_pipeline_creates_config(self):
        """Should run pipeline with config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            config_dir = base_dir / "config"
            config_dir.mkdir()
            
            # Create minimal config
            config_path = config_dir / "lists.yml"
            config_path.write_text("""
lists:
  test:
    title: Test List
    status: stable
formats:
  hosts:
    directory: ""
    suffix: ".txt"
  domains:
    directory: "alt-version"
    suffix: "-nl.txt"
""")
            
            # Create source file
            source = base_dir / "test.txt"
            source.write_text("0.0.0.0 example.com\n")
            
            result = run_pipeline(
                config_path,
                base_dir=base_dir,
                validate=False,
            )
            
            assert result.total_lists == 1
            assert result.successful == 1
            assert result.failed == 0
    
    def test_run_pipeline_specific_lists(self):
        """Should only build specified lists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            config_dir = base_dir / "config"
            config_dir.mkdir()
            
            config_path = config_dir / "lists.yml"
            config_path.write_text("""
lists:
  list1:
    status: stable
  list2:
    status: stable
formats:
  hosts:
    directory: ""
    suffix: ".txt"
""")
            
            # Create only list1 source
            (base_dir / "list1.txt").write_text("0.0.0.0 a.com\n")
            
            result = run_pipeline(
                config_path,
                base_dir=base_dir,
                lists=["list1"],
                validate=False,
            )
            
            assert result.total_lists == 1
            assert len(result.results) == 1
            assert result.results[0].name == "list1"


class TestVerifyOutputConsistency:
    """Tests for verify_output_consistency function."""
    
    def test_consistent_outputs(self):
        """Should pass when all formats have same domain count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Create consistent outputs
            (base_dir / "test.txt").write_text("0.0.0.0 a.com\n0.0.0.0 b.com\n")
            
            (base_dir / "adguard").mkdir()
            (base_dir / "adguard" / "test-ags.txt").write_text("||a.com^\n||b.com^\n")
            
            (base_dir / "alt-version").mkdir()
            (base_dir / "alt-version" / "test-nl.txt").write_text("a.com\nb.com\n")
            
            inconsistencies = verify_output_consistency(base_dir)
            
            assert len(inconsistencies) == 0
    
    def test_inconsistent_outputs(self):
        """Should detect when formats have different domain counts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            
            # Create inconsistent outputs
            (base_dir / "test.txt").write_text("0.0.0.0 a.com\n0.0.0.0 b.com\n")  # 2 domains
            
            (base_dir / "adguard").mkdir()
            (base_dir / "adguard" / "test-ags.txt").write_text("||a.com^\n")  # 1 domain!
            
            inconsistencies = verify_output_consistency(base_dir)
            
            assert len(inconsistencies) == 1
            assert inconsistencies[0][0] == "test"


class TestBuildResult:
    """Tests for BuildResult dataclass."""
    
    def test_build_result_fields(self):
        """Should store all fields correctly."""
        result = BuildResult(
            name="test",
            domain_count=100,
            validation_errors=5,
            output_files={"hosts": Path("/test.txt")},
        )
        
        assert result.name == "test"
        assert result.domain_count == 100
        assert result.validation_errors == 5
        assert result.output_files == {"hosts": Path("/test.txt")}


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""
    
    def test_pipeline_result_fields(self):
        """Should store all fields correctly."""
        result = PipelineResult(
            total_lists=10,
            successful=8,
            failed=2,
            results=[],
            errors=["error1", "error2"],
        )
        
        assert result.total_lists == 10
        assert result.successful == 8
        assert result.failed == 2
        assert len(result.errors) == 2
