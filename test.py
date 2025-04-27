#!/usr/bin/env python3
"""
Test script for LLM Documentation Generator.
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console

from src.repo_handler import RepoHandler
from src.content_processor import ContentProcessor
from src.embedding_service import EmbeddingService
from src.formatter import DocFormatter

# Load environment variables
load_dotenv()

console = Console()


def test_repo_handler():
    """Test repository handler functionality."""
    console.print("[bold]Testing Repository Handler[/]")

    repo_handler = RepoHandler()
    repo_url = "https://github.com/atlanhq/agent-toolkit"

    try:
        repo_path = repo_handler.clone_repo(repo_url)
        console.print(f"Repository cloned successfully at: {repo_path}")

        # Clean up
        repo_handler.cleanup()
        console.print("Repository cleaned up successfully")

        return True
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        return False


def test_content_processor(repo_url="https://github.com/atlanhq/agent-toolkit"):
    """Test content processor functionality."""
    console.print("[bold]Testing Content Processor[/]")

    repo_handler = RepoHandler()

    try:
        repo_path = repo_handler.clone_repo(repo_url)

        processor = ContentProcessor(
            repo_path=repo_path,
            include_dirs=None,
            exclude_dirs=["node_modules", ".git", "__pycache__"],
            file_types=[".md"],
        )

        files = processor.get_files()
        console.print(f"Found {len(files)} files")

        if files:
            content = processor.process_file(files[0])
            console.print(f"Processed file: {os.path.basename(files[0])}")
            console.print(f"Title: {content.get('title')}")
            console.print(f"Code blocks: {len(content.get('code_blocks', []))}")

        # Clean up
        repo_handler.cleanup()
        console.print("Repository cleaned up successfully")

        return True
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        return False


def test_full_pipeline(repo_url="https://github.com/atlanhq/agent-toolkit"):
    """Test the full pipeline with a small repository."""
    console.print("[bold]Testing Full Pipeline[/]")

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[bold red]Error:[/] OPENAI_API_KEY environment variable is not set"
        )
        console.print("Skipping full pipeline test")
        return False

    repo_handler = RepoHandler()

    try:
        repo_path = repo_handler.clone_repo(repo_url)

        processor = ContentProcessor(
            repo_path=repo_path,
            include_dirs=None,
            exclude_dirs=["node_modules", ".git", "__pycache__"],
            file_types=[".md"],
        )

        files = processor.get_files()
        console.print(f"Found {len(files)} files")

        contents = []
        for file in files[:2]:  # Process only first 2 files for testing
            content = processor.process_file(file)
            if content:
                contents.append(content)

        embedding_service = EmbeddingService()
        indexed_contents = embedding_service.create_embeddings(contents)

        formatter = DocFormatter()
        repo_name = repo_url.rstrip("/").split("/")[-1]
        documentation = formatter.format_docs(indexed_contents, repo_url, repo_name)

        # Write to output file
        with open("test_output.txt", "w", encoding="utf-8") as f:
            f.write(documentation)

        console.print(f"Generated documentation written to: test_output.txt")

        # Clean up
        repo_handler.cleanup()
        console.print("Repository cleaned up successfully")

        return True
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        return False


def main():
    """Run tests."""
    console.print("[bold green]LLM Documentation Generator Tests[/]")

    test_results = {
        "repo_handler": test_repo_handler(),
        "content_processor": test_content_processor(),
        "full_pipeline": test_full_pipeline(),
    }

    console.print("\n[bold]Test Results:[/]")
    for test, result in test_results.items():
        status = "[bold green]PASS[/]" if result else "[bold red]FAIL[/]"
        console.print(f"{test}: {status}")

    # Exit with error code if any test failed
    if not all(test_results.values()):
        console.print("\n[bold red]Some tests failed.[/]")
        sys.exit(1)
    else:
        console.print("\n[bold green]All tests passed successfully![/]")
        sys.exit(0)


if __name__ == "__main__":
    main()
