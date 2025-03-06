from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

API_KEYS_CREDIT = {os.getenv("API_KEY"): 2}

app = FastAPI()


def verify_api_key(x_key: str = Header(None)): 
    credit = API_KEYS_CREDIT.get(x_key, 0)
    if credit <= 0:
        raise HTTPException(status_code=401, detail="Invalid API key, or no more credits left")
    return x_key


# Define the request body model
# class Prompt(BaseModel):
#     prompt: str

@app.post("/generate")


# def generate(request: Prompt):
#     response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": request.prompt}])
#     return {"response": response["message"]["content"]}

def generate(prompt: str, x_key: str = Depends(verify_api_key)):
    API_KEYS_CREDIT[x_key] -= 1
    response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": prompt}])
    return {"response": response["message"]["content"]}

