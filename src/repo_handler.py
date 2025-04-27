"""
Repository Handler module for cloning and managing GitHub repositories.
"""

import os
import tempfile
import shutil
from typing import Optional
import git
from rich.console import Console

console = Console()


class RepoHandler:
    """Handle GitHub repository operations like cloning and cleaning up."""

    def __init__(self):
        """Initialize the repository handler."""
        self.temp_dir = None

    def clone_repo(self, repo_url: str) -> str:
        """
        Clone a GitHub repository to a temporary directory.

        Args:
            repo_url: URL of the GitHub repository

        Returns:
            Path to the cloned repository
        """
        # Clean up any previous temporary directory
        self.cleanup()

        # Create a new temporary directory
        self.temp_dir = tempfile.mkdtemp()

        try:
            console.print(
                f"Cloning repository [bold]{repo_url}[/]... This may take a while..."
            )
            start_time = os.times()

            # Clone the repository
            git.Repo.clone_from(repo_url, self.temp_dir, depth=1)

            end_time = os.times()
            elapsed = (end_time.user - start_time.user) * 1000

            console.print(f"Repository cloned [bold]{repo_url}[/] in {elapsed:.0f}ms")

            return self.temp_dir
        except git.GitCommandError as e:
            self.cleanup()
            raise RuntimeError(f"Failed to clone repository: {str(e)}")

    def cleanup(self):
        """Remove temporary directory and its contents."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None
