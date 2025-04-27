package embedding

import (
	"context"
	"fmt"
	"os"

	"github.com/sashabaranov/go-openai"
	"github.com/user/llm-generator-go/internal/content"
)

// EmbeddingService is responsible for creating embeddings for content
type EmbeddingService struct {
	client *openai.Client
	model  openai.EmbeddingModel
}

// NewEmbeddingService creates a new embedding service
func NewEmbeddingService() *EmbeddingService {
	apiKey := os.Getenv("OPENAI_API_KEY")
	client := openai.NewClient(apiKey)
	return &EmbeddingService{
		client: client,
		model:  openai.AdaEmbeddingV2,
	}
}

// CreateEmbeddings creates embeddings for content
func (s *EmbeddingService) CreateEmbeddings(contents []content.Content) ([]content.Content, error) {
	for i := range contents {
		// Create embeddings for code blocks
		for j := range contents[i].CodeBlocks {
			// Skip empty code blocks
			if contents[i].CodeBlocks[j].Code == "" {
				continue
			}

			// Truncate code to fit embedding model limit (8191 tokens)
			code := contents[i].CodeBlocks[j].Code
			if len(code) > 32000 {
				code = code[:32000]
			}

			// Create embedding
			resp, err := s.client.CreateEmbeddings(
				context.Background(),
				openai.EmbeddingRequest{
					Input: []string{code},
					Model: s.model,
				},
			)
			if err != nil {
				return nil, fmt.Errorf("failed to create embedding: %w", err)
			}

			if len(resp.Data) > 0 {
				// Convert []float32 to []float64
				float32Embedding := resp.Data[0].Embedding
				float64Embedding := make([]float64, len(float32Embedding))
				for k, v := range float32Embedding {
					float64Embedding[k] = float64(v)
				}
				contents[i].CodeBlocks[j].Embedding = float64Embedding
			}
		}
	}

	return contents, nil
}
