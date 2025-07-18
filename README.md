# 🏀 NCAA Basketball Assistant

An AI-powered Streamlit app for NCAA basketball analysts, recruiters, and coaches — combining Q&A, scouting insights, and recruit matching in a seamless interface powered by **Groq LLaMA + Pinecone + Sentence-BERT**.

---

## 📌 What this app does

- 🤖 **AI Chatbot on Team Scouting Reports**  
  Ask natural questions like _“How did Purdue perform in 2023?”_ — and get intelligent, season-specific summaries.

- 🔍 **Recruit Similarity Matching**  
  Find look-alike players based on position, class, and traits using cosine similarity.

- 🧠 **Context-Aware Recommendations**  
  Combines embedded scouting data with generative responses for deeper insights.

- 🛠️ **Multi-Tab Streamlit UI**  
  Organized into tabs: **Chatbot**, **Recruit Matcher**, and (upcoming) **Team Scouting & Growth Tracking**.

- 💾 **Semantic Search Engine**  
  Uses `Sentence-BERT` to embed JSON summaries and stores them in `Pinecone` for fast retrieval.

- 🚀 **Groq-hosted LLaMA Backend**  
  Lightning-fast, cost-efficient inference with Groq’s API, delivering smart responses in seconds.

---

🧩 This is not just a chatbot — it's a **modular basketball analytics assistant** built for performance, recruiting, and decision-making.



## Features

- Chatbot assistant that answers team-level questions using embedded scouting summaries  
- Real-time responses powered by Groq-hosted LLaMA model  
- Pinecone-powered retrieval for fast, accurate scouting context  
- Sentence-BERT used to embed and search JSON-formatted team data  
- Supports year-specific queries like “How did Illinois perform in 2022?”  
- Modular backend design to allow future extension to player growth and scouting trends  
- Streamlit-based UI with a clean, tabbed layout for ease of use


## Project Structure

This repository is organized into modular components:

### `app/` – Core application logic
- `chatbot.py` – Streamlit chatbot app for team-level Q&A
- `recruiting_similarity_app.py` – Recommender tool for similar recruits based on traits
- `embed_team_scouting.py` – Embedding script for team scouting JSON files
- `scraper.py` – Player data scraper for seasons from 2008 to 2025

### `data/` – Raw and processed data
- `raw/` – Scraped JSON and CSV files
- `cleaned/` – Cleaned datasets ready for use
- `json/` – Final JSONs used in embedding + chatbot

### `scripts/` – Utility helpers
- `convert_team_scouting_to_json.py` – Converts scouting data into structured JSON

### Root files
- `requirements.txt` – All Python dependencies
- `README.md` – Project documentation and instructions



## Installation

Follow these steps to set up the project locally:

### 1️⃣ Clone the repository  
Download the project files from GitHub to your local machine.
```bash
git clone https://github.com/karunyaMunagala12/nca-basketball-assistant.git
cd nca-basketball-assistant


---

### 📦 2. Install Required Dependencies  
Install all the Python packages listed in `requirements.txt`.
pip install -r requirements.txt

---

### 🛡️ 3. Create a `.env` File  
Add your API credentials to a `.env` file at the project root.
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=your_pinecone_env


> 💡 *Make sure your `.env` file is listed in `.gitignore` to prevent accidental pushes.*

---

### 🚀 4. Run the Chatbot App Locally  
Start the Streamlit application on your browser.
streamlit run app/chatbot.py
