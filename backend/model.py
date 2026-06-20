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
    predictions = torch.softmax(logit, dim=-1)


    # convert to list of probabilities that sum to 1
    output_values = predictions[0].tolist()


    return {"WC": output_values[0], "OH": output_values[1], "FD": output_values[2], "AN": output_values[3]}
