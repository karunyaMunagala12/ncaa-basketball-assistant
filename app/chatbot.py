import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import json
from sentence_transformers import SentenceTransformer
import pinecone
from groq import Groq
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
from scraper import scrape_player
import re

# === ENV ===
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# === INIT Services ===
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pinecone.Index("team-scouting")

groq_client = Groq(api_key=GROQ_API_KEY)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# === Streamlit Sidebar ===
st.set_page_config(page_title="🏀 Basketball Tool", layout="wide")
st.sidebar.title("🏀 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["💬 Chatbot Assistant", "🏀 Team Scouting", "🔍 Player Lookup", "🔁 Player Comparison", "🕵️ Opponent Weakness"]
)

def show_chatbot():
    st.markdown("""
💡 <b>How it works:</b><br>
This assistant uses <b>NCAA team summaries</b> from the <i>Team Scouting</i> dataset to answer your questions.<br><br>

📌 <b>What you can ask:</b><br>
• Team performance in a season<br>
<i>e.g., "How did Purdue perform in 2023?"</i><br>
• Offensive & defensive efficiency<br>
<i>e.g., "Was Illinois better defensively in 2021?"</i><br>
• Tournament seed or round<br>
<i>e.g., "What seed did Kansas have in 2021?"</i><br><br>

🚫 <b>Limitations:</b><br>
• ❌ No player stats (use Player Lookup module)<br>
• ❌ No turnover, rebound, or 3-point stats available<br>
• ❌ No bracket-specific game results<br>
• ✅ Only supports NCAA teams from 2008–2025<br><br>

📖 <b>Tip:</b> Stick to team-level topics like offense, defense, seed, or round.
""", unsafe_allow_html=True)

    st.title("💬 LLM-Powered Basketball Assistant")
    st.markdown("Ask questions about team performance using Team Scouting data.")

    with st.expander("💡 Need ideas? Try asking..."):
        st.markdown("""
        - *How did Purdue perform in 2023?*  
        - *Was Illinois better defensively in 2021?*  
        - *How efficient was Duke’s offense in 2023?*  
        - *What seed did Kansas have in 2021?*  
        - *Did Alabama improve from 2022 to 2023?*
        """)

  
    INDEX_NAME = "team-scouting"
    index = pinecone.Index(INDEX_NAME)


    user_query = st.text_input("💬 Ask your question")

    blocked_keywords = ["turnover", "rebound", "3pt", "3-point", "three point", "steal", "block", "free throw"]
    if user_query and any(word in user_query.lower() for word in blocked_keywords):
        st.warning("⚠️ Sorry! This assistant only supports team-level stats like efficiency, seed, and round.\nTry: *“How did Purdue perform in 2023?”*")
        return

    if user_query:
        with st.spinner("🔍 Retrieving context and generating answer..."):
            try:
                query_emb = embed_model.encode(user_query).tolist()
                result = index.query(vector=query_emb, top_k=20, include_metadata=True)
                all_matches = result.matches

                # === Smart Filtering ===
                years = re.findall(r"(20\d{2})", user_query)
                team_match = re.search(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b", user_query)
                target_team = team_match.group().strip() if team_match else None

                filtered_matches = []

                for match in all_matches:
                    meta_year = str(match.metadata.get("year", ""))
                    meta_team = str(match.metadata.get("team", "")).lower()

                    if (not years or meta_year in years) and (not target_team or target_team.lower() in meta_team):
                        filtered_matches.append(match)

                matches_to_use = filtered_matches if filtered_matches else all_matches

                context_chunks, sources = [], []
                for match in matches_to_use:
                    meta = match.metadata
                    context_chunks.append(meta.get("summary", ""))
                    sources.append(f"{meta.get('team', 'Unknown')} ({meta.get('year', 'Unknown')})")

                context = "\n".join(context_chunks)
                prompt = f"""You are a helpful NCAA basketball assistant.
Use only the information from the context below to answer the question.
If no relevant information is found, say: "Not enough data in the retrieved NCAA stats."

CONTEXT:
{context}

Question: {user_query}
"""

                response = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}]
                )

                st.success("✅ Answer:")
                st.write(response.choices[0].message.content)

                with st.expander("📄 Retrieved context chunks"):
                    for i, chunk in enumerate(context_chunks):
                        st.markdown(f"**Chunk {i+1}:**")
                        st.code(chunk)

                with st.expander("🔗 Sources used"):
                    st.write("\n".join(sources))

            except Exception as e:
                st.error("❌ LLM Failed to respond.")
                st.error(str(e))

    st.markdown("""
    <div class="tip-box">
        💬 <b>Quick Tip:</b> You can ask:  
        • "How did Purdue perform in 2023?"  
        • "Was Texas better defensively in 2022 or 2023?"  
        • "What seed did Illinois have in 2021?"  
        • "Which team had best defense in 2022?"  
    </div>
    """, unsafe_allow_html=True)

