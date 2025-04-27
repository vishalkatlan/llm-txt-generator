#!/usr/bin/env python3
"""
LLM Documentation Generator - A tool for creating LLM-friendly documentation from GitHub repositories
"""

import os
import sys
import argparse
import time
from typing import Optional, List
from rich.console import Console
from rich.progress import Progress
from dotenv import load_dotenv

from src.repo_handler import RepoHandler
from src.content_processor import ContentProcessor
from src.embedding_service import EmbeddingService
from src.formatter import DocFormatter

# Load environment variables
load_dotenv()

console = Console()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate LLM-friendly documentation from GitHub repositories"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate documentation")
    generate_parser.add_argument("--repo", required=True, help="GitHub repository URL")
    generate_parser.add_argument(
        "--output", default="llm.txt", help="Output file path (default: llm.txt)"
    )
    generate_parser.add_argument(
        "--include-dirs",
        nargs="+",
        help="Specific directories to include (default: all)",
    )
    generate_parser.add_argument(
        "--exclude-dirs",
        nargs="+",
        default=["node_modules", ".git", "__pycache__", "venv", ".venv"],
        help="Directories to exclude",
    )
    generate_parser.add_argument(
        "--file-types",
        nargs="+",
        default=[
            ".md",
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
        ],
        help="File types to process",
    )

    return parser.parse_args()


def generate_docs(
    repo_url: str,
    output_path: str = "llm.txt",
    include_dirs: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
    file_types: Optional[List[str]] = None,
):
    """Generate documentation from a GitHub repository."""
    start_time = time.time()

    with Progress() as progress:
        task1 = progress.add_task("[green]Cloning repository...", total=1)

        # Clone repository
        repo_handler = RepoHandler()
        repo_path = repo_handler.clone_repo(repo_url)
        progress.update(task1, advance=1)

        # Extract repository name for output
        repo_name = repo_url.rstrip("/").split("/")[-1]

        task2 = progress.add_task("[green]Processing files...", total=None)
        # Process content
        processor = ContentProcessor(
            repo_path=repo_path,
            include_dirs=include_dirs,
            exclude_dirs=exclude_dirs,
            file_types=file_types,
        )
        files = processor.get_files()
        progress.update(task2, total=len(files))

        contents = []
        for file in files:
            content = processor.process_file(file)
            if content:
                contents.append(content)
            progress.update(task2, advance=1)

        task3 = progress.add_task("[green]Creating embeddings...", total=1)
        # Create embeddings
        embedding_service = EmbeddingService()
        indexed_contents = embedding_service.create_embeddings(contents)
        progress.update(task3, advance=1)

        task4 = progress.add_task("[green]Formatting documentation...", total=1)
        # Format documentation
        formatter = DocFormatter()
        documentation = formatter.format_docs(indexed_contents, repo_url, repo_name)
        progress.update(task4, advance=1)

        # Write to output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(documentation)

    end_time = time.time()
    execution_time = end_time - start_time

    console.print(f"\n✅ [bold green]Documentation generated successfully![/]")
    console.print(f"📝 Output file: [bold]{output_path}[/]")
    console.print(
        f"⏱️ Execution time: [bold]{execution_time:.2f}s[/] ({int(execution_time)}s)"
    )


def main():
    """Main entry point."""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        console.print(
            "[bold red]Error:[/] OPENAI_API_KEY environment variable is not set"
        )
        console.print(
            "Please set your OpenAI API key in .env file or as an environment variable"
        )
        sys.exit(1)

    args = parse_args()

    if args.command == "generate":
        try:
            generate_docs(
                repo_url=args.repo,
                output_path=args.output,
                include_dirs=args.include_dirs,
                exclude_dirs=args.exclude_dirs,
                file_types=args.file_types,
            )
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
            sys.exit(1)
    else:
        console.print("[yellow]Please specify a command.[/]")
        console.print("Run 'python main.py --help' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
