# LLM Generator Go

A Go implementation of a tool for creating LLM-friendly documentation from GitHub repositories.

## Overview

This tool clones a GitHub repository, processes its contents, generates embeddings using OpenAI's API, and creates a comprehensive LLM-friendly documentation file.

## Features

- Clone any public GitHub repository
- Process various file types (Markdown, Go, JavaScript, TypeScript, etc.)
- Generate embeddings for content using OpenAI API
- Create a well-structured documentation file

## Requirements

- Go 1.21 or later
- OpenAI API key

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/llm-generator-go.git
   cd llm-generator-go
   ```

2. Install dependencies:

   ```
   go mod tidy
   ```

3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Build and run the tool:

```bash
go build -o llm-generator ./cmd/main.go
./llm-generator generate --repo https://github.com/username/repository
```

### Command line options

```
Usage:
  llm-generator generate [flags]

Flags:
  --repo string             GitHub repository URL (required)
  --output string           Output file path (default "llm.txt")
  --include-dirs strings    Specific directories to include (default: all)
  --exclude-dirs strings    Directories to exclude (default [node_modules,.git,__pycache__,venv,.venv])
  --file-types strings      File types to process (default [.md,.go,.js,.jsx,.ts,.tsx,.html,.css,.json,.yaml,.yml])
```

## Example

```bash
./llm-generator generate --repo https://github.com/atlanhq/agent-toolkit
```

This will generate a file called `llm.txt` containing the documentation.

## License

MIT
