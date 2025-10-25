"""
Example script demonstrating the Docling pipeline for parsing, cleaning, and tagging codebases.

Usage:
    python -m backend.examples.test_docling_pipeline <repo_url> [git_ref]

Examples:
    # Analyze a small Python project
    python -m backend.examples.test_docling_pipeline https://github.com/psf/requests

    # Analyze specific branch
    python -m backend.examples.test_docling_pipeline https://github.com/user/repo main

    # Test with a local directory
    python -m backend.examples.test_docling_pipeline /path/to/local/repo
"""

import asyncio
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_docling_pipeline(repo_url: str, git_ref: str = "main"):
    """Test the Docling pipeline on a repository."""
    from backend.services.repository_analyzer import RepositoryAnalyzer

    logger.info("=" * 80)
    logger.info("Testing Docling Pipeline")
    logger.info("=" * 80)
    logger.info(f"Repository: {repo_url}")
    logger.info(f"Git ref: {git_ref}")
    logger.info("")

    try:
        # Initialize analyzer with Docling
        analyzer = RepositoryAnalyzer(
            repo_url=repo_url,
            git_ref=git_ref,
            use_docling=True,
            max_repo_size_mb=500,
        )

        logger.info("Step 1: Full analysis (clone + parse + clean + tag)")
        logger.info("-" * 80)

        # Run full analysis
        result = await analyzer.analyze_full()

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("ANALYSIS SUMMARY")
        logger.info("=" * 80)

        logger.info(f"\nRepository: {result['repository_url']}")
        logger.info(f"Branch/Tag: {result['git_ref']}")
        logger.info(f"Analysis Mode: {result['analysis_mode']}")

        # Structure info
        structure = result["structure"]
        logger.info(f"\nRepository Structure:")
        logger.info(f"  Total files: {structure['file_count']}")
        logger.info(
            f"  Total size: {structure['total_size_bytes'] / 1024 / 1024:.2f} MB"
        )
        logger.info(f"  Languages detected: {', '.join(structure['languages'])}")

        # Parsed data info
        parsed = result["parsed"]
        if "summary" in parsed:
            summary = parsed["summary"]
            logger.info(f"\nParsing Results:")
            logger.info(f"  Successfully parsed: {summary['successfully_parsed']}")
            logger.info(f"  Failed to parse: {summary['failed_to_parse']}")
            logger.info(f"  Success rate: {summary['parse_success_rate']:.1f}%")

        # Entry points
        if "entry_points" in parsed and parsed["entry_points"]:
            logger.info(f"\nEntry Points Detected:")
            for entry in parsed["entry_points"][:5]:  # Show first 5
                logger.info(f"  - {entry}")

        # Sample tagged files
        if "files" in parsed and parsed["files"]:
            logger.info(f"\nSample Parsed Files (first 5):")
            for file_data in parsed["files"][:5]:
                if "error" not in file_data:
                    logger.info(f"\n  File: {file_data['file_path']}")
                    logger.info(f"    Type: {file_data.get('content_type', 'unknown')}")

                    if "tags" in file_data:
                        tags = file_data["tags"]
                        logger.info(f"    Language: {tags.get('language', [])}")
                        logger.info(f"    Framework: {tags.get('framework', [])}")
                        logger.info(f"    Purpose: {tags.get('purpose', 'unknown')}")
                        logger.info(
                            f"    Complexity: {tags.get('complexity', 'unknown')}"
                        )

                    if "code_blocks" in file_data:
                        logger.info(f"    Code blocks: {len(file_data['code_blocks'])}")

        # Save detailed results to JSON
        output_file = Path("docling_analysis_result.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        logger.info(f"\n✓ Full analysis results saved to: {output_file}")
        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise


async def test_local_directory(directory_path: str):
    """Test the Docling pipeline on a local directory (no git clone needed)."""
    from backend.services.docling_pipeline import DoclingPipeline

    logger.info("=" * 80)
    logger.info("Testing Docling Pipeline on Local Directory")
    logger.info("=" * 80)
    logger.info(f"Directory: {directory_path}")
    logger.info("")

    try:
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        # Initialize pipeline
        pipeline = DoclingPipeline(
            enable_code_enrichment=True,
            enable_formula_enrichment=False,
        )

        logger.info("Running parse -> clean -> tag pipeline...")

        # Run full pipeline
        result = await pipeline.process_pipeline(dir_path)

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE RESULTS")
        logger.info("=" * 80)

        summary = result["summary"]
        logger.info(f"\nProcessing Summary:")
        logger.info(f"  Total files: {summary['total_files']}")
        logger.info(f"  Successfully parsed: {summary['successfully_parsed']}")
        logger.info(f"  Failed: {summary['failed_to_parse']}")
        logger.info(f"  Success rate: {summary['parse_success_rate']:.1f}%")

        if result.get("entry_points"):
            logger.info(f"\nEntry Points:")
            for entry in result["entry_points"]:
                logger.info(f"  - {entry}")

        # Save results
        output_file = Path("docling_pipeline_result.json")
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)

        logger.info(f"\n✓ Pipeline results saved to: {output_file}")
        logger.info("\n" + "=" * 80)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return result

    except Exception as e:
        logger.error(f"Pipeline test failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    path_or_url = sys.argv[1]
    git_ref = sys.argv[2] if len(sys.argv) > 2 else "main"

    # Check if it's a local directory or remote URL
    if Path(path_or_url).exists():
        # Local directory
        asyncio.run(test_local_directory(path_or_url))
    else:
        # Assume it's a git URL
        asyncio.run(test_docling_pipeline(path_or_url, git_ref))


if __name__ == "__main__":
    main()
