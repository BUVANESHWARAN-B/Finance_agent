import streamlit as st
import requests
import json

# URL of your orchestrator's FastAPI endpoint
ORCHESTRATOR_URL = "http://localhost:8000/run/"  # Adjust if your orchestrator runs on a different host/port

def get_response_from_orchestrator(query: str):
    try:
        response = requests.post(ORCHESTRATOR_URL, json={"query": query})
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["narrative"]
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to orchestrator. {e}"
    except KeyError as e:
        return f"Error: Unexpected response format from orchestrator. {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def main():
    st.title("Finance Assistant")

    query = st.text_input("Enter your financial query:")

    if query:
        st.spinner("Processing your query...")
        response = get_response_from_orchestrator(query)
        st.subheader("Response:")
        st.write(response)

if __name__ == "__main__":
    main()