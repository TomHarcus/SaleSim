import pandas as pd
from transformers import pipeline

DATA_FILE = "ml/data/sales_convo_labelled.csv"

def get_counts(data):
    df = pd.read_csv(data)

    column_counts = df["label"].value_counts()

    return column_counts

classifier = pipeline(
    task="text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0
)

result = classifier("I dont have an opinion for hugging face transformers")
print(result)