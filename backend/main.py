from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from session import Session, Customer_Type
import secrets
from gemini import get_response
from model import classify, tokenize
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# all active sessions
sessions_dict = {}

# schema for a session
class UserSession(BaseModel):
    description : str
    personality : str
    customer_type : Customer_Type
    interest_level : int

# schema for a message
class Message(BaseModel):
    session_id : str
    content : str

# schema for session id
class SessionID(BaseModel):
    session_id : str

# initialise session endpoint
@app.post("/start")
async def start_session(user_session: UserSession):
    # generate unique session id
    user_session_id = secrets.token_hex(16)

    user_session = Session(user_session.description, user_session.personality, user_session.customer_type, user_session.interest_level)

    # connect session id to user session class
    sessions_dict[user_session_id] = user_session
    return user_session_id

# message endpoint
@app.post("/message")
async def get_message(user_message: Message):
    # check if session exists
    if user_message.session_id in sessions_dict:
        user_session = sessions_dict[user_message.session_id]
    else:
        raise HTTPException(status_code=404, detail="Session not found")
    

    distribution = None
    classification = ("N/A", 0)
    if user_session.get_counter() > 0:
        model_input = tokenize(user_session.get_previous_message(), user_message.content)
        distribution = classify(model_input)

        for i in distribution:
            distribution[i] = round(distribution[i], 2)

        list_distribution = distribution.items()

        classification = max(list_distribution, key=lambda x: x[1])


    response = get_response(user_session, user_message)

    user_session.update_counter()
    user_session.update_interest_level(response["interest_level"])
    user_session.update_history("user", user_message.content)
    content = response["content"]
    user_session.update_history("model", content)


    return {"content": content, "distribution": distribution, "classification": classification[0], "interest_level": user_session.interest_level}


@app.post("/end")
async def end_session(user_session_id : SessionID):
    # remove users session from dictionary
    try:
        del sessions_dict[user_session_id.session_id]
        return "Session ended"
    
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    
    