def show_opponent_weakness():
    st.markdown("""
    > 🧠 **How this works:** Select a team and season to reveal opponent weaknesses based on NCAA stats.  
    We highlight areas where the team struggles:
    - **EFG_D** (Effective FG% Defense) — Higher = worse at defending shots  
    - **TOR** (Turnover Rate) — Higher = commits more turnovers  
    - **ORB** (Offensive Rebound %) — Lower = fewer second chances  
    - **ADJDE** (Adjusted Defensive Efficiency) — Higher = worse defense overall
    
    ✅ Use these insights to strategize matchups and tailor game plans.
    """)

    st.title("🕵️ Opponent Weakness Analyzer")

    # Load the dataset
    filepath = "data/cleaned/cbb_cleaned.csv"
    try:
        df = pd.read_csv(filepath)
    except:
        st.error("Could not load cbb_cleaned.csv")
        return

    years = sorted(df["YEAR"].dropna().unique(), reverse=True)
    year = st.selectbox("Select Year:", years)
    teams = sorted(df[df["YEAR"] == year]["TEAM"].unique())
    team = st.selectbox("Select Team:", teams)

    row = df[(df["TEAM"] == team) & (df["YEAR"] == year)]
    if row.empty:
        st.warning("No data for selected team/year.")
        return

    row = row.iloc[0]

    # Define metrics and interpretations
    weaknesses = {
        "EFG_D": (row["EFG_D"], "Higher value = Worse FG defense"),
        "TOR": (row["TOR"], "Higher value = More turnovers"),
        "ORB": (100 - row["ORB"], "Lower % = Weak on offensive boards"),
        "ADJDE": (row["ADJDE"], "Higher = Worse defensive efficiency"),
    }

    st.subheader(f"📉 Weakness Profile for {team} ({year})")
    for metric, (val, comment) in weaknesses.items():
        st.markdown(f"- **{metric}**: {val:.2f} – {comment}")

    # Bar chart visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(weaknesses.keys()),
        y=[v[0] for v in weaknesses.values()],
        text=[v[1] for v in weaknesses.values()],
        textposition="outside"
    ))
    fig.update_layout(title=f"{team}'s Potential Weakness Metrics ({year})",
                      yaxis_title="Metric Value")
    st.plotly_chart(fig)

    st.markdown("---")
    st.markdown("### 🎯 Game Plan Suggestions:")

    if row["EFG_D"] > 50:
        st.markdown("- 📌 **Attack mid-range and paint** — Opponent struggles to contest shots.")
    if row["TOR"] > 18:
        st.markdown("- 📌 **Press or trap defense** — Opponent prone to turnovers.")
    if row["ORB"] < 30:
        st.markdown("- 📌 **Crash offensive boards** — Weakness in securing rebounds.")
    if row["ADJDE"] > 105:
        st.markdown("- 📌 **Push tempo** — Poor defensive efficiency overall.")

    st.markdown("✅ Tailor your game strategy by leveraging these exploitable weaknesses.")

def add_synthetic_season(df_stats):
    class_order = ['FR', 'SO', 'JR', 'SR', 'GR']
    season_map = {cls: i + 1 for i, cls in enumerate(class_order)}
    if "Class" in df_stats.columns:
        df_stats["season"] = df_stats["Class"].map(season_map).ffill()
    else:
        df_stats["season"] = list(range(1, len(df_stats) + 1))
    return df_stats


