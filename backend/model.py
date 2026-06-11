from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model = AutoModelForSequenceClassification.from_pretrained("ml/checkpoints")
tokenizer = AutoTokenizer.from_pretrained("ml/checkpoints")

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model.to(device)

model.eval()

# tokenize context+message
def tokenize(context, message):
    return tokenizer(context, message, truncation=True, return_tensors="pt")


def classify(tokens):
    # input to model
    tokens = {k: v.to(device) for k, v in tokens.items()}
    with torch.no_grad():
        outputs = model(**tokens)
    
    # get prediction
    logit = outputs.logits
    prediction = torch.argmax(logit, dim=-1)

    # map to correct label
    label_map = {0: "WC", 1: "OH", 2: "FD", 3: "AN"}
    return label_map[prediction.item()]
