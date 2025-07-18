import pandas as pd
import json
import os

# --- Config ---
INPUT_FILES = [
    "data/cleaned/cbb_cleaned.csv",
    "data/cleaned/dev_march_madness_cleaned.csv"
]
OUTPUT_JSON = "data/json/team_scouting_data.json"

# --- Process ---
all_data = []

for path in INPUT_FILES:
    df = pd.read_csv(path).fillna("")
    print(f"\n📂 Columns in {os.path.basename(path)}:")
    print(df.columns.tolist())

    for _, row in df.iterrows():
        if "TEAM" in row and "ADJOE" in row:
            record = {
                "team": row.get("TEAM", ""),
                "year": row.get("YEAR", ""),
                "conference": row.get("CONF", ""),
                "seed": row.get("SEED", ""),
                "round": row.get("POSTSEASON", ""),
                "off_eff": row.get("ADJOE", ""),
                "def_eff": row.get("ADJDE", ""),
                "summary": (
                    f"{row.get('TEAM', '')} ({row.get('YEAR', '')}) from {row.get('CONF', '')} "
                    f"had an offensive efficiency of {row.get('ADJOE', '')} and defensive efficiency of {row.get('ADJDE', '')}. "
                    f"They reached round {row.get('POSTSEASON', '')} with seed {row.get('SEED', '')}."
                )
            }

        elif "Mapped_ESPN_Team_Name" in row:
            record = {
                "team": row.get("Mapped_ESPN_Team_Name", ""),
                "year": row.get("Season", ""),
                "conference": row.get("Mapped_Conference_Name", ""),
                "seed": row.get("Seed", ""),
                "round": row.get("Post-Season_Tournament", ""),
                "off_eff": row.get("Adjusted_Offensive_Efficiency", ""),
                "def_eff": row.get("Adjusted_Defensive_Efficiency", ""),
                "summary": (
                    f"{row.get('Mapped_ESPN_Team_Name', '')} ({row.get('Season', '')}) from {row.get('Mapped_Conference_Name', '')} "
                    f"had an offensive efficiency of {row.get('Adjusted_Offensive_Efficiency', '')} and defensive efficiency of {row.get('Adjusted_Defensive_Efficiency', '')}. "
                    f"They reached round {row.get('Post-Season_Tournament', '')} with seed {row.get('Seed', '')}."
                )
            }
        else:
            continue

        all_data.append(record)

# --- Output ---
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

with open(OUTPUT_JSON, "w") as f:
    json.dump(all_data, f, indent=2)

# Sample
print("\n🧪 Sample records:")
for r in all_data[:5]:
    print(json.dumps(r, indent=2))

print(f"\n✅ Team scouting data saved to: {OUTPUT_JSON}")