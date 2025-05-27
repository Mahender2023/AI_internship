# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI # Import OpenAI

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End CORS Configuration ---

# --- OpenAI Configuration ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("ERROR: OPENAI_API_KEY environment variable not found.")
    # You might want to raise an exception here or handle it gracefully
    # For now, we'll let the app start but OpenAI calls will fail.
else:
    print("OpenAI API Key loaded successfully.") # For debugging, remove in prod

client = OpenAI(api_key=openai_api_key)
# --- End OpenAI Configuration ---


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI Document Analyser Backend!"}

@app.get("/api/test")
async def test_endpoint():
    return {"data": "This is a test DATA successfully fetched from FastAPI!"}

# --- Chatbot Endpoint ---
class ChatMessage(BaseModel):
    message: str
    # Optional: You could add conversation_history here if you want to manage context
    # history: list[dict[str, str]] = [] # e.g., [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}]

@app.post("/api/chat")
async def chat_with_gpt(chat_message: ChatMessage):
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    user_message = chat_message.message
    # For a simple one-turn conversation:
    messages_for_api = [{"role": "user", "content": user_message}]

    # If you were to pass history from frontend:
    # messages_for_api = chat_message.history + [{"role": "user", "content": user_message}]

    try:
        print(f"Sending to OpenAI: {messages_for_api}") # Debugging
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Or your preferred model
            messages=messages_for_api,
            # max_tokens=150 # Optional: control response length
        )
        ai_reply = response.choices[0].message.content
        print(f"Received from OpenAI: {ai_reply}") # Debugging
        return {"reply": ai_reply.strip()}
    except Exception as e:
        print(f"OpenAI API Error: {e}") # Debugging
        raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")
@app.post("/api/chat")
async def chat_with_gpt(chat_message: ChatMessage):
    # ... (OpenAI client setup) ...
    user_prompt = chat_message.message

    if user_prompt == "User clicked SURE, proceed with questions.":
        # This is the initial interaction, AI should ask the first question
        ai_reply_content = "Great! My first question is: What is your favorite color?" # Example
    else:
        # Regular chat completion
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_prompt}],
            )
            ai_reply_content = response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")

    return {"reply": ai_reply_content.strip()}

# We'll add an endpoint for file upload later
# from fastapi import UploadFile, File
# @app.post("/api/upload")
# async def upload_document(file: UploadFile = File(...)):
#     return {"filename": file.filename, "content_type": file.content_type}