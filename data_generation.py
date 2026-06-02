from google import genai
from dotenv import load_dotenv
import random
import csv
import json
import time

load_dotenv()
client = genai.Client()

# list of sales categories and topics
categories = ["HEDGING", "ANCHORING", "PREMATURE DISCOUNTING", "OBJECTION HANDLING", "FEATURE DUMPING", "RAPPORT BUILDING"]
topics = ["TECHNOLOGY", "HEALTHCARE", "INVESTMENTS", "TRAVEL", "MANUFACTURING", "TV/MEDIA"]

# open csv file
with open("sales_convo_data.csv", "w", newline="") as data_file:
    fieldnames = ["label", "context_turns", "response"]
    writer = csv.DictWriter(data_file, fieldnames=fieldnames)
    writer.writeheader()

    # generate 1200 samples with varying categories and topcis
    for i in range(1200):
        prompt = f"""
            You are going to generate sales data that falls into 1 of these 6 categories: HEDGING (weak, uncertain language that undermines your 
            position), ANCHORING (stating your position or price first and confidently), PREMATURE DISCOUNTING (dropping price or 
            conceding value before objection is fully raised), OBJECTION HANDLING (responding to prospect pushpack with evidence or reframing), 
            FEATURE DUMPING (listing features without linking to prospect pain), RAPPORT BUILDING (personalising, active listening, building trust).

            You are going to act as the sales person, so your task is to generate a conversation example that uses one of these categories, 
            in this case ***{categories[i%6]}***. The topic of the conversation is ***{random.choice(topics)}***. Choose between responding 
            confidently, nervously, angrily, or shyly. Respond naturally as in how a human would interact, not an LLM. This consists of filler 
            words and incomplete sentences. Also do not make the category too obvious, real human language is ambiguous, so vary the obviousness 
            of your behaviour. Don't use unconventional words that are rarely used during natural conversation, keep it as human like as possible.

            Add a field to your JSON output called ***Context turns***: a list of 1-2 short prospect messages that naturally lead into the 
            salesperson's (your) response. The context turns should create a realistic setup that makes the category behaviour make sense in 
            context.

            For your response output in JSON format like so:
            {{
                "Context turns”: ["Thanks for reaching out, but I'm currently satisfied with my existing provider. I've been burned before by good deals that end up having hidden fees or unstable service after the introductory period, so I'm quite hesitant to switch unless there's a very compelling reason to move. What exactly makes your service different, and how do I know the pricing won't just hike up in six months?", "I appreciate the assurance, but 'best value' is a bit subjective, isn't it? Every provider says that, and then the fine print reveals a different story. If I'm going to consider making a change—which is always a bit of a headache—I need to see something concrete. Can you walk me through your actual pricing structure for a long-term plan, and more importantly, how you handle reliability compared to the major players? I'm not looking for a sales pitch, just the technical and contractual reality."],
                “Response”: “response”
            }}
        """
        # avoid errors
        try:
            response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            )

            output = response.text.replace("```json", "").replace("```", "").strip()

            parsed_output = json.loads(output)
            writer.writerow({
                "label": "",
                "context_turns": parsed_output["Context turns"],
                "response": parsed_output["Response"]
            })
            data_file.flush()
            
            print(f"completed sample {i}")
            time.sleep(4)

        except json.JSONDecodeError:
            print(f"json error on sample {i}")
        except Exception as e:
            print(f"{e} error at sample {i}")

    