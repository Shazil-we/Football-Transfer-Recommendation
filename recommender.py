import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist
import os

# --- Role Features for Calculation (Same as before) ---
ROLE_FEATURE_SETS = {
    "DEF_COMMON": ['Ast_p90','KP_p90','xAG_p90','SCA90','GCA90','Gls_p90','Tkl_p90','TklW_p90','Int_p90','Blocks_stats_defense_p90','Clr_p90'],
    "MID_SCORING": ['Gls_p90','xG_p90','Sh_p90','SoT_p90'],
    "MID_PASSING": ['PrgP_p90','Touches_p90','1/3_p90','PPA_p90','Cmp_p90'],
    "MID_CREATING": ['Ast_p90','KP_p90','xAG_p90','SCA90','GCA90'],
    "FWD_COMMON": ['Ast_p90','KP_p90','xAG_p90','SCA90','GCA90','Gls_p90','Succ_p90','Att_stats_possession_p90','PrgP_p90','PrgC_p90','PPA_p90','PrgR_p90'],
    "FWD_SCORING": ['Gls_p90','xG_p90','Sh_p90','SoT_p90','G/SoT','PrgR_p90'],
    "FWD_PASSING": ['Crs_p90','Succ_p90','Att_stats_possession_p90','PrgC_p90'],
    "FWD_CREATING": ['Ast_p90','xAG_p90','KP_p90','SCA90','GCA90','PPA_p90','TB_p90'],
    "GK_COMMON": ['GA90','Save%','CS%','Saves','SoTA']
}

# --- 4 Major Attributes to Display per Role ---
DISPLAY_FEATURES = {
    "CB": ["Tkl_p90", "Int_p90", "Clr_p90", "Blocks_stats_defense_p90"],
    "FB": ["Tkl_p90", "Crs_p90", "Succ_p90", "PrgP_p90"],
    "CDM": ["Tkl_p90", "Int_p90", "Cmp_p90", "PrgP_p90"],
    "CM": ["Cmp_p90", "PrgP_p90", "SCA90", "KP_p90"],
    "CAM": ["SCA90", "GCA90", "Ast_p90", "xAG_p90"],
    "WINGER": ["Succ_p90", "Crs_p90", "SCA90", "PrgC_p90"],
    "ST": ["Gls_p90", "xG_p90", "Sh_p90", "SoT_p90"],
    "GK": ["Save%", "CS%", "GA90", "PSxG"] # Assuming PSxG exists, else fallback handled
}

ROLE_FEATURES = {}

def map_specificpos_to_subrole(s):
    if pd.isna(s): return None
    s_up = str(s).upper()
    if "CENTER" in s_up or "CB" in s_up: return "CB"
    if "FULL" in s_up or s_up in ("LB","RB","LEFT BACK","RIGHT BACK","FULL BACK"): return "FB"
    if "CDM" in s_up: return "CDM"
    if "CAM" in s_up: return "CAM"
    if s_up == "CM" or "CM" in s_up: return "CM"
    if "STRIKER" in s_up or "ST" in s_up: return "ST"
    if "WINGER" in s_up or s_up in ("LW","RW"): return "WINGER"
    return None

