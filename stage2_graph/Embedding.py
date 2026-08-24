from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained('allenai/specter2_base')
model = AutoModel.from_pretrained('allenai/specter2_base')

def embed_paper(title, abstract):
    text = title + tokenizer.sep_token + abstract
    inputs = tokenizer(text, padding=True, truncation=True, 
                        return_tensors="pt", max_length=512)
    with torch.no_grad():
        output = model(**inputs)
    # SPECTER2 uses the [CLS] token embedding
    embedding = output.last_hidden_state[:, 0, :].squeeze().numpy()
    return embedding