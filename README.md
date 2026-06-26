# 🍔 GSB Food AI Assistant
**AI-Food-React-Agent-Rag** is an intelligent culinary intelligence platform specifically designed to preserve and analyze **Gowd Saraswat Brahmin (GSB) cuisine**. Traditional GSB dishes often rely on highly localized ingredients, and precise fermentation techniques (such as Surnali, Sanna, or Pathrode) that standard food apps fail to parse. This application allows users to query traditional GSB recipes, automatically extracting authentic ingredient lists and calculating complete, deterministic caloric and macronutrient profiles.Built on a Python **LangGraph** orchestration loop, the application uses a ReAct (Reasoning and Action) agent workflow to dynamically clean and translate regional culinary terms. It integrates directly with the **USDA FoodData Central API** to fetch certified nutritional foundations per ingredient. To drive context-aware recipe parsing, the system implements an advanced Retrieval-Augmented Generation (RAG) architecture backed by a **local Chroma DB vector store stored directly on the hard drive** for persistent, zero-cloud cookbook indexing. Finally, the system leverages **Streamlit caching mechanisms** to memory-map heavy vector lookups and redundant API queries, ensuring an efficient, near-instantaneous user experience.

Powered by **Streamlit**, **LangChain**, **LangGraph** and **Google Gemini 2.5**.

### 🤖 System Architecture

![LangGraph Agent Workflow](architecture.png)


Open your terminal and type
python3 -m venv <your-environment-name>
source <your-environment-name>/bin/activate

We are using Google Gemni Model LLM(gemini-2.5-flash) here.

Paste the api keys in the .env folder created at the root level of your project
1. Go to Google AI Studio and get the api key https://aistudio.google.com/api-keys
GOOGLE_API_KEY="<YOUR_API_KEY>"

2. Go to https://smith.langchain.com/ and get the API KEY
LANGCHAIN_API_KEY="<YOUR_API_KEY>"

3. Go to https://fdc.nal.usda.gov/api-key-signup and get your usda api key.
USDA API KEY="<YOUR_API_KEY>

How to run Streamlit applications ?.
Open terminal and type:
```
streamlit run "<project-name>"
```