import torch
import torch.nn as nn
import torch.nn.functional as functional
from TransformerBlock import TransformerBlock

class LLM(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_layers, num_heads, ff_dim, max_seq_length):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.pos_embedding = nn.Parameter(torch.randn(1, max_seq_length, embed_dim))
        
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, ff_dim)
            for _ in range(num_layers)
        ])
        
        self.output = nn.Linear(embed_dim, vocab_size)
        self.max_seq_length = max_seq_length

    def forward(self, x, mask=None):
        x = self.embedding(x)
        x = x + self.pos_embedding[:, :x.size(1), :]
        
        for transformer in self.transformer_blocks:
            x = transformer(x, mask)
            
        return self.output(x)

    def generate(self, input_ids, max_length, temperature=0.7):
        self.eval()
        current_ids = input_ids.clone()
        
        with torch.no_grad():
            for _ in range(max_length - len(input_ids[0])):
                outputs = self(current_ids)
                next_token_logits = outputs[:, -1, :] / temperature
                next_token = torch.multinomial(functional.softmax(next_token_logits, dim=-1), 1)
                current_ids = torch.cat([current_ids, next_token], dim=1)
                
                if next_token.item() == self.tokenizer.eos_token_id:
                    break
                    
        return current_ids