def show_player_lookup():
    st.markdown(
        "> ⚠️ **Note:** Player lookup only works for NCAA players listed on "
        "[Sports Reference](https://www.sports-reference.com/cbb/seasons/)."
    )
    st.title("🔍 Player Stats Lookup")
    st.markdown("Type a player's name to fetch real-time summary and stats.")

    # Load player_links
    try:
        with open("data/player_links.json") as f:
            player_links = json.load(f)
    except Exception as e:
        st.error("❌ Could not load player_links.json")
        st.exception(e)
        return

    player_name = st.text_input("Enter player name (e.g., Luka Garza, Caitlin Clark):").strip()

    if player_name:
        matches = [link for link in player_links if player_name.lower().replace(" ", "-") in link.lower()]
        if matches:
            selected_url = st.selectbox("Select a matching player:", matches)

            if st.button("🔍 Fetch Player Data"):
                with st.spinner("Scraping player data..."):
                    player_data = scrape_player(selected_url)

                    if player_data:
                        st.markdown(f"### 🧍 Player: {player_data['name']}")
                        st.markdown(f"**Position**: {player_data['position']}")
                        st.markdown(f"**Height**: {player_data['height']}")
                        st.markdown(f"**Weight**: {player_data['weight']}")
                        st.markdown(f"**School**: {player_data['school']}")

                        

                        if player_data['stats']:
                            st.markdown("### 📊 Per-Game Stats")
                            df_stats = pd.DataFrame(player_data['stats'])
                            df_stats = add_synthetic_season(df_stats)

                            st.dataframe(df_stats)

                            st.markdown("ℹ️ **Note on Season Column**: `1 = FR`, `2 = SO`, `3 = JR`, `4 = SR`, `5 = GR`. Values like `2.5` indicate redshirt/mid-year transfer seasons.")

                            try:
                                for col in ["PTS", "AST", "TRB"]:
                                    df_stats[col] = pd.to_numeric(df_stats[col], errors="coerce")

                                fig = go.Figure()
                                fig.add_trace(go.Scatter(x=df_stats["season"], y=df_stats["PTS"], name="PTS", mode="lines+markers"))
                                fig.add_trace(go.Scatter(x=df_stats["season"], y=df_stats["AST"], name="AST", mode="lines+markers"))
                                fig.add_trace(go.Scatter(x=df_stats["season"], y=df_stats["TRB"], name="REB", mode="lines+markers"))
                                fig.update_layout(title="📈 Career Trends (PTS, AST, REB)", xaxis_title="Season", yaxis_title="Stat Value")
                                st.plotly_chart(fig)

                            except Exception as e:
                                st.warning("📉 Could not render line chart.")
                                st.exception(e)
                        else:
                            st.warning("No stats found.")
                    else:
                        st.error("Failed to fetch player data.")
        else:
            st.warning("No matching players found in the index.")


def compare_players():
    st.markdown("""
> 🎯 **How this works:**
- Enter two NCAA player names (e.g., *Caitlin Clark*, *Luka Garza*).
- The app scrapes their per-game stats from [Sports Reference](https://www.sports-reference.com/cbb/).
- It computes **average stats** across all seasons and calculates a **Game Impact Score** using weighted metrics like PTS, AST, REB, and FG%.
- Based on this score, you'll see:
    - 📊 A stats table
    - 🕸️ A radar chart of performance
    - 📉 A horizontal bar chart comparison
    - 🏆 A recommended better pick
    - 🧠 Specific reasons explaining the pick

**Tip:** Only NCAA players listed in our player index will work. If a name doesn’t show up, try using different spellings or abbreviations.
""")

    st.title("🔁 Compare Two Players")

    try:
        with open("data/player_links.json") as f:
            player_links = json.load(f)
    except:
        st.error("❌ Failed to load player list.")
        return

    name1 = st.text_input("First player name:")
    name2 = st.text_input("Second player name:")

    if name1 and name2:
        matches1 = [link for link in player_links if name1.lower().replace(" ", "-") in link.lower()]
        matches2 = [link for link in player_links if name2.lower().replace(" ", "-") in link.lower()]

        if matches1 and matches2:
            with st.spinner("Scraping player data..."):
                data1 = scrape_player(matches1[0])
                data2 = scrape_player(matches2[0])

                if data1 and data2:
                    df1 = pd.DataFrame(data1["stats"])
                    df2 = pd.DataFrame(data2["stats"])

                    # --- Convert to numeric
                    cols = ["PTS", "AST", "TRB", "MP", "FG%", "3P%", "FT%", "STL", "BLK", "TOV"]
                    for df in [df1, df2]:
                        for col in cols:
                            df[col] = pd.to_numeric(df[col], errors="coerce")

                    # --- Average Stats
                    df1_avg = df1[cols].mean().round(2)
                    df2_avg = df2[cols].mean().round(2)

                    st.subheader("📊 Average Per-Game Stats")
                    comp_df = pd.DataFrame({data1["name"]: df1_avg, data2["name"]: df2_avg})
                    st.dataframe(comp_df)

                    # --- Horizontal bar chart (Recommended Comparison)
                    compare_df = pd.DataFrame({
                        "Metric": list(df1_avg.index),
                        data1["name"]: df1_avg.values,
                        data2["name"]: df2_avg.values
                    }).set_index("Metric")

                    st.markdown("### 📉 Side-by-Side Stat Comparison")

                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        y=compare_df.index,
                        x=compare_df[data1["name"]],
                        name=data1["name"],
                        orientation='h'
                    ))

                    fig.add_trace(go.Bar(
                        y=compare_df.index,
                        x=compare_df[data2["name"]],
                        name=data2["name"],
                        orientation='h'
                    ))

                    fig.update_layout(
                        barmode='group',
                        title="📊 Player Stat Comparison",
                        xaxis_title="Per-Game Stat",
                        yaxis_title="",
                        height=500
                    )

                    st.plotly_chart(fig)

                    # --- Game Impact Score (custom weighted metric)
                    weights = {
                        "PTS": 0.3, "AST": 0.2, "TRB": 0.15, "STL": 0.1, "BLK": 0.1,
                        "FG%": 0.05, "3P%": 0.05, "FT%": 0.03, "MP": 0.02
                    }

                    score1 = sum(df1_avg.get(k, 0) * w for k, w in weights.items())
                    score2 = sum(df2_avg.get(k, 0) * w for k, w in weights.items())

                    better = data1["name"] if score1 > score2 else data2["name"]
                    st.success(f"🏆 **{better}** is the better pick based on weighted performance metrics.")

                    # --- Reasoning
                    st.markdown("### 🧠 Why?")
                    for stat, weight in weights.items():
                        v1, v2 = df1_avg.get(stat, 0), df2_avg.get(stat, 0)
                        if abs(v1 - v2) >= 0.5:
                            winner = data1["name"] if v1 > v2 else data2["name"]
                            st.markdown(f"- **{winner}** leads in `{stat}`: {v1} vs {v2}")

                else:
                    st.error("⚠️ Could not scrape one of the players.")
        else:
            st.warning("⚠️ Please enter valid NCAA player names.")


