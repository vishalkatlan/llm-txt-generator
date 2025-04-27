# LLM Documentation Generator

A tool similar to Context7 that generates documentation from GitHub repositories for use with LLMs.

## Features

- Clones GitHub repositories
- Extracts and parses content from markdown, code, and documentation files
- Creates embeddings for semantic search
- Generates formatted documentation for LLM consumption
- Provides a command-line interface for easy usage

## Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/llm-txt-generator.git
cd llm-txt-generator

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to add your OpenAI API key
```

## Usage

```bash
# Generate documentation for a repository
python main.py generate --repo https://github.com/username/repository
```

## Configuration

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
```

## License

MIT
