import pandas as pd
import streamlit as st
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import re

# --- Helpers ---
def convert_height(h):
    """Convert height from '6-4' format to inches."""
    try:
        if isinstance(h, str) and '-' in h:
            ft, inch = h.split('-')
            return int(ft) * 12 + int(inch)
        elif isinstance(h, (int, float)):
            return h
    except:
        return None

def extract_stat(summary, stat):
    """Extract stat value (Pts, Reb, Ast) from summary text."""
    match = re.search(rf"([\d\.]+)\s*{stat}", str(summary))
    return float(match.group(1)) if match else 0.0

@st.cache_data
def load_and_process():
    """Load, clean, and encode player data. Return DataFrame + similarity matrix."""
    df = pd.read_csv("data/player_stats_merged.csv").rename(columns={
        "height_x": "height",
        "weight_x": "weight",
        "pos_x": "pos",
        "class_x": "class"
    })

    # Filter and clean height/weight
    df = df.dropna(subset=["height", "weight"])
    df["height"] = df["height"].apply(convert_height)
    df = df[df["height"].notnull() & (df["height"] > 40)]
    df = df[df["weight"].apply(lambda w: isinstance(w, (int, float)) and w > 100)]

    # Clean categorical values
    df["pos"] = df["pos"].astype(str).str.upper().str.strip()
    df["class"] = df["class"].astype(str).str.upper().str.strip()

    # Extract performance stats
    df["pts"] = df["summary"].apply(lambda x: extract_stat(x, "Pts"))
    df["reb"] = df["summary"].apply(lambda x: extract_stat(x, "Reb"))
    df["ast"] = df["summary"].apply(lambda x: extract_stat(x, "Ast"))

    # Encode categorical vars + normalize features
    df_encoded = pd.get_dummies(df[["pos", "class"]], drop_first=True)
    features_df = pd.concat([df[["height", "weight", "pts", "reb", "ast"]], df_encoded], axis=1)

    scaler = StandardScaler()
    X = scaler.fit_transform(features_df)
    similarity_matrix = cosine_similarity(X)

    df["label"] = df["summary"] + " | " + df["school"] + " (" + df["year"].astype(str) + ")"
    return df.reset_index(drop=True), similarity_matrix

# --- UI Setup ---
st.set_page_config(page_title="Recruiting Similarity Tool", layout="centered")
st.title("🏀 Recruiting Similarity Tool")
st.markdown("Find similar NCAA players based on physical traits and performance.")

df, similarity_matrix = load_and_process()

selected_player = st.selectbox("Select a player to compare:", options=df["label"], index=0)
num_matches = st.slider("Number of similar players to show:", 3, 10, 5)

# --- Similarity Lookup ---
target_idx = df[df["label"] == selected_player].index[0]
target_row = df.iloc[target_idx]

st.markdown("### 🎯 Target Player:")
st.markdown(f"**{target_row['summary']}** — {target_row['school']} ({target_row['year']})")

similar_indices = similarity_matrix[target_idx].argsort()[::-1][1:num_matches + 1]
results = df.iloc[similar_indices][["summary", "school", "year"]].copy()
results["Similarity Score"] = [similarity_matrix[target_idx][i] for i in similar_indices]

st.markdown("### ✅ Top Similar Players:")
st.dataframe(results.reset_index(drop=True))