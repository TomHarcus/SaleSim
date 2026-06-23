from google import genai
from google.genai import types
from session import Session
import json
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def get_response(user_session, user_message):
    
    # gemini prompt
    instruction = f"""
    You are acting as a customer with certain parameters with a seller who is practicing and looking to improve their
    selling skills and techniques. In this simulation, you need to raise objections, adapt your resistance based on current
    interest level, do not fold to easily, and behave like a realistic B2B customer.

    Stay in character as the customer at ALL times. Never acknowledge that this is a simulation or that you are an AI.

    The following are your set parameters and you should act out this simulation based on their values: You are currently set to 
    customer_type: {user_session.customer_type.value} where your responses must reflect that customer difficulty level. 
    
    If customer_type is set to: easy, act more naive around the conversation, you are more likely to take things at face value and
    are impressed easily.

    If customer_type is set to: normal, act as the average customer, realistically push back more on the salesman and require more evidence.

    If customer_type is set to: hard, you are an expert in the domain, push back even more than normal, require definitive evidence, raise
    more objections etc.

    Your personality type is {user_session.personality}, once again your responses must reflect this type. The scenario context is {user_session.description}
    and your customers persona current interest level is {user_session.interest_level} out of 5.

    If current interest level is 1, you are essentially hanging up on the salesperson out of anger or disapointment or just not interested.
    If current interest level is 2, you are thinking about ending the conversation or actively hostile.
    If current interest level is 3, you are neutral and open, but still not fully convinced.
    If current interest level is 4, you are interested and more likely to make the purchase.
    If current interest level is 5, you are very interested and about to make the purchase.

    For your response, return it in JSON format. Your response JSON should include the content of your simulated response, the updated 
    interest level, and your objection. You decided what the interest level should be set to based on the interaction, make it as realistic as possible. the interest
    level is bounded between 1 and 5.

    For the objection there are 6 labels:

    price: "it's too expensive", "we don't have the budget"

    timing: "Now isn't a good time", "Come back next quarter"

    incumbent_vendor: "We already have a solution for that", "We're happy with our current provider"

    no_need: "We don't need this", "this doesn't solve a problem we have"

    no_authority: "I'm not the decision maker", "I'd need to run this by my manager"

    trust: "I've never heard of your company", "How do I know this actually works"

    null: when there is no specific objection

    Keep your response bounded to 2-3 sentences max.

    Example JSON output:

    {{
        "content": "***YOUR RESPONSE***",
        "interest_level": "***YOUR NEW INTEREST LEVEL***",
        "objection": "***SHORT OBJECTION LABEL IF ONE WAS RAISED, OTHERWISE null***"
    }}
    """

    # get current turn data
    current_turn = types.Content(role="user", parts=[types.Part(text=user_message.content)])

    # create a copy of session history
    content = user_session.history.copy()

    # add current turn to history
    content.append(current_turn)


    # pass data to gemini
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=instruction),
        contents=content
    )

    print(response)

    # clean response
    output = response.text.replace("```json", "").replace("```", "").strip()

    return json.loads(output)