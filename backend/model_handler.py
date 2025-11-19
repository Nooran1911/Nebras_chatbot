"""
model_handler.py

Model utilities for Nebras Chatbot.
Handles model loading and response generation.
"""

import os
import torch
import logging
import warnings
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

#  Ignore Transformer Warnings
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=UserWarning)

# Check CUDA
cuda_available = torch.cuda.is_available()
device = "cuda" if cuda_available else "cpu"
print(f" Loading model on {device.upper()} ...")

#  Model Loading  (HF PUBLIC MODEL)
#MODEL_PATH = "Nooran111/Nebras_mediphi_model"
MODEL_PATH = r"C:\Users\basit\Downloads\Depi_Project1\Depi_Project\mediphi_final_model"

#  LAZY LOAD (Optimized)

tokenizer = None
model = None
chatbot = None

def load_model():
    """Loads tokenizer + model + pipeline only when needed."""
    global tokenizer, model, chatbot

    if tokenizer is not None and model is not None and chatbot is not None:
        return  # Already loaded (avoid reloading every request)

    print(" Initializing Nebras model...")

    # Load tokenizer from HF
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )

    # Load model
    if cuda_available:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
            local_files_only=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            local_files_only=True
        ).to("cpu")

    # Build pipeline AFTER model is loaded
    chatbot = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=50,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.3,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
        device=0 if cuda_available else -1
    )

    print(" Chatbot pipeline configured successfully!")


#  Helper Function: Clean Output
def clean_response(text: str) -> str:
    """Remove unwanted tokens and formatting from generated text."""
    stop_sequences = ["User:", "Question:", "\n\n", "###", "Human:", "<|end_of_document|>"]
    for stop_seq in stop_sequences:
        if stop_seq in text:
            text = text.split(stop_seq)[0]

    text = (text.replace("#HealthTipReminder", "").replace('"', "").replace("'", "").strip())

    # Normalize extra whitespace
    text = " ".join(text.split())

    # Ensure proper ending punctuation
    if text and text[-1] not in ['.', '!', '?']:
        text = text.rstrip(' ,;:-') + '.'

    return text


print(" Helper functions loaded successfully!")


# Generate Chatbot response Function
def ask_chatbot(question: str) -> str:
    """
    Generate a response from the medical chatbot.
    - Lazy loads model on first use
    - Fast for Cloud Run cold starts
    """
    load_model()   # Lazy loading here

    system_prompt = (
        "You are a medical assistant. Provide concise, professional medical advice "
        "in 1-2 sentences.\n"
        f"User: {question}\n"
        "Doctor:"
    )

    try:
        output = chatbot(system_prompt, num_return_sequences=1, return_full_text=False)
        response = output[0]["generated_text"]
        response = clean_response(response)
        return response

    except Exception as e:
        return f"Error generating response: {e}"

