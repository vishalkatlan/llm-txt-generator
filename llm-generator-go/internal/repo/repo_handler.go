package repo

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/go-git/go-git/v5"
)

// RepoHandler handles repository operations
type RepoHandler struct {
	tempDir string
}

// NewRepoHandler creates a new repository handler
func NewRepoHandler() *RepoHandler {
	return &RepoHandler{}
}

// CloneRepo clones a repository from the given URL
func (h *RepoHandler) CloneRepo(repoURL string) (string, error) {
	// Create a temporary directory for the repository
	tempDir, err := os.MkdirTemp("", "llm-generator-")
	if err != nil {
		return "", fmt.Errorf("failed to create temp directory: %w", err)
	}
	h.tempDir = tempDir

	// Validate repository URL
	if !strings.HasPrefix(repoURL, "https://github.com/") && !strings.HasPrefix(repoURL, "https://gitlab.com/") {
		return "", fmt.Errorf("only GitHub and GitLab repositories are supported")
	}

	// Clone the repository
	_, err = git.PlainClone(tempDir, false, &git.CloneOptions{
		URL:          repoURL,
		Progress:     os.Stdout,
		Depth:        1,
		SingleBranch: true,
	})
	if err != nil {
		return "", fmt.Errorf("failed to clone repository: %w", err)
	}

	return tempDir, nil
}

// GetRepoName extracts the repository name from the URL
func (h *RepoHandler) GetRepoName(repoURL string) string {
	// Remove trailing .git if present
	repoURL = strings.TrimSuffix(repoURL, ".git")

	// Extract repo name from URL
	parts := strings.Split(repoURL, "/")
	if len(parts) < 2 {
		return fmt.Sprintf("repo-%s", time.Now().Format("20060102-150405"))
	}

	return parts[len(parts)-1]
}

// Cleanup removes temporary files
func (h *RepoHandler) Cleanup() error {
	if h.tempDir != "" {
		if err := os.RemoveAll(h.tempDir); err != nil {
			return fmt.Errorf("failed to remove temp directory: %w", err)
		}
	}
	return nil
}

// GetAbsolutePath returns the absolute path of a file in the repository
func (h *RepoHandler) GetAbsolutePath(relativePath string) (string, error) {
	if h.tempDir == "" {
		return "", fmt.Errorf("repository not cloned yet")
	}

	return filepath.Join(h.tempDir, relativePath), nil
}
