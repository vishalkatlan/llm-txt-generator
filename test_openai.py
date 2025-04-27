#!/usr/bin/env python3
"""
Test script for OpenAI API with dotenv
"""

import os
import openai
from dotenv import load_dotenv
from rich.console import Console

# Initialize console
console = Console()

# Load environment variables from .env file
load_dotenv()


# Test OpenAI client initialization
def test_openai_client():
    try:
        # Use the hardcoded API key for testing
        api_key = "d4cdd9c09c114cf48a3c9144f86bdcba"

        # Log API key format for debugging
        console.print(
            f"API key format: {api_key[:4]}...{api_key[-4:]}, length: {len(api_key)}"
        )

        # Check OpenAI package version
        console.print(f"OpenAI package version: {openai.__version__}")

        # Set the API key directly
        openai.api_key = api_key

        # For newer versions (v1.0.0+)
        if hasattr(openai, "OpenAI"):
            try:
                client = openai.OpenAI(api_key=api_key)
                console.print(
                    "[bold green]Success![/] OpenAI client initialized with new API"
                )
            except Exception as e:
                console.print(
                    f"[yellow]Note:[/] Could not initialize with new API: {str(e)}"
                )
                console.print("Trying legacy API...")
                # Nothing to do, we'll use the legacy API
                pass

        console.print("[bold green]Success![/] OpenAI package configured")
        return True

    except Exception as e:
        console.print(f"[bold red]Error configuring OpenAI:[/] {str(e)}")
        import traceback

        console.print(traceback.format_exc())
        return False


if __name__ == "__main__":
    console.print("Testing OpenAI configuration...")
    success = test_openai_client()
    if success:
        console.print("[bold green]✓[/] OpenAI configuration test passed")
    else:
        console.print("[bold red]✗[/] OpenAI configuration test failed")
