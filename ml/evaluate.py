from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification
import torch
from torch.utils.data import DataLoader
from datasets import load_dataset, DatasetDict
from sklearn import metrics
import numpy as np

# same setup as training
model = AutoModelForSequenceClassification.from_pretrained("ml/checkpoints")
tokenizer = AutoTokenizer.from_pretrained("ml/checkpoints")
dataset = load_dataset("TomHarcus/sales-behaviour-classifier-dataset", split="train")

shuffled_dataset = dataset.shuffle(seed=42)

train_test = shuffled_dataset.train_test_split(test_size=0.3)

train_test_valid = train_test["test"].train_test_split(test_size=0.5)

datasets = DatasetDict({
    "train": train_test["train"],
    "test": train_test_valid["test"],
    "valid": train_test_valid["train"]
})


def tokenize(sample):
    return tokenizer(sample["context_turns"], sample["response"], truncation=True)


def label_to_int(sample):
    label_map = {
    "WC": 0,
    "OH": 1,
    "FD": 2,
    "AN": 3
    }

    return {"labels": label_map[sample["label"]]} 

tokenized_dataset = datasets.map(tokenize, batched=True).map(label_to_int)

tokenized_dataset = tokenized_dataset.remove_columns(["label", "context_turns", "response"])

tokenized_dataset.set_format("torch")

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# test sample data loader this time
test_dataloader = DataLoader(
    tokenized_dataset["test"], batch_size=8, collate_fn=data_collator
)

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model.to(device)

# run model for evaluation and calculate scores
model.eval()

labels = []
predictions = []

for batch in test_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        with torch.no_grad():
            outputs = model(**batch)

        logit = outputs.logits
        prediction = torch.argmax(logit, dim=-1)

        labels.append(batch["labels"].cpu().numpy())
        predictions.append(prediction.cpu().numpy())
    
all_labels = np.concatenate(labels)
all_predictions = np.concatenate(predictions)
score = metrics.f1_score(all_labels, all_predictions, average="macro")
print(f"F1: {score}")
print(metrics.classification_report(all_labels, all_predictions, target_names=["WC", "OH", "FD", "AN"]))