from google import genai
from dotenv import load_dotenv
import random
import csv
import json
import time
import os

load_dotenv()
client = genai.Client()

CATEGORIES = {
    "WEAK_CONCESSIVE": """The salesperson loses frame control. They use epistemic uncertainty markers 
("I guess", "probably", "I think", "um", "sort of", "maybe", "I suppose") and avoid 
commitment, OR they offer a price reduction without the prospect explicitly demanding one. The rep 
is retreating — from a claim, from a price, or from their own position. The behaviour should be 
clear but not cartoonish.

POSITIVE EXAMPLES of WEAK_CONCESSIVE:
- Rep hedges a capability claim: "I mean, I think it's usually pretty reliable, I guess, though 
  I suppose nothing is ever totally guaranteed, you know?"
- Rep offers unprompted discount: "Look, if the price is the issue I can probably knock twenty 
  percent off right now just to get us moving."
- Rep combines both: "I'm fairly sure it should work fine, but honestly if the budget's the 
  problem I could maybe drop the fee a bit."

NEGATIVE EXAMPLES — do NOT generate these for WEAK_CONCESSIVE:
- A rep who acknowledges uncertainty once but then holds their position (that's OBJECTION_HANDLING)
- A rep who lists specs without committing (that's FEATURE_DUMPING)
- A rep who drops price only after the prospect explicitly names a competing price (that's a 
  concession, not premature discounting)""",

    "FEATURE_DUMPING": """The salesperson lists product specifications or capabilities without 
connecting them to the prospect's stated problem. The response would read almost identically 
regardless of what the prospect said. The prospect's actual concern is ignored in favour of a 
product monologue. Technical jargon, acronyms, and spec stacking are common signals.

POSITIVE EXAMPLES of FEATURE_DUMPING:
- Prospect worried about reliability, rep responds: "So we've got a 256-bit encrypted API with 
  quad-redundant load balancing, real-time telemetry across 40 data centres, and automated 
  failover protocols."
- Prospect asks why they should switch, rep responds: "We offer a proprietary rebalancing 
  algorithm, multi-tier asset class diversification, automated tax-loss harvesting, and a 
  dedicated mobile dashboard."

NEGATIVE EXAMPLES — do NOT generate these for FEATURE_DUMPING:
- A rep who lists one or two specs that directly answer a specific technical question 
  (that's OBJECTION_HANDLING)
- A rep who lists specs AND explicitly connects them to the prospect's stated pain 
  (that's OBJECTION_HANDLING)
- A rep who hedges while listing specs (that's WEAK_CONCESSIVE — the retreat is the 
  dominant behaviour)""",

    "OBJECTION_HANDLING": """The salesperson addresses a specific concern the prospect raised 
with a direct, structured response. The mechanism or evidence provided is clearly chosen because 
of what the prospect said — it would not make sense as a response to a different objection. 
The rep holds their position while resolving the concern. Confidence is maintained throughout.

POSITIVE EXAMPLES of OBJECTION_HANDLING:
- Prospect worried about price hikes: "Our contracts include a legally binding price-lock for 
  the full term — it's written into the SLA, not just a verbal commitment."
- Prospect worried about migration downtime: "We run a parallel environment for the first two 
  weeks so your current system stays live until the new one is fully validated."
- Prospect skeptical of reliability claims: "We publish our uptime logs directly to your portal 
  in real time — you're not taking my word for it, you can see it yourself."

NEGATIVE EXAMPLES — do NOT generate these for OBJECTION_HANDLING:
- A rep who addresses the concern but then offers a discount (that's WEAK_CONCESSIVE — the 
  retreat overrides the handling)
- A rep who lists multiple specs without tying any of them to the specific concern raised 
  (that's FEATURE_DUMPING)
- A rep who acknowledges the concern empathetically but provides no resolution 
  (that's WEAK_CONCESSIVE)""",

    "ANCHORING": """The salesperson states a specific price, number, or position confidently 
and early, framing it as the reference point for the conversation. No retreat, no qualification, 
no apology for the number. The rep owns the frame. The anchor is stated as a matter of fact, 
not a negotiating opener.

POSITIVE EXAMPLES of ANCHORING:
- "For a setup of your size, you're looking at $50,000 flat. That's the standard entry for 
  this level of integration."
- "Our enterprise tier starts at $15,000 a month. Most firms at your scale find that's where 
  the ROI actually kicks in."
- "Look, the number is $450k for the full implementation. I'm putting that on the table now 
  so we're not dancing around it later."

NEGATIVE EXAMPLES — do NOT generate these for ANCHORING:
- A rep who states a price and then immediately offers to reduce it (that's WEAK_CONCESSIVE)
- A rep who states a price in the middle of a long spec list (that's FEATURE_DUMPING)
- A rep who states a price only after the prospect explicitly asks for it without any 
  confident framing (that's just answering a question)"""
}

