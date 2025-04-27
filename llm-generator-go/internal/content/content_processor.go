package content

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// ContentProcessor processes content from files in a repository
type ContentProcessor struct {
	repoPath    string
	includeDirs []string
	excludeDirs []string
	fileTypes   []string
}

// Content represents processed content from a file
type Content struct {
	Title       string      `json:"title"`
	Description string      `json:"description"`
	Source      string      `json:"source"`
	Content     string      `json:"content"`
	CodeBlocks  []CodeBlock `json:"code_blocks"`
	Type        string      `json:"type"`
}

// CodeBlock represents a code block in a file
type CodeBlock struct {
	Language  string    `json:"language"`
	Code      string    `json:"code"`
	Embedding []float64 `json:"embedding,omitempty"`
}

// NewContentProcessor creates a new content processor
func NewContentProcessor(repoPath string, includeDirs, excludeDirs, fileTypes []string) *ContentProcessor {
	if excludeDirs == nil {
		excludeDirs = []string{
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
		}
	}

	if fileTypes == nil {
		fileTypes = []string{
			".md",
		}
	}

	return &ContentProcessor{
		repoPath:    repoPath,
		includeDirs: includeDirs,
		excludeDirs: excludeDirs,
		fileTypes:   fileTypes,
	}
}

// GetFiles returns all files in the repository that match the criteria
func (p *ContentProcessor) GetFiles() ([]string, error) {
	var files []string

	err := filepath.Walk(p.repoPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			// Get the directory name
			dirName := info.Name()

			// Skip excluded directories
			for _, excludeDir := range p.excludeDirs {
				if dirName == excludeDir {
					return filepath.SkipDir
				}
			}

			// Only process included directories if specified
			if len(p.includeDirs) > 0 {
				relPath, err := filepath.Rel(p.repoPath, path)
				if err != nil {
					return err
				}

				// Skip if not in included directories
				if relPath != "." {
					included := false
					for _, includeDir := range p.includeDirs {
						if strings.HasPrefix(relPath, includeDir) {
							included = true
							break
						}
					}

					if !included {
						return filepath.SkipDir
					}
				}
			}

			return nil
		}

		// Check file types
		for _, fileType := range p.fileTypes {
			if strings.HasSuffix(path, fileType) {
				files = append(files, path)
				break
			}
		}

		return nil
	})

	if err != nil {
		return nil, fmt.Errorf("failed to walk directory: %w", err)
	}

	return files, nil
}

// ProcessFile processes a file and extracts its content
func (p *ContentProcessor) ProcessFile(filePath string) (Content, error) {
	// Read file content
	fileContent, err := os.ReadFile(filePath)
	if err != nil {
		return Content{}, fmt.Errorf("failed to read file: %w", err)
	}

	// Get file extension
	fileExt := filepath.Ext(filePath)

	// Get relative path
	relPath, err := filepath.Rel(p.repoPath, filePath)
	if err != nil {
		return Content{}, fmt.Errorf("failed to get relative path: %w", err)
	}

	// Process content based on file type
	var processedContent Content
	if fileExt == ".md" {
		processedContent = p.processMarkdown(string(fileContent), relPath)
	} else {
		processedContent = p.processCode(string(fileContent), fileExt, relPath)
	}

	return processedContent, nil
}

// processMarkdown processes markdown content
func (p *ContentProcessor) processMarkdown(content, filePath string) Content {
	// Extract title from first heading
	titleRegex := regexp.MustCompile(`(?m)^#\s+(.+)$`)
	titleMatch := titleRegex.FindStringSubmatch(content)
	title := filepath.Base(filePath)
	if len(titleMatch) > 1 {
		title = titleMatch[1]
	}

	// Extract description from content - using a simpler approach without negative lookahead
	description := "No description available"
	scanner := bufio.NewScanner(strings.NewReader(content))
	for scanner.Scan() {
		line := scanner.Text()
		// Find first non-empty line that doesn't start with #
		if line != "" && !strings.HasPrefix(line, "#") {
			description = strings.TrimSpace(line)
			break
		}
	}

	// Extract code blocks
	codeBlockRegex := regexp.MustCompile("```(\\w+)?\\n(.*?)\\n```")
	codeBlockMatches := codeBlockRegex.FindAllStringSubmatch(content, -1)
	codeBlocks := make([]CodeBlock, 0, len(codeBlockMatches))

	for _, match := range codeBlockMatches {
		language := "text"
		if len(match) > 1 && match[1] != "" {
			language = match[1]
		}
		code := ""
		if len(match) > 2 {
			code = match[2]
		}
		codeBlocks = append(codeBlocks, CodeBlock{
			Language: language,
			Code:     code,
		})
	}

	return Content{
		Title:       title,
		Description: description,
		Source:      filePath,
		Content:     content,
		CodeBlocks:  codeBlocks,
		Type:        "markdown",
	}
}

// processCode processes code content
func (p *ContentProcessor) processCode(content, fileExt, filePath string) Content {
	// Map file extension to language
	languageMap := map[string]string{
		".go":   "go",
		".py":   "python",
		".js":   "javascript",
		".jsx":  "jsx",
		".ts":   "typescript",
		".tsx":  "tsx",
		".html": "html",
		".css":  "css",
		".json": "json",
		".yaml": "yaml",
		".yml":  "yaml",
	}

	language, ok := languageMap[fileExt]
	if !ok {
		language = "text"
	}

	// Extract docstring/comments
	description := ""
	if language == "python" {
		docstringRegex := regexp.MustCompile(`"""(.*?)"""`)
		docstringMatch := docstringRegex.FindStringSubmatch(content)
		if len(docstringMatch) > 1 {
			description = strings.TrimSpace(docstringMatch[1])
		}
	} else if language == "go" {
		// Try to find package comment
		scanner := bufio.NewScanner(strings.NewReader(content))
		for scanner.Scan() {
			line := scanner.Text()
			if strings.HasPrefix(line, "//") {
				description += strings.TrimPrefix(line, "//") + "\n"
			} else if strings.TrimSpace(line) == "" {
				continue
			} else {
				break
			}
		}
		description = strings.TrimSpace(description)
	} else if language == "javascript" || language == "typescript" || language == "jsx" || language == "tsx" {
		commentRegex := regexp.MustCompile(`/\*\*(.*?)\*/`)
		commentMatch := commentRegex.FindStringSubmatch(content)
		if len(commentMatch) > 1 {
			description = strings.TrimSpace(commentMatch[1])
		}
	}

	// Default description if none found
	if description == "" {
		description = fmt.Sprintf("Code file: %s", filePath)
	}

	// Extract filename as title
	title := filepath.Base(filePath)

	return Content{
		Title:       title,
		Description: description,
		Source:      filePath,
		Content:     content,
		CodeBlocks: []CodeBlock{
			{
				Language: language,
				Code:     content,
			},
		},
		Type: "code",
	}
}
