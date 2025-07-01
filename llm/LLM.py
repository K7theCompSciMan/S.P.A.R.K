import re
import tiktoken
UNK = '<|unk|>'
EOT = '<|endoftext|>'

class WordTokenizer:
    def __init__(self, vocab):
        vocab.extend([EOT, UNK])
        vocabulary = {token: integer for integer, token in enumerate(vocab)}
        self.str_to_int = vocabulary
        self.int_to_str = {i:s for s, i in vocabulary.items()}
    def encode(self, text):
        preprocess = re.split(r'([,.:;?_!"()\']|--|\s)', text)
        
        preprocess = [
            item.strip() for item in preprocess if item.strip()
        ]
        preprocess = [
            item if item in self.str_to_int
            else UNK for item in preprocess
        ]
        ids = [self.str_to_int[x] for x in preprocess]
        return ids

    def decode(self, ids):
        text = " ".join([self.int_to_str[x] for x in ids])
        text = re.sub(r'\s+([,.?!"()\'])', r'\1', text)
        return text

#im not good enough to make my own BPE, so just using tiktoken wrapper
class BPE:
    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("gpt2")
    
    def encode(self, text):
        return self.tokenizer.encode(text, allowed_special={EOT})
    
    def decode(self, ids):
        return self.tokenizer.decode(ids)
