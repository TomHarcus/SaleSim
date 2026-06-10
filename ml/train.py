from transformers import AutoTokenizer, DataCollatorWithPadding, TrainingArguments, Trainer
from datasets import load_dataset, DatasetDict

model = "distilbert-base-uncased"
dataset = load_dataset("TomHarcus/sales-behaviour-classifier-dataset", split="train")

shuffled_dataset = dataset.shuffle()

# split dataset into train/test/val
train_test = shuffled_dataset.train_test_split(test_size=0.3)

train_test_valid = train_test["test"].train_test_split(test_size=0.5)

datasets = DatasetDict({
    "train": train_test["train"],
    "test": train_test_valid["test"],
    "valid": train_test_valid["train"]
})

# create the default tokenizer in case model needs changed
tokenizer = AutoTokenizer.from_pretrained(model)

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

# provide paddings
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

training_args = TrainingArguments("checkpoints/", push_to_hub=True)

trainer = Trainer(
    model,
    training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["valid"],
    data_collator=data_collator,
    processing_class=tokenizer
)

trainer.train()
