from fastapi import FastAPI, HTTPException
import httpx
from typing import Dict, Any, Optional, Union
import json

app = FastAPI()

API_AGENT_URL = "http://localhost:8001/get_data/"
SCRAPING_AGENT_URL = "http://localhost:8002/retrieve_relevant_content/"
LANGUAGE_AGENT_URL = "http://localhost:8003/generate_narrative/"


async def fetch_agent_response(url: str, payload: Dict) -> Dict[str, Any]:
    """
    Asynchronously fetches a response from a given agent.

    Args:
        url (str): The URL of the agent's endpoint.
        payload (Dict): The payload to send to the agent.

    Returns:
        Dict[str, Any]: The JSON response from the agent, or an error dictionary if an error occurs.

    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()  # Raise HTTPStatusError for bad responses
            try:
                return response.json()
            except json.JSONDecodeError:
                error_message = f"Agent {url} returned invalid JSON: {response.text}"
                print(error_message)
                return {"error": error_message}
        except httpx.HTTPStatusError as e:
            error_message = f"Agent {url} error: {e}"
            print(error_message)
            return {"error": error_message}
        except httpx.RequestError as e:
            error_message = f"Error connecting to agent {url}: {e}"
            print(error_message)
            return {"error": error_message}
        except Exception as e:
            error_message = f"Unexpected error fetching from {url}: {e}"
            print(error_message)
            return {"error": error_message}


@app.post("/run/")
async def orchestrate_agents(payload: Dict) -> Dict[str, Any]:
    """
    Orchestrates the API, Scraping, and Language Agents to generate a narrative.

    Args:
        payload (Dict): The incoming request payload containing the user query.

    Returns:
        Dict[str, Any]: A dictionary containing the generated narrative and potentially error messages.

    Raises:
        HTTPException: If the query is not provided.
    """

    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query not provided")

    api_data = await fetch_agent_response(API_AGENT_URL, {"query": query})
    scraped_data = await fetch_agent_response(SCRAPING_AGENT_URL, {"query": query})
    narrative: Union[str, None] = "Error: Could not retrieve narrative."  # Default error message (explicitly typed)

    if "error" not in api_data and "error" not in scraped_data:
        language_agent_payload = {"query": query, "api_data": api_data, "scraped_data": scraped_data}
        narrative_response = await fetch_agent_response(LANGUAGE_AGENT_URL, language_agent_payload)

        # Super-defensive check: Ensure narrative_response is a dict
        if isinstance(narrative_response, dict):
            if "error" not in narrative_response:
                narrative = narrative_response.get("narrative", "No narrative generated.")
            else:
                narrative = narrative_response.get("error", "Error: Language Agent failed.")
        else:
            narrative = f"Error: Language Agent returned unexpected data type: {type(narrative_response)}"
            print(narrative)  # Log this unexpected type
    else:
        if "error" in api_data:
            narrative = api_data["error"]
        elif "error" in scraped_data:
            narrative = scraped_data["error"]

    return {"narrative": narrative}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)