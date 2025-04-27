"""
Content Processor module for parsing and extracting content from repository files.
"""

import os
import re
from typing import List, Optional, Dict, Any
from rich.console import Console

console = Console()


class ContentProcessor:
    """Process content from files in a repository."""

    def __init__(
        self,
        repo_path: str,
        include_dirs: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        file_types: Optional[List[str]] = None,
    ):
        """
        Initialize the content processor.

        Args:
            repo_path: Path to the repository
            include_dirs: Directories to include (default: all)
            exclude_dirs: Directories to exclude
            file_types: File types to process
        """
        self.repo_path = repo_path
        self.include_dirs = include_dirs
        self.exclude_dirs = exclude_dirs or [
            "node_modules",
            ".git",
            "__pycache__",
            "venv",
            ".venv",
            ".github",
            ".vscode",
            ".idea",
            ".DS_Store",
            ".env",
            ".env.local",
            ".env.development",
        ]
        self.file_types = file_types or [
            ".md",
        ]

    def get_files(self) -> List[str]:
        """
        Get all files in the repository that match the criteria.

        Returns:
            List of file paths
        """
        files = []

        for root, dirs, filenames in os.walk(self.repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            # Only process included directories if specified
            if self.include_dirs:
                relative_root = os.path.relpath(root, self.repo_path)
                if relative_root != "." and not any(
                    relative_root.startswith(d) for d in self.include_dirs
                ):
                    continue

            for filename in filenames:
                # Skip files that don't match the file types
                if not any(filename.endswith(ext) for ext in self.file_types):
                    continue

                file_path = os.path.join(root, filename)
                files.append(file_path)

        console.print(f"Found {len(files)} files to process")
        return files

    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a file and extract its content.

        Args:
            file_path: Path to the file

        Returns:
            Processed content or None if processing failed
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Get file extension
            _, file_ext = os.path.splitext(file_path)

            # Get relative path
            relative_path = os.path.relpath(file_path, self.repo_path)

            # Process content based on file type
            if file_ext == ".md":
                processed_content = self._process_markdown(content, relative_path)
            else:
                processed_content = self._process_code(content, file_ext, relative_path)

            console.print(f"Processed file: {relative_path}")
            return processed_content
        except Exception as e:
            console.print(
                f"[yellow]Warning:[/] Failed to process file {file_path}: {str(e)}"
            )
            return None

    def _process_markdown(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Process markdown content.

        Args:
            content: Markdown content
            file_path: Relative path to the file

        Returns:
            Processed content
        """
        # Extract title from first heading
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else os.path.basename(file_path)

        # Extract description from content
        description_match = re.search(r"^(?!#)(.+)$", content, re.MULTILINE)
        description = (
            description_match.group(1).strip()
            if description_match
            else "No description available"
        )

        # Extract code blocks
        code_blocks = []
        for match in re.finditer(r"```(\w+)?\n(.*?)\n```", content, re.DOTALL):
            language = match.group(1) or "text"
            code = match.group(2)
            code_blocks.append({"language": language, "code": code})

        return {
            "title": title,
            "description": description,
            "source": file_path,
            "content": content,
            "code_blocks": code_blocks,
            "type": "markdown",
        }

    def _process_code(
        self, content: str, file_ext: str, file_path: str
    ) -> Dict[str, Any]:
        """
        Process code content.

        Args:
            content: Code content
            file_ext: File extension
            file_path: Relative path to the file

        Returns:
            Processed content
        """
        # Map file extension to language
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "jsx",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
        }

        language = language_map.get(file_ext, "text")

        # Extract docstring/comments
        description = ""
        if language == "python":
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                description = docstring_match.group(1).strip()
        elif language in ["javascript", "typescript", "jsx", "tsx"]:
            comment_match = re.search(r"/\*\*(.*?)\*/", content, re.DOTALL)
            if comment_match:
                description = comment_match.group(1).strip()

        # Default description if none found
        if not description:
            description = f"Code file: {file_path}"

        # Extract filename as title
        title = os.path.basename(file_path)

        return {
            "title": title,
            "description": description,
            "source": file_path,
            "content": content,
            "code_blocks": [{"language": language, "code": content}],
            "type": "code",
        }
