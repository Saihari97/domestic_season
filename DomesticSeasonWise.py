import streamlit as st
import pandas as pd
#import os
import numpy as np

# --- Define Constants ---
DEFAULT_LEAGUE = 'Select a League'
DEFAULT_TEAM = 'Select a Team'

# --- 1. Data Loading Function (Cached) ---
@st.cache_data
def load_data(file_name):
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # file_path = os.path.join(script_dir, file_name)
    
    # if not os.path.exists(file_path):
    #     st.error(f"FATAL ERROR: The file '{file_name}' was not found.")
    #     return pd.DataFrame()

    try:
        df = pd.read_excel(file_name)
        return df
    except Exception as e:
        st.error(f"Error reading '{file_name}': {e}")
        return pd.DataFrame()

# --- 2. Main Application Function ---
def app(season_restricted_stats_final):
    # CSS for Metric Delta size
    st.markdown("""
    <style>
    [data-testid="stMetricDelta"] { font-size: 0.8em; min-width: 0; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

    if season_restricted_stats_final.empty:
        st.markdown("<h1>Data failed to load.</h1>", unsafe_allow_html=True)
        return

    # --- Header ---
    st.markdown("<h1 style='text-align: center;'>Season so Far: 2024/25 v 2025/26</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:18px; color:gray;'>Compare teams on how they have fared in the domestic season</p>", unsafe_allow_html=True)

    # --- TOP SECTION: TEAM SELECTION ---
    league_options = [DEFAULT_LEAGUE] + sorted(season_restricted_stats_final['league'].unique().tolist())
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("Team 1")
        sel_league_1 = st.selectbox("League:", options=league_options, key='l1')
        t1_list = [DEFAULT_TEAM] + sorted(season_restricted_stats_final[season_restricted_stats_final['league']==sel_league_1]['team'].unique().tolist()) if sel_league_1 != DEFAULT_LEAGUE else [DEFAULT_TEAM]
        sel_team_1 = st.selectbox("Team:", options=t1_list, key='t1')

    with col_t2:
        st.subheader("Team 2")
        sel_league_2 = st.selectbox("League:", options=league_options, key='l2')
        t2_list = [DEFAULT_TEAM] + sorted(season_restricted_stats_final[season_restricted_stats_final['league']==sel_league_2]['team'].unique().tolist()) if sel_league_2 != DEFAULT_LEAGUE else [DEFAULT_TEAM]
        sel_team_2 = st.selectbox("Team:", options=t2_list, key='t2')

    # --- CENTERED RADIO BUTTON ---
    st.write("") # Padding
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        stat_view = st.radio(
            "Choose Stats Category:",
            options=["Attacking", "Defensive", "Overall"],
            horizontal=True,
            key="central_stat_selector"
        )
    st.divider()

    # --- METRICS DISPLAY ---
    main_col1, main_col2 = st.columns(2)

    # Helper function to render a season's metrics to avoid repeating code 4 times
    def render_team_season_metrics(team_name, season_code, prev_stats=None):
        if team_name == DEFAULT_TEAM:
            st.info("Select a team.")
            return None
        
        stats = season_restricted_stats_final[(season_restricted_stats_final['team']==team_name) & (season_restricted_stats_final['season']==season_code)]
        
        if stats.empty:
            st.warning(f"No data for {season_code}")
            return None

         # Calculations
        row = stats.iloc[0]
        g_pg = row['Goals/Game']
        xg_pg = row['Expected Goals/Game']
        gc_pg = row['Goals Conceded/Game']
        xga_pg = row['Expected Goals Conceded/Game']
        poss = row['Average_Possession']
        ppg = (3*row['Wins'] + row['Draws']) / row['matches']
        
        tackles_pg = row['Tackles_Tkl/Game']
        tacklesW_pg = row['Tackles_TklW/Game']/ row['Tackles_Tkl/Game']


        tackesdef3rd_perct_pg = row['Tackles_Def_3rd/Game'] / tackles_pg
        tackesmid3rd_perct_pg = row['Tackles_Mid_3rd/Game'] / tackles_pg
        tacklesatt3rd_perct_pg = row['Tackles_Att_3rd/Game'] /tackles_pg
        
        CrdY_ppg = row["CrdY/Game"]
        foulscommitted_ppg = row["Fouls_Commited/Game"]
        foulsdrawn_ppg = row["Fouls_Drawn/Game"]



        ontarget = row['Shot_OnTarget/Game']
        total_shots = row['Shots_Taken/Game']
        acc = ontarget / total_shots if total_shots > 0 else 0

        # UI Rendering based on stat_view
        if stat_view == "Attacking":
            st.metric("Goals", f"{g_pg:.2f}", delta=f"{g_pg - xg_pg:+.2f} vs xG")
        
            st.caption("Shots")
            
            delta_ot = f"{ontarget - prev_stats['ontarget']:+.1f} vs Prev" if prev_stats else '-'
            if delta_ot != '-':
                st.metric("#On-Target", f"{ontarget:.1f}", delta=delta_ot)
            else:
                st.metric("#On-Target", f"{ontarget:.1f}", delta=delta_ot,delta_color="off",delta_arrow="off")

            delta_acc = f"{(acc - prev_stats['acc'])*100:+.1f}% vs Prev" if prev_stats else '-'
            if delta_acc != '-':
                st.metric("On-Target Accuracy", f"{acc*100:.1f}%", delta=delta_acc)
            else:
                st.metric("On-Target Accuracy", f"{acc*100:.1f}%", delta=delta_acc,delta_color="off",delta_arrow="off")
            
        
        elif stat_view == "Defensive":
            st.metric("Goals Conceded", f"{gc_pg:.2f}", delta=f"{gc_pg - xga_pg:+.2f} vs xGA", delta_color='inverse')

            
            st.caption("Tackles:")

            delta_tackles = f"{(tackles_pg - prev_stats['tackles_pg']):.1f}% vs Prev" if prev_stats else '-'
            if delta_tackles != '-':
                st.metric("Tackles Attempted", f"{tackles_pg:.1f}",delta=f"{delta_tackles}")
            else:
                st.metric("Tackles Attempted", f"{tackles_pg:.1f}",delta=f"{delta_tackles}",delta_color="off",delta_arrow="off")

            
            delta_tacklesW = f"{(tacklesW_pg - prev_stats['tacklesW_pg'])*100:+.1f}% vs Prev" if prev_stats else '-'
            if delta_tacklesW !='-':
                st.metric("Tackles Won", f"{tacklesW_pg*100:.1f}%",delta=f"{delta_tacklesW}")
            else:
                st.metric("Tackles Won", f"{tacklesW_pg*100:.1f}%",delta=f"{delta_tacklesW}",delta_color="off",delta_arrow="off")

            st.caption("Tackles Intensity:")

            delta_tacklesatt3rd = f"{(tacklesatt3rd_perct_pg - prev_stats['tacklesatt3rd_perct_pg'])*100:+.1f}% vs Prev" if prev_stats else '-'
            if delta_tacklesatt3rd !='-':
                st.metric("Tackles in Att 3rd", f"{tacklesatt3rd_perct_pg*100:.1f}%",delta=f"{delta_tacklesatt3rd}")
            else:
               st.metric("Tackles in Att 3rd", f"{tacklesatt3rd_perct_pg*100:.1f}%",delta=f"{delta_tacklesatt3rd}",delta_color="off",delta_arrow="off")

            delta_tacklesdef3rd = f"{(tackesdef3rd_perct_pg - prev_stats['tackesdef3rd_perct_pg'])*100:+.1f}% vs Prev" if prev_stats else '-'
            if delta_tacklesdef3rd !='-':
                st.metric("Tackles in Def 3rd", f"{tackesdef3rd_perct_pg*100:.1f}%",delta=f"{delta_tacklesdef3rd}")
            else:
               st.metric("Tackles in Def 3rd", f"{tackesdef3rd_perct_pg*100:.1f}%",delta=f"{delta_tacklesdef3rd}",delta_color="off",delta_arrow="off")
            

        else: # Overall
            delta_ppg = f"{ppg - prev_stats['ppg']:+.2f} vs Prev" if prev_stats else '-'
            if delta_ppg!='-':
                st.metric("Points", f"{ppg:.1f}", delta=delta_ppg)
            else:
                st.metric("Points", f"{ppg:.1f}", delta=delta_ppg,delta_color="off",delta_arrow="off")

            delta_poss = f"{poss - prev_stats['poss']:.0f}% vs Prev" if prev_stats else '-'
            if delta_poss != '-':
                st.metric("Possession", f"{poss:.0f}%", delta=delta_poss)
            else:
                st.metric("Possession", f"{poss:.0f}%", delta=delta_poss,delta_color="off",delta_arrow="off")

            delta_CrdY_ppg = f"{CrdY_ppg - prev_stats['CrdY_ppg']:+.1f} vs Prev" if prev_stats else '-'
            if delta_CrdY_ppg != '-':
                st.metric("Yellow Cards", f"{CrdY_ppg:.1f}", delta=delta_CrdY_ppg)
            else:
                st.metric("Yellow Cards", f"{CrdY_ppg:.1f}", delta=delta_CrdY_ppg,delta_color="off",delta_arrow="off")
            
            delta_fouls_commited = f"{(foulscommitted_ppg - prev_stats['foulscommitted_ppg']):.1f}% vs Prev" if prev_stats else '-'
            if delta_fouls_commited!='-':
                st.metric("Fouls Committed", f"{foulscommitted_ppg:.1f}",delta=f"{delta_fouls_commited}",delta_color='inverse')
            else:
                st.metric("Fouls Committed", f"{foulscommitted_ppg:.1f}",delta=f"{delta_fouls_commited}",delta_color="off",delta_arrow="off")
            
            delta_foulsdrawn = f"{(foulsdrawn_ppg - prev_stats['foulsdrawn_ppg']):.1f}% vs Prev" if prev_stats else '-'
            if delta_foulsdrawn !='-':
                st.metric("Fouls Drawn", f"{foulsdrawn_ppg:.1f}",delta=f"{delta_foulsdrawn}")
            else:
                st.metric("Fouls Drawn", f"{foulsdrawn_ppg:.1f}",delta=f"{delta_foulsdrawn}",delta_color="off",delta_arrow="off")

        return {"poss": poss, "acc": acc, "ontarget": ontarget, "ppg": ppg,"tackles_pg":tackles_pg,"tacklesW_pg":tacklesW_pg,"tackesdef3rd_perct_pg":tackesdef3rd_perct_pg,
                "tacklesatt3rd_perct_pg":tacklesatt3rd_perct_pg,"CrdY_ppg":CrdY_ppg,"foulscommitted_ppg":foulscommitted_ppg,"foulsdrawn_ppg":foulsdrawn_ppg}

    # Execute Rendering
    with main_col1:
        st.write(f"**{sel_team_1}**")
        s1, s2 = st.columns(2)
        with s1:
            st.caption("2024/25: Per Game")
            t1_s1_data = render_team_season_metrics(sel_team_1, '2024/2025')
        with s2:
            st.caption("2025/26: Per Game")
            render_team_season_metrics(sel_team_1, '2025/2026', prev_stats=t1_s1_data)

    with main_col2:
        st.write(f"**{sel_team_2}**")
        s1, s2 = st.columns(2)
        with s1:
            st.caption("2024/25: Per Game")
            t2_s1_data = render_team_season_metrics(sel_team_2, '2024/2025')
        with s2:
            st.caption("2025/26: Per Game")
            render_team_season_metrics(sel_team_2, '2025/2026', prev_stats=t2_s1_data)

if __name__ == '__main__':
    df_main = load_data('1226_FBREF Aggregated.xlsx')
    app(df_main)

