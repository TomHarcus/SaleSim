from enum import Enum
from google.genai import types

# customer difficulty levels
class Customer_Type(Enum):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


class Session:
    def __init__(self, description, personality, customer_type, interest_level):
        self.counter = 0
        self.history = []
        self.description = description
        self.personality = personality
        self.customer_type = customer_type
        self.objections = []
        self.interest_level = interest_level

    def update_counter(self):
        self.counter += 1

    def get_counter(self):
        return self.counter

    def update_interest_level(self, new_value):
        if new_value >= 1 and new_value <= 5:
            self.interest_level = new_value
    
    def update_history(self, role, parts):
        turn = types.Content(role=role, parts=[types.Part(text=parts)])
       
        self.history.append(turn)

    def get_previous_message(self):
        return self.history[-1].parts[0].text
    
    def update_objections(self, objection):
        self.objections.append(objection)


        

    