TOPICS = [
    "Technology/SaaS", "Healthcare software", "Investment management",
    "Corporate travel", "Manufacturing equipment", "TV and media packages",
    "Commercial real estate", "Recruitment and staffing", "Logistics and supply chain",
    "Cybersecurity", "Marketing and advertising services", "Legal services"
]

def build_prompt(category: str, topic: str) -> str:
    return f"""You are generating a single training example for a sales behaviour classifier.

CATEGORY TO GENERATE: {category}

CATEGORY DEFINITION AND EXAMPLES:
{CATEGORIES[category]}

TOPIC: {topic}

YOUR TASK:
Generate one realistic sales conversation example where a salesperson demonstrates {category} behaviour.

STRICT REQUIREMENTS:
1. The salesperson response must unambiguously demonstrate {category} and no other category
2. The context turns must create a situation where {category} is the natural response — not just 
   possible, but the behaviour the context is specifically setting up
3. The response must be 2-3 sentences. No longer.
4. Write like a real human on a sales call — use contractions, occasional filler words, 
   incomplete thoughts. Not formal. Not an LLM.
5. Do NOT make the category name or its markers explicit in the response
6. The prospect messages should be direct and skeptical — not polite or verbose
7. Use vocabulary natural to the {topic} industry

OUTPUT FORMAT — return only valid JSON, no markdown, no preamble:
{{
    "context_turns": ["prospect message 1", "prospect message 2"],
    "response": "salesperson response"
}}

You may use 1 or 2 context turns, whichever creates a more natural setup. If 1 is sufficient, 
use 1. Do not pad with an unnecessary second turn."""

SAMPLES_PER_CATEGORY = 600
OUTPUT_FILE = "sales_convo_data.csv"

# create random category order with 600 of each category
jobs = []
for category in CATEGORIES:
    for _ in range(SAMPLES_PER_CATEGORY):
        jobs.append((category, random.choice(TOPICS)))

random.shuffle(jobs)

# check if file exists
start_index = 0
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r") as f:
        start_index = sum(1 for _ in f) - 1
    print(f"Resuming from index {start_index}")

with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as data_file:
    fieldnames = ["context_turns", "response"]
    writer = csv.DictWriter(data_file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

    if start_index == 0:
        writer.writeheader()

    # fill in the current category and topic into the prompt
    for i, (category, topic) in enumerate(jobs[start_index:], start=start_index):
        prompt = build_prompt(category, topic)

        # pass to the LLM
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt,
            )

            output = response.text.replace("```json", "").replace("```", "").strip()
            parsed_output = json.loads(output)

            writer.writerow({
                "context_turns": json.dumps(parsed_output["context_turns"]),
                "response": parsed_output["response"]
            })
            data_file.flush()

            print(f"Completed sample {i}/{len(jobs)}")
            time.sleep(4)

        except json.JSONDecodeError:
            print(f"JSON error on sample {i}, skipping")
            time.sleep(4)

        except Exception as e:
            print(f"Error at sample {i}: {e}")
            time.sleep(10)
    