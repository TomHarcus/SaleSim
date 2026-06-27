# SaleSim

## Project Overview

## Live Demo

[salesim.app](https://salesim.app)

## Architecture

In this project there are two AI agents.

Agent A: an external LLM (Gemini) that acts as the customer and responds to the practicing salesperson, the user.
Agent B: a finetuned DistilBERT model that takes in each conversation pair and classifies the sample from four categories: OH, WC, FD, or AN.

Agent B takes the conversation pair (customer message + salesperson response) as input, instead of just the 'salesperson's message alone. This is because the salesperson's
behaviour only makes sense in the context of what they were responding to, giving a more useful classification. Classifying the salesperson's message alone would lose that context.

The vanilla Javascript frontend communicates to a FastAPI backend via REST API calls.

When a new user starts a session, their session ID is stored server side, allowing different users to all use the project at the same time.

Agent B runs locally on the server to avoid a startup latency per-request. Agent A makes an external API call to gemini-3.1-flash-lite.

## ML Pipeline

### Schema Design

Initially I came up with six different classes, the last two were Hedging and Premature Discounting. After reviewing initial samples, there was too much ambiguity and overlap for manual labelling by a human so I reduced the number to four.

The final four classes are as follows:

Objection Handling (OH) - The salesperson addresses a specific concern the prospect raised with a direct, structured response.

Weak Concession (WC) - The salesperson loses control, avoids commitment, or reduces price too quickly.

Feature Dumping (FD) - The salesperson lists off features or specs that had no connection with the customers question or concern.

Anchoring (AN) - The salesperson sets a price for the service/product early in the conversation with confidence.


### Data Generation

Google Gemini created 2400 synthetic samples of conversation pairs with each sample given one classification type making sure that the four classes were balanced in the final dataset. The labels were deliberately left out of the output.

### Circularity Problem 

Gemini controlled both sides of the sample, meaning it could generate trivially classifiable samples that were not grounded in real sales behaviour. This would have meant during training, Agent B would learn pairs that matched the class exactly, rather than universal actual sales behaviour and conversation dialogue.

To fix this Gemini was given explicit positive and negative examples for each category's definition. This allowed Gemini to generate responses grounded in human defined criteria and also exhibiting the target behaviour as defined by the examples.

### Manual Labelling Decision

Gemini generated all 2400 conversation pairs but deliberately left out classification labels so that I could manually label all of them.

This was done as relying on Gemini to label its own samples would re-introduce the circularity problem. Its label would reflect its own generation intent instead of a consistent human-defined standard.


### Training and Evaluation

### OOD Detection Mechanism and Threshold Calibration


## Tech Stack

Python, JavaScript, HTML, and CSS

## Running Locally