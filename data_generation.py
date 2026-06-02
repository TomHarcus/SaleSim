from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()


# want 1200 samples

PROMPT = """
You are going to generate sales data that falls into one of these six categories: HEDGING (weak, uncertain language that undermines your 
position), ANCHORING (stating your position or price first and confidently), PREMATURE DISCOUNTING (dropping price or 
conceding value before objection is fully raised), OBJECTION HANDLING (responding to prospect pushpack with evidence or reframing), 
FEATURE DUMPING (listing features without linking to prospect pain), RAPPORT BUILDING (personalising, active listening, building trust).

You are going to act as the sales person, so your task is to generate a conversation example that uses one of these categories, 
in this case ***{current_category.upper()}***. The topic of the conversation is ***{current_topic.upper()}***. Choose between responding 
confidently, nervously, angrily, or shyly. Respond naturally as in how a human would interact, not an LLM. This consists of filler 
words and incomplete sentences. Also do not make the category too obvious, real human language is ambiguous, so vary the obviousness 
of your behaviour.

For your response output in JSON format like so, current_context should be few words that describe the situation:
{
	“Context”: “current_context”,
	“Prospect turns”: {
		“Prospect_turn[1]”: prospect_turn[1],
		“Prospect_turn[2]”: prospect_turn[2]
		},
	“Response”: “response”
}
"""