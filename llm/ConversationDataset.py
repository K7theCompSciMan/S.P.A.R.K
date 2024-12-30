from torch.utils.data import Dataset

class ConversationDataset(Dataset):
    def __init__(self, conversations, tokenizer, max_length):
        self.tokenizer = tokenizer
        self.conversations = conversations
        self.max_length = max_length

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conversation = self.conversations[idx]
        encoded = self.tokenizer.encode_plus(
            conversation,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoded['input_ids'].squeeze(),
            'attention_mask': encoded['attention_mask'].squeeze()
        }