# 🏀 NCAA Basketball Assistant

An AI-powered Streamlit application designed to assist NCAA basketball analysts, recruiters, and coaches. It provides team summaries, player similarity search, recruiting recommendations, and a smart chatbot powered by Groq LLM + Pinecone.

---

## 🚀 Features

- 🧠 **Chatbot Assistant**  
  Ask questions like *“How did Purdue perform in 2023?”* — powered by Groq + Pinecone.

- 📊 **Recruit Matching**  
  Find similar recruits using cosine similarity based on traits, class, and position.

- 🔁 **Data Pipelines**  
  Scripts to scrape, clean, convert to JSON, embed using Sentence-BERT, and store in Pinecone.

---

## 📁 Project Structure
nca-basketball-assistant/
│
├── app/                       # Core application scripts
│   ├── chatbot.py             # Streamlit chatbot assistant (Groq/GPT + Pinecone)
│   ├── recruiting_similarity_app.py  # Cosine similarity for recruiting matches
│   ├── embed_team_scouting.py # Embedding logic for team JSON data
│   └── scraper.py             # Player data scraper (2008–2025)
│
├── data/
│   ├── cleaned/               # Cleaned CSVs
│   ├── json/                  # JSON data for chatbot
│   └── raw/                   # Raw scraped CSVs and JSONs
│
│
├── scripts/                  # Utility scripts
│   └── convert_team_scouting_to_json.py
│
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation


---

## ⚙️ Installation

Make sure you have Python ≥ 3.9.

```bash
# 1. Clone the repository
git clone https://github.com/karunyaMunagala12/nca-basketball-assistant.git
cd nca-basketball-assistant

# 2. Install dependencies
pip install -r requirements.txt

#▶️ Run the App
Launch the chatbot Streamlit app locally:

streamlit run app/chatbot.py