class TransferRecommender:
    def __init__(self, data_dir="."):
        self.data_dir = data_dir
        self.dfs = {}
        self.is_loaded = False

    def load_data(self):
        print(f"--- Loading data from: {os.path.abspath(self.data_dir)} ---")
        try:
            self.dfs['def'] = pd.read_csv(os.path.join(self.data_dir, "Defenders.csv"))
            self.dfs['mid'] = pd.read_csv(os.path.join(self.data_dir, "Midfielders.csv"))
            self.dfs['fwd'] = pd.read_csv(os.path.join(self.data_dir, "Forwards.csv"))
            self.dfs['gk'] = pd.read_csv(os.path.join(self.data_dir, "Goalkeepers.csv"))
            
            for key in ['def', 'mid', 'fwd']:
                if 'SpecificPos' in self.dfs[key].columns:
                    self.dfs[key]['SubRole'] = self.dfs[key]['SpecificPos'].apply(map_specificpos_to_subrole)
            self.dfs['gk']['SubRole'] = 'GK'

            self._init_features_map()
            self.is_loaded = True
            print("✅ Data loaded.")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.is_loaded = False

    def _init_features_map(self):
        df_def = self.dfs['def']
        df_mid = self.dfs['mid']
        df_fwd = self.dfs['fwd']
        df_gk = self.dfs['gk']
        global ROLE_FEATURES
        ROLE_FEATURES = {
            "CB": [c for c in ROLE_FEATURE_SETS["DEF_COMMON"] if c in df_def.columns],
            "FB": [c for c in ROLE_FEATURE_SETS["DEF_COMMON"] + ['Crs_p90','PrgP_p90','Succ_p90'] if c in df_def.columns],
            "CDM": [c for c in (ROLE_FEATURE_SETS["DEF_COMMON"] + ROLE_FEATURE_SETS["MID_PASSING"]) if c in df_mid.columns],
            "CM": [c for c in (ROLE_FEATURE_SETS["MID_CREATING"] + ROLE_FEATURE_SETS["MID_PASSING"]) if c in df_mid.columns],
            "CAM": [c for c in (ROLE_FEATURE_SETS["MID_CREATING"] + ROLE_FEATURE_SETS["MID_SCORING"]) if c in df_mid.columns],
            "ST": [c for c in ROLE_FEATURE_SETS["FWD_COMMON"] if c in df_fwd.columns],
            "WINGER": [c for c in (ROLE_FEATURE_SETS["FWD_CREATING"] + ROLE_FEATURE_SETS["FWD_PASSING"]) if c in df_fwd.columns],
            "GK": [c for c in ROLE_FEATURE_SETS["GK_COMMON"] if c in df_gk.columns]
        }

    def get_role_dataframe(self, subrole):
        if subrole in ("CB","FB"): return self.dfs['def'], ROLE_FEATURES[subrole]
        if subrole in ("CDM","CM","CAM"): return self.dfs['mid'], ROLE_FEATURES[subrole]
        if subrole in ("ST","WINGER"): return self.dfs['fwd'], ROLE_FEATURES[subrole]
        if subrole == "GK": return self.dfs['gk'], ROLE_FEATURES[subrole]
        return None, []

    def get_clubs(self):
        if not self.is_loaded: self.load_data()
        if not self.dfs: return []
        clubs = set()
        for df in self.dfs.values():
            if 'Squad' in df.columns:
                clubs.update(df['Squad'].dropna().unique())
        return sorted(list(clubs))

    def recommend(self, club_name, subrole, top_k=10):
        if not self.is_loaded: self.load_data()
        df_role_all, features = self.get_role_dataframe(subrole)
        if df_role_all is None: return {"error": "Invalid subrole"}

        df_role = df_role_all[df_role_all['SubRole'] == subrole].copy()
        club_players = df_role[df_role['Squad'] == club_name].copy()
        world_players = df_role[df_role['Squad'] != club_name].copy()
        
        if club_players.empty: return {"error": f"No players found for {club_name} in role {subrole}"}

        # Scaling and Similarity
        combined = pd.concat([club_players[features], world_players[features]], axis=0).fillna(0)
        scaler = StandardScaler().fit(combined.values)
        club_scaled = scaler.transform(club_players[features].fillna(0).values)
        world_scaled = scaler.transform(world_players[features].fillna(0).values)
        club_centroid = np.nanmean(club_scaled, axis=0).reshape(1, -1)
        
        world_players['Fit_Cosine'] = cosine_similarity(world_scaled, club_centroid).flatten()
        world_players['Fit_Euclid'] = cdist(world_scaled, club_centroid, metric='euclidean').flatten()
        world_players['MinutesEvidence'] = world_players['90s'].fillna(0) if '90s' in world_players.columns else 0

        # Key Feature Logic
        world_scaled_df = pd.DataFrame(world_scaled, columns=features, index=world_players.index)
        key_feature_col = world_scaled_df.idxmax(axis=1)
        world_players['Key_Feature'] = key_feature_col
        world_players['Key_Feature_Value'] = [world_players.loc[idx, feat] for idx, feat in zip(world_players.index, key_feature_col)]

        # Ranking
        ranked = world_players.sort_values(by=['Fit_Cosine', 'Fit_Euclid', 'MinutesEvidence'], ascending=[False, True, False]).reset_index(drop=True)
        ranked['Rank'] = ranked.index + 1
        
        # Retrieve Display Attributes
        display_stats = DISPLAY_FEATURES.get(subrole, features[:4]) # Fallback to first 4 if not defined
        
        # Filter Available columns only
        available_display_stats = [col for col in display_stats if col in df_role.columns]

        topk = ranked.head(top_k)
        results = []
        for _, row in topk.iterrows():
            # Extract the 4 major attributes values
            stats_data = {stat.replace("_p90", ""): round(row[stat], 2) for stat in available_display_stats}
            
            player_data = {
                "rank": int(row['Rank']),
                "player": row['Player'],
                "nation": row['Nation'].split(' ')[-1] if 'Nation' in row and isinstance(row['Nation'], str) else "N/A", # Clean nation string
                "club": row['Squad'],
                "subrole": row['SubRole'],
                "age": int(row['Age']) if 'Age' in row else "N/A",
                "key_feature": row['Key_Feature'].replace("_p90", ""),
                "key_feature_value": round(row['Key_Feature_Value'], 2),
                "fit_cosine": round(row['Fit_Cosine'] * 100, 1),
                "display_stats": stats_data # Dictionary of specific stats
            }
            results.append(player_data)
            
        return {"results": results, "club": club_name, "role": subrole, "display_columns": [s.replace("_p90","") for s in available_display_stats]}