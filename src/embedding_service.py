"""
Embedding Service module for generating embeddings and performing semantic search.
"""

import os
import sys
from typing import List, Dict, Any, Optional
import numpy as np
from tqdm import tqdm
from rich.console import Console
import openai
from dotenv import load_dotenv

load_dotenv()

console = Console()


class EmbeddingService:
    """Service for generating embeddings and performing semantic search."""

    def __init__(self, model: str = "text-embedding-ada-002"):
        """
        Initialize the embedding service.

        Args:
            model: OpenAI embedding model to use
        """
        self.model = model
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key == "sk-placeholder" or api_key == "your_openai_api_key_here":
                console.print(
                    "[bold red]Error:[/] Please provide a valid OpenAI API key"
                )
                console.print("You are using a placeholder API key")
                sys.exit(1)

            # Set API key directly on the openai module
            openai.api_key = api_key

            # For debugging
            console.print(f"Using OpenAI package version: {openai.__version__}")

        except Exception as e:
            console.print(f"[bold red]Error initializing OpenAI client:[/] {str(e)}")
            console.print(
                "Make sure you have a valid OpenAI API key and the correct version of the OpenAI package"
            )
            sys.exit(1)
        self.embeddings = []
        self.contents = []
        self.max_tokens = 8000  # Approximate max tokens for embeddings

    def _truncate_text(self, text: str, max_chars: int = 32000) -> str:
        """
        Truncate text to a maximum number of characters.
        This is a simple replacement for tiktoken encoding.

        Args:
            text: Text to truncate
            max_chars: Maximum number of characters

        Returns:
            Truncated text
        """
        if len(text) <= max_chars:
            return text
        return text[:max_chars]

    def create_embeddings(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create embeddings for the given contents.

        Args:
            contents: List of content dictionaries

        Returns:
            Contents with added embeddings
        """
        if not contents:
            console.print("[yellow]Warning:[/] No contents to embed")
            return []

        # Store contents for later use
        self.contents = contents

        # Create embeddings for each content
        console.print("Creating embeddings for [bold]content titles[/]...")
        try:
            title_embeddings = self._create_embeddings(
                [content["title"] for content in contents]
            )

            # Create embeddings for code blocks
            console.print("Creating embeddings for [bold]code blocks[/]...")
            code_block_embeddings = []

            for content in contents:
                for code_block in content.get("code_blocks", []):
                    # Truncate code if too long
                    code_text = code_block["code"]
                    code_text = self._truncate_text(code_text)

                    embedding = self._get_embedding(code_text)
                    code_block_embeddings.append(embedding)

            # Store all embeddings
            self.embeddings = title_embeddings + code_block_embeddings

            # Add embeddings to content
            for i, content in enumerate(contents):
                content["title_embedding"] = title_embeddings[i].tolist()

                embedding_index = len(title_embeddings)
                for j in range(len(content.get("code_blocks", []))):
                    content["code_blocks"][j]["embedding"] = code_block_embeddings[
                        embedding_index - len(title_embeddings) + j
                    ].tolist()

            console.print(
                f"Created embeddings for {len(contents)} content items and {len(code_block_embeddings)} code blocks"
            )
            return contents
        except Exception as e:
            console.print(f"[bold red]Error creating embeddings:[/] {str(e)}")
            # For debugging
            import traceback

            console.print(traceback.format_exc())
            sys.exit(1)

    def _create_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Create embeddings for a list of texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding arrays
        """
        embeddings = []

        for text in tqdm(texts):
            embedding = self._get_embedding(text)
            embeddings.append(embedding)

        return embeddings

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding array
        """
        try:
            # Make sure text is not empty
            if not text or text.isspace():
                return np.zeros(1536)

            # Handle both new and legacy OpenAI API versions
            if hasattr(openai, "Embedding") or hasattr(openai, "embeddings"):
                # New API (v1.0.0+)
                if hasattr(openai, "Embedding"):
                    response = openai.Embedding.create(input=text, model=self.model)
                else:
                    response = openai.embeddings.create(input=text, model=self.model)

                embedding = response.data[0].embedding
            else:
                # Legacy API (pre v1.0.0)
                response = openai.Embedding.create(input=text, model=self.model)
                embedding = response["data"][0]["embedding"]

            return np.array(embedding)
        except Exception as e:
            console.print(f"[yellow]Warning:[/] Failed to get embedding: {str(e)}")
            # Return a zero vector as fallback
            return np.zeros(1536)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for most relevant content items based on query.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of most relevant content items
        """
        if not self.embeddings or not self.contents:
            console.print(
                "[yellow]Warning:[/] No embeddings or contents available for search"
            )
            return []

        # Get query embedding
        query_embedding = self._get_embedding(query)

        # Calculate similarities
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((i, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top k results
        content_indices = set()
        results = []

        for i, similarity in similarities[
            : top_k * 2
        ]:  # Get more results to handle duplicates
            if i < len(self.contents):
                # Title embedding
                content_index = i
            else:
                # Code block embedding
                code_block_index = i - len(self.contents)
                content_index = code_block_index // len(
                    self.contents[0].get("code_blocks", [])
                )

            if content_index not in content_indices and len(results) < top_k:
                content_indices.add(content_index)
                results.append(self.contents[content_index])

        return results

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
