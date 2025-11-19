from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging
from model_handler import ask_chatbot, load_model 

# Initialize FastAPI 
app = FastAPI(title="Nebras Chatbot API", version="1.0")

# Enable CORS (so frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL later (e.g. allow_origins=["http://localhost:8501"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schema for Request Validation
class ChatRequest(BaseModel):
    question: str

# loads model once when server starts
@app.on_event("startup")
def preload_model():
    load_model() 

# --- Startup code ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI startup: initializing model...")
    load_model()
    yield
    # --- Shutdown code  ---
    print("FastAPI shutdown: cleaning up resources...")

# Routes
@app.get("/")
def home():
    return {"message": " Nebras Medical Chatbot API is running."}

@app.post("/chat")
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please provide a valid question, Question cannot be empty.")
    try:
        response = ask_chatbot(question)
        return {"response": response}
    except Exception as e:
        logging.exception("Error processing request")

        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
