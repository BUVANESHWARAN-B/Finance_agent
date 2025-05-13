# Finance Assistant

This project is a personal finance assistant powered by language models and various APIs. It allows users to ask natural language questions about stock prices, company information, and potentially other financial data.

## Overview

The Finance Assistant is built using a modular architecture, comprising several key components:

* **API Agent (`api_agent.py`):** An API endpoint that interacts with financial data APIs (currently Alpha Vantage) to retrieve information like stock prices and company overviews based on user queries.
* **Scraping Agent (`scraping_agent.py`):** (Potentially in development or future feature) An agent designed to scrape financial information from websites.
* **Language Agent (`language_agent.py`):** (Potentially in development or future feature) An agent that uses a Language Model (LLM) to understand user queries and orchestrate the other agents.
* **Orchestrator (`orchestrator.py`):** (Potentially in development or future feature) A central component that manages the flow of information between the user, the Language Agent, and the specialized agents.
* **Streamlit App (`streamlit_app.py`):** A user interface built with Streamlit for interacting with the Finance Assistant.

## Setup and Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone 
    cd Finance_agent
    ```
    (Replace `<repository_url>` with the URL of your GitHub repository and `<repository_name>` with the name of your repository.)

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure you have a `requirements.txt` file in your project root. If not, create one with the necessary libraries like `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `langchain`, `sentence-transformers`, `faiss-cpu`, `streamlit`, `httpx`.)

3.  **Set up environment variables:**
    * Create a `.env` file in the root of your project.
    * Add your API keys to the `.env` file:
        ```dotenv
        ALPHAVANTAGE_API_KEY=YOUR_ALPHAVANTAGE_API_KEY
        # Add other API keys here if needed (e.g., for web scraping, LLM)
        ```
        Replace `YOUR_ALPHAVANTAGE_API_KEY` with your actual Alpha Vantage API key. You can obtain one for free from the [Alpha Vantage website](https://www.alphavantage.co/).

## Running the Application

1.  **Run the API Agent (on port 8001):**
    ```bash
    python api_agent.py
    ```
    You should see Uvicorn start the FastAPI application.

2.  **Run the Streamlit User Interface (on port 8501):**
    ```bash
    streamlit run streamlit_app.py
    ```
    This will open the Finance Assistant web interface in your default browser.

3.  **(Optional) Run other agents (if implemented):**
    * You might have separate scripts for the `orchestrator.py`, `scraping_agent.py`, and `language_agent.py`. Run them in separate terminal windows if they are designed to run independently.

## Usage

1.  Open the Streamlit web interface in your browser (usually at `http://localhost:8501`).
2.  Enter your financial query in the input field (e.g., "What is the stock price of AAPL?", "Tell me about Microsoft company overview").
3.  The application will send your query to the backend (likely involving the Orchestrator and the API Agent) and display the response.
