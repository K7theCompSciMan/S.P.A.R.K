import time
import uuid
import torch
import torch.nn.functional as functional
from torch.utils.data import DataLoader
from transformers import AutoTokenizer
from fastapi import FastAPI, APIRouter
import uvicorn
from LLM import LLM
from ConversationDataset import ConversationDataset
from OpenAIAPI import ChatCompletionRequest, ChatCompletionResponse 


def train_model(model, train_dataset, device, epochs=3):
    optimizer = torch.optim.AdamW(model.parameters())
    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    
    model.train()
    for epoch in range(epochs):
        for batch in train_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            
            outputs = model(input_ids)
            loss = functional.cross_entropy(
                outputs.view(-1, outputs.size(-1)),
                input_ids.view(-1),
                ignore_index=tokenizer.pad_token_id
            )
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

app = FastAPI()
router = APIRouter()

@router.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    conversation = ""
    for message in request.messages:
        role = message["role"]
        content = message["content"]
        conversation += f"{role}: {content}\n"
    
    input_ids = tokenizer.encode(
        conversation,
        return_tensors="pt",
        max_length=model.max_seq_length,
        truncation=True
    ).to(device)
    
    output_ids = model.generate(
        input_ids,
        max_length=input_ids.size(1) + request.max_tokens,
        temperature=request.temperature
    )
    
    response_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    return ChatCompletionResponse(
        id="chat-" + str(uuid.uuid4()),
        object="chat.completion",
        created=int(time.time()),
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_text
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": len(input_ids[0]),
            "completion_tokens": len(output_ids[0]) - len(input_ids[0]),
            "total_tokens": len(output_ids[0])
        }
    )

app.include_router(router)

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    model = LLM(
        vocab_size=tokenizer.vocab_size,
        embed_dim=768,
        num_layers=6,
        num_heads=12,
        ff_dim=3072,
        max_seq_length=1024
    ).to(device)
    
    conversations = [
    ]
    
    train_dataset = ConversationDataset(conversations, tokenizer, max_length=1024)
    train_model(model, train_dataset, device)
    
    torch.save(model.state_dict(), "local_llm.pt")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)