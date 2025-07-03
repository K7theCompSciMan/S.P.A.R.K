import re
import tiktoken
from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn
UNK = "<|unk|>"
EOT = "<|endoftext|>"


class WordTokenizer:
    def __init__(self, vocab):
        vocab.extend([EOT, UNK])
        vocabulary = {token: integer for integer, token in enumerate(vocab)}
        self.str_to_int = vocabulary
        self.int_to_str = {i: s for s, i in vocabulary.items()}

    def encode(self, text):
        preprocess = re.split(r'([,.:;?_!"()\']|--|\s)', text)

        preprocess = [item.strip() for item in preprocess if item.strip()]
        preprocess = [item if item in self.str_to_int else UNK for item in preprocess]
        ids = [self.str_to_int[x] for x in preprocess]
        return ids

    def decode(self, ids):
        text = " ".join([self.int_to_str[x] for x in ids])
        text = re.sub(r'\s+([,.?!"()\'])', r"\1", text)
        return text


# im not good enough to make my own BPE, so just using tiktoken wrapper
class BPE:
    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("gpt2")

    def encode(self, text):
        return self.tokenizer.encode(text, allowed_special={EOT})

    def decode(self, ids):
        return self.tokenizer.decode(ids)


# using pytorch dataset and dataloader too...
class GPTDataset(Dataset):
    def __init__(self, text, tokenizer, max_length, stride):
        self.input_ids = []
        self.target_ids = []
        token_ids = tokenizer.encode(text)
        for i in range(0, len(token_ids) - max_length, stride):
            self.input_ids.append(torch.tensor(token_ids[i : i + max_length]))
            self.target_ids.append(torch.tensor(token_ids[i + 1 : i + 1 + max_length]))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.target_ids[idx]


def create_dataloader(
    text,
    batch_size=4,
    max_length=256,
    stride=128,
    shuffle=True,
    drop_last=True,
    num_workers=0,
):
    tokenizer = BPE()

    dataset = GPTDataset(text, tokenizer, max_length, stride)

    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=drop_last,
        num_workers=num_workers,
    )

    return dataloader


class EmbeddingLayer:
    def __init__(self, vocab_size, embedding_dim):
        self.dict = torch.nn.Embedding(vocab_size, embedding_dim) #does the random init too
        self.shape = self.dict.weight.shape
    def __getitem__(self, key):
        return self.dict(torch.tensor([key]))

    def __str__(self):
        return self.dict.weight.__str__()
    def embed(self, input_ids):
        return self.dict(input_ids)

class DataPreprocessor:
    def __init__(self, text_file='sample.txt', batch_size=4,
    max_length=256,
    stride=128,
    shuffle=True,
    drop_last=True,
    num_workers=0,
    vocab_size=50257,
    embedding_dim=256,
    ):
        self.raw_text = ''
        with open(text_file, 'r') as f:
            self.raw_text = f.read()
        self.stride  = stride
        self.shuffle = shuffle
        self.drop_last = drop_last
        self.num_workers = num_workers
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.batch_size = batch_size
        self.max_length = max_length
        self.context_size = self.max_length
        self.token_embeddings_layer = EmbeddingLayer(vocab_size, embedding_dim)
        self.pos_embeddings = EmbeddingLayer(self.context_size, embedding_dim).embed(torch.arange(self.context_size))

        self.dataloader = create_dataloader(self.raw_text, batch_size=self.batch_size, max_length=self.max_length, stride=self.max_length, shuffle=self.shuffle, drop_last=self.drop_last, num_workers=self.num_workers)
        self.data_iter = iter(self.dataloader)
        
    def preprocess(self):
        inputs, targets = next(self.data_iter)

        # print("Input Ids:", inputs)
        # print("inputs_size:", inputs.shape)

        token_embeddings = self.token_embeddings_layer.embed(inputs)
        # print("Token Embeddings:", token_embeddings)
        # print("Token Embeddings size:", token_embeddings.shape)
        input_embeddings = token_embeddings + self.pos_embeddings
        # print("input Embeddings:", input_embeddings)
        # print("input Embeddings size:", input_embeddings.shape)
        return input_embeddings, targets

class Attention:
    class SimpleAttention:
        def __init__(self, inputs):
            self.inputs = inputs
            self.attention_scores = torch.zeros(inputs.shape[0], inputs.shape[0])
        def forward(self):
            self.attention_scores = self.inputs @ self.inputs.T
            self.attention_weights = torch.softmax(self.attention_scores, dim=-1)
            
            self.context_vecs = self.attention_weights @ self.inputs
            return self.context_vecs
        
    class SelfAttention(nn.Module):
        def __init__(self, d_in, d_out, qkv_bias=False):
            super().__init__()
            self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
            self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias)
            self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
        
        def forward(self, x):
            keys = self.W_key(x)
            queries = self.W_query(x)
            values = self.W_value(x)
            
            self.attention_scores = queries @ keys.T
            self.attention_weights = torch.softmax(self.attention_scores / keys.shape[-1]**0.5, dim=-1)

            return self.attention_weights @ values
    class CausalAttention(nn.Module):
        def __init__(self, d_in, d_out, context_length, dropout, qkv_bias=False):
            super().__init__()
            self.d_out = d_out
            self.W_query = nn.Linear(d_in, d_out, bias=qkv_bias)
            self.W_key = nn.Linear(d_in, d_out, bias=qkv_bias)
            self.W_value = nn.Linear(d_in, d_out, bias=qkv_bias)
            self.dropout = nn.Dropout(dropout)
            self.register_buffer("mask", torch.triu(torch.ones(context_length, context_length), diagonal=1))
        def forward(self, x):
            b, num_tokens, d_in = x.shape
            keys = self.W_key(x)
            queries = self.W_query(x)
            values = self.W_value(x)
            
            self.attention_scores = queries @ keys.transpose(1, 2)
            self.attention_scores.masked_fill_(self.mask.bool()[:num_tokens, :num_tokens], -torch.inf) #safety with :num_tokens in case num_tokens < context_length
            self.attention_weights = torch.softmax(self.attention_scores / keys.shape[-1]**0.5, dim=-1)
            self.attention_weights = self.dropout(self.attention_weights)
            
            self.context_vec = self.attention_weights @ values
            return self.context_vec


datapreprocessor = DataPreprocessor()
inputs, targets = datapreprocessor.preprocess()

test_inputs  = torch.tensor(
  [[0.43, 0.15, 0.89], # Your     (x^1)
   [0.55, 0.87, 0.66], # journey  (x^2)
   [0.57, 0.85, 0.64], # starts   (x^3)
   [0.22, 0.58, 0.33], # with     (x^4)
   [0.77, 0.25, 0.10], # one      (x^5)
   [0.05, 0.80, 0.55]] # step     (x^6)
)
batch = torch.stack((test_inputs, test_inputs), dim=0)

attention = Attention.CausalAttention(batch.shape[-1], 2, batch.shape[1], 0.0)
print(attention.forward(batch))
print(attention.context_vec.shape)