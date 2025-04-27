package formatter

import (
	"fmt"
	"strings"
	"time"

	"github.com/user/llm-generator-go/internal/content"
)

// DocFormatter formats documentation
type DocFormatter struct{}

// NewDocFormatter creates a new document formatter
func NewDocFormatter() *DocFormatter {
	return &DocFormatter{}
}

// FormatDocs formats documentation for LLM consumption
func (f *DocFormatter) FormatDocs(contents []content.Content, repoURL, repoName string) string {
	var doc strings.Builder

	// Add header
	doc.WriteString(fmt.Sprintf("# %s Documentation\n\n", repoName))
	doc.WriteString(fmt.Sprintf("Repository: %s\n", repoURL))
	doc.WriteString(fmt.Sprintf("Generated: %s\n\n", time.Now().Format("2006-01-02 15:04:05")))
	doc.WriteString("## Contents\n\n")

	// Add table of contents
	for i, c := range contents {
		doc.WriteString(fmt.Sprintf("%d. [%s](#%d-%s)\n", i+1, c.Title, i+1, slugify(c.Title)))
	}

	doc.WriteString("\n---\n\n")

	// Add content
	for i, c := range contents {
		doc.WriteString(fmt.Sprintf("## %d. %s\n\n", i+1, c.Title))
		doc.WriteString(fmt.Sprintf("**Source:** %s\n\n", c.Source))
		doc.WriteString(fmt.Sprintf("%s\n\n", c.Description))

		if len(c.CodeBlocks) > 0 {
			for j, block := range c.CodeBlocks {
				doc.WriteString(fmt.Sprintf("### Code Block %d\n\n", j+1))
				doc.WriteString(fmt.Sprintf("```%s\n%s\n```\n\n", block.Language, block.Code))
			}
		}

		doc.WriteString("---\n\n")
	}

	return doc.String()
}

// slugify creates a URL-friendly slug from a string
func slugify(s string) string {
	s = strings.ToLower(s)
	s = strings.ReplaceAll(s, " ", "-")
	s = strings.ReplaceAll(s, ".", "")
	s = strings.ReplaceAll(s, ",", "")
	s = strings.ReplaceAll(s, ":", "")
	s = strings.ReplaceAll(s, ";", "")
	s = strings.ReplaceAll(s, "!", "")
	s = strings.ReplaceAll(s, "?", "")
	s = strings.ReplaceAll(s, "(", "")
	s = strings.ReplaceAll(s, ")", "")
	s = strings.ReplaceAll(s, "[", "")
	s = strings.ReplaceAll(s, "]", "")
	s = strings.ReplaceAll(s, "{", "")
	s = strings.ReplaceAll(s, "}", "")
	return s
}
