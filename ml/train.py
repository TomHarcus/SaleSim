from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, get_scheduler
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from datasets import load_dataset, DatasetDict
from sklearn import metrics
import numpy as np
from tqdm.auto import tqdm

model_name = "distilbert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=4)
dataset = load_dataset("TomHarcus/sales-behaviour-classifier-dataset", split="train")

shuffled_dataset = dataset.shuffle(seed=42)

# split dataset into train/test/val
train_test = shuffled_dataset.train_test_split(test_size=0.3)

train_test_valid = train_test["test"].train_test_split(test_size=0.5)

datasets = DatasetDict({
    "train": train_test["train"],
    "test": train_test_valid["test"],
    "valid": train_test_valid["train"]
})

# create the default tokenizer in case model needs changed
tokenizer = AutoTokenizer.from_pretrained(model_name)

# helper functions: 1. tokenize each sample 2. convert string label to integer
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

# create tokenized dataset via helper functions
tokenized_dataset = datasets.map(tokenize, batched=True).map(label_to_int)

tokenized_dataset = tokenized_dataset.remove_columns(["label", "context_turns", "response"])

tokenized_dataset.set_format("torch")

# provide paddings
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# create both dataloaders
train_dataloader = DataLoader(
    tokenized_dataset["train"], shuffle=True, batch_size=8, collate_fn=data_collator
)

eval_dataloader = DataLoader(
    tokenized_dataset["valid"], batch_size=8, collate_fn=data_collator
)

# training parameters set

optimizer = AdamW(model.parameters(), lr=5e-5)

num_epochs = 3
num_training_steps = num_epochs * len(train_dataloader)
lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps
)

# check for gpu
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model.to(device)

progress_bar = tqdm(range(num_training_steps))

# main loop

model.train()
for epoch in range(num_epochs):
    for batch in train_dataloader:
        # go through each sample, make prediction, adjust weights
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()

        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)
    
    # evaluate model on eval set
    model.eval()
    labels = []
    predictions = []
    for batch in eval_dataloader:
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
    print(f"Epoch {epoch} F1: {score}")

    model.train()

model.save_pretrained("ml/checkpoints")
tokenizer.save_pretrained("ml/checkpoints")
print(metrics.classification_report(all_labels, all_predictions, target_names=["WC", "OH", "FD", "AN"]))


