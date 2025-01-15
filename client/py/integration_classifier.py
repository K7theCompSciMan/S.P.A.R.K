from tokenizers import Tokenizer


class IntegrationModel:
    def __init__(self, max_words=20000, max_length=50, embedding_dim=100):
        self.max_words = max_words
        self.max_length = max_length
        self.embedding_dim = embedding_dim
        self.tokenizer = Tokenizer(num_words=max_words)
        self.model = None
        self.integration_indicators = {
            'media': [],
            'management': [],
            'communication': [],
        }