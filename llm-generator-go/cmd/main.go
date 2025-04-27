package main

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
	"github.com/spf13/cobra"
	"github.com/user/llm-generator-go/internal/content"
	"github.com/user/llm-generator-go/internal/embedding"
	"github.com/user/llm-generator-go/internal/formatter"
	"github.com/user/llm-generator-go/internal/repo"
)

func main() {
	// Load environment variables from .env file
	godotenv.Load()

	// Check if OpenAI API key is set
	if os.Getenv("OPENAI_API_KEY") == "" {
		fmt.Println("Error: OPENAI_API_KEY environment variable is not set")
		fmt.Println("Please set your OpenAI API key in .env file or as an environment variable")
		os.Exit(1)
	}

	var rootCmd = &cobra.Command{
		Use:   "llm-generator",
		Short: "Generate LLM-friendly documentation from GitHub repositories",
		Long:  `A tool for creating LLM-friendly documentation from GitHub repositories`,
	}

	var generateCmd = &cobra.Command{
		Use:   "generate",
		Short: "Generate documentation",
		Run: func(cmd *cobra.Command, args []string) {
			repoURL, _ := cmd.Flags().GetString("repo")
			output, _ := cmd.Flags().GetString("output")
			includeDirs, _ := cmd.Flags().GetStringSlice("include-dirs")
			excludeDirs, _ := cmd.Flags().GetStringSlice("exclude-dirs")
			fileTypes, _ := cmd.Flags().GetStringSlice("file-types")

			generateDocs(repoURL, output, includeDirs, excludeDirs, fileTypes)
		},
	}

	generateCmd.Flags().String("repo", "", "GitHub repository URL (required)")
	generateCmd.Flags().String("output", "llm.txt", "Output file path (default: llm.txt)")
	generateCmd.Flags().StringSlice("include-dirs", []string{}, "Specific directories to include (default: all)")
	generateCmd.Flags().StringSlice("exclude-dirs", []string{"node_modules", ".git", "__pycache__", "venv", ".venv"}, "Directories to exclude")
	generateCmd.Flags().StringSlice("file-types", []string{".md", ".go", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json", ".yaml", ".yml"}, "File types to process")
	generateCmd.MarkFlagRequired("repo")

	rootCmd.AddCommand(generateCmd)

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func generateDocs(repoURL, outputPath string, includeDirs, excludeDirs, fileTypes []string) {
	fmt.Println("Generating documentation from repository:", repoURL)

	// Clone repository
	fmt.Println("Cloning repository...")
	repoHandler := repo.NewRepoHandler()
	repoPath, err := repoHandler.CloneRepo(repoURL)
	if err != nil {
		fmt.Printf("Error cloning repository: %v\n", err)
		os.Exit(1)
	}

	// Extract repository name for output
	repoName := repoHandler.GetRepoName(repoURL)

	// Process content
	fmt.Println("Processing files...")
	processor := content.NewContentProcessor(repoPath, includeDirs, excludeDirs, fileTypes)
	files, err := processor.GetFiles()
	if err != nil {
		fmt.Printf("Error getting files: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Found %d files to process\n", len(files))
	contents := make([]content.Content, 0)
	for _, file := range files {
		processedContent, err := processor.ProcessFile(file)
		if err != nil {
			fmt.Printf("Warning: Failed to process file %s: %v\n", file, err)
			continue
		}
		contents = append(contents, processedContent)
		fmt.Printf("Processed file: %s\n", file)
	}

	// Create embeddings
	fmt.Println("Creating embeddings...")
	embeddingService := embedding.NewEmbeddingService()
	indexedContents, err := embeddingService.CreateEmbeddings(contents)
	if err != nil {
		fmt.Printf("Error creating embeddings: %v\n", err)
		os.Exit(1)
	}

	// Format documentation
	fmt.Println("Formatting documentation...")
	docFormatter := formatter.NewDocFormatter()
	documentation := docFormatter.FormatDocs(indexedContents, repoURL, repoName)

	// Write to output file
	err = os.WriteFile(outputPath, []byte(documentation), 0644)
	if err != nil {
		fmt.Printf("Error writing output file: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("\n✅ Documentation generated successfully!")
	fmt.Printf("📝 Output file: %s\n", outputPath)
}
