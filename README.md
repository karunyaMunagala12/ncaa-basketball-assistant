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