def show_team_scouting():
    st.markdown(
    "> 📘 **Instructions:** Select any two teams from the chosen season to compare NCAA performance metrics. "
    "Only teams available in our cleaned dataset will appear in the dropdown. "
    "Data includes metrics like Adjusted Efficiency, FG%, Rebounds, and more."
)
    st.title("🏀 Team Scouting")
    st.markdown("Compare two teams' performance metrics for a given season.")

    try:
        filepath = "data/cleaned/cbb_cleaned.csv"
        if not os.path.exists(filepath):
            st.error(f"File not found: {filepath}")
            return

        df = pd.read_csv(filepath)

        required_cols = ["TEAM", "YEAR", "ADJOE", "ADJDE", "EFG_O", "EFG_D", "TOR", "TORD", "ORB", "FTR"]
        if not all(col in df.columns for col in required_cols):
            st.error("Missing expected columns in the dataset.")
            return

        st.markdown("### 📅 Select a Season")
        years = sorted(df["YEAR"].dropna().unique(), reverse=True)
        year_choice = st.selectbox("Season:", years)

        season_df = df[df["YEAR"] == year_choice]
        teams = sorted(season_df["TEAM"].dropna().unique())

        st.markdown("### 🆚 Select Two Teams to Compare")
        team_choices = st.multiselect("Teams:", teams, default=teams[:2])
        if len(team_choices) != 2:
            st.warning("Please select exactly 2 teams.")
            return

        normalize = st.checkbox("⚖️ Normalize metrics (0–1 scale)", value=False)

        metrics = {
            "ADJOE": "Adjusted Offensive Efficiency",
            "ADJDE": "Adjusted Defensive Efficiency",
            "EFG_O": "Effective FG% (Offense)",
            "EFG_D": "Effective FG% (Defense)",
            "TOR": "Turnover % (Offense)",
            "TORD": "Turnover % (Defense)",
            "ORB": "Offensive Rebound %",
            "FTR": "Free Throw Rate"
        }

        fig = go.Figure()

        for team in team_choices:
            row = season_df[season_df["TEAM"] == team]
            if row.empty:
                continue

            team_stats = row.iloc[0]
            values = []
            for k in metrics.keys():
                val = team_stats[k]
                if normalize:
                    max_val = df[k].max()
                    val = val / max_val if max_val else 0
                values.append(val)

            fig.add_trace(go.Bar(
                name=f"{team} ({year_choice})",
                x=list(metrics.values()),
                y=values,
                text=[round(v, 2) for v in values],
                textposition='auto'
            ))

        fig.update_layout(
            barmode='group',
            xaxis_title="Metrics",
            yaxis_title="Value (Normalized)" if normalize else "Raw Value",
            title=f"Team Comparison – {team_choices[0]} vs {team_choices[1]} ({year_choice})",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Raw Values")
        for team in team_choices:
            row = season_df[season_df["TEAM"] == team]
            if not row.empty:
                stats = {k: row.iloc[0][k] for k in metrics.keys()}
                st.markdown(f"**{team}**")
                st.write(stats)

        with st.expander("📘 Metric Definitions"):
            for key, desc in metrics.items():
                st.markdown(f"**{key}**: {desc}")

    except Exception as e:
        st.error("❌ Failed to load or display team scouting.")
        st.exception(e)


# === Routing ===
if page == "💬 Chatbot Assistant":
    show_chatbot()
elif page == "🏀 Team Scouting":
    show_team_scouting()

elif page == "🕵️ Opponent Weakness":
    show_opponent_weakness()

elif page == "🔍 Player Lookup":
    show_player_lookup()

elif page == "🔁 Player Comparison":
    compare_players()
