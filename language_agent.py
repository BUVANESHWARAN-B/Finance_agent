from fastapi import FastAPI, HTTPException
from typing import Dict, List
import google.generativeai as genai
import os
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')


def generate_narrative(query: str, api_data: Dict, scraped_data: List[str]) -> str:
    """Generates a narrative based on the query and provided data."""

    context = f"API Data: {api_data}\nScraped Data: {scraped_data}"
    prompt = f"Given the following data, generate a concise financial narrative: {query}\nContext:{context}"
    try:
        response = model.generate_content(prompt)
        if response and response.text:  # Check if response and response.text are not None
            return {"narrative": response.text}  # Enclose the narrative in a dictionary
        else:
            return {"error": "Language model returned empty response."}
    except Exception as e:
        error_message = f"LLM generation failed: {e}"
        print(error_message)  # Log the error
        return {"error": error_message}


@app.post("/generate_narrative/")
async def generate_agent_narrative(payload: Dict):
    """API endpoint to generate a financial narrative."""

    query: str = payload.get("query")
    api_data: Dict = payload.get("api_data", {})
    scraped_data: List[str] = payload.get("scraped_data", [])

    if not query:
        raise HTTPException(status_code=400, detail="Query not provided")

    narrative_response = generate_narrative(query, api_data, scraped_data)
    return narrative_response  # Return the dictionary


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)