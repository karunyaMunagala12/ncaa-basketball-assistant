# 🏀 NCAA Basketball Assistant

An AI-powered Streamlit application to assist NCAA basketball analysts, recruiters, and coaches by offering team summaries, player similarity matching, recruiting recommendations, and a chatbot powered by Groq LLM.

---

## 📁 Project Structure


---

## 🚀 Features

- 🧠 **Chatbot Assistant**  
  Ask season-specific questions like "How did Purdue perform in 2023?" powered by Groq + Pinecone.

- 📊 **Recruit Matching**  
  Find similar recruits based on player class, position, and traits using cosine similarity.

- 🛠️ **Data Pipelines**  
  Scripts to scrape team summaries, convert to JSON, embed using Sentence-BERT, and store in Pinecone.

---

## ⚙️ Installation

```bash
# 1. Clone this repository
git clone https://github.com/karunyaMunagala12/nca-basketball-assistant.git
cd nca-basketball-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a `.env` file in the root with:
# GROQ_API_KEY=your_groq_api_key
# PINECONE_API_KEY=your_pinecone_api_key
# PINECONE_ENV=your_pinecone_env
