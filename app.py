import streamlit as st
import pandas as pd
import datetime
import os
import time
import streamlit.components.v1 as components

GITHUB_USER, GITHUB_REPO = "chiachan0108", "stock-data"
st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# [CSS 樣式終極修正版] - 徹底消滅所有點點，只留文字與外框發光
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap'); html, body, [class*="css"], .stApp, [data-testid="stHeader"], [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { font-family: 'Inter', 'Noto Sans TC', sans-serif !important; background-color: #0b0f19 !important; color: #e2e8f0 !important; -webkit-font-smoothing: antialiased; overscroll-behavior-y: none; } ::-webkit-scrollbar { width: 6px; height: 6px; } ::-webkit-scrollbar-track { background: rgba(11, 15, 25, 0.9); } ::-webkit-scrollbar-thumb { background: rgba(0, 242, 255, 0.3); border-radius: 10px; } ::-webkit-scrollbar-thumb:hover { background: rgba(0, 242, 255, 0.6); } [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu { visibility: hidden !important; display: none !important; } @keyframes fadeSlideUp { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } } .header-group { margin-top: -45px; margin-bottom: 5px; animation: fadeSlideUp 0.4s ease-out forwards; } .main-title { font-family: 'JetBrains Mono', monospace !important; font-weight: 700; letter-spacing: -2px; background: linear-gradient(90deg, #00f2ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(2.0rem, 6vw, 3.5rem); line-height: 1.1; margin: 0; } .status-pill { display: inline-flex; align-items: center; white-space: nowrap; background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); padding: 6px 16px; border-radius: 50px; font-size: 0.8rem; color: rgba(148, 163, 184, 0.9); margin-bottom: 20px; font-weight: 500; letter-spacing: 0.5px; } .status-val { color: #ffffff; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-left: 6px; } .section-header-container { margin-top: 25px; margin-bottom: 16px; display: flex; align-items: center; position: relative; animation: fadeSlideUp 0.5s ease-out forwards; } .section-accent { width: 4px; height: 34px; background: linear-gradient(180deg, #00f2ff, #0072ff); border-radius: 4px; margin-right: 14px; box-shadow: 0 0 12px rgba(0, 242, 255, 0.4); } .section-header-text { display: flex; flex-direction: column; justify-content: center; } .section-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: rgba(0, 242, 255, 0.9); letter-spacing: 2px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; line-height: 1; } .section-label-zh { font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: 1.5px; line-height: 1; } .section-line { flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 242, 255, 0.2), transparent); margin-left: 20px; } .stButton > button { background: rgba(0, 242, 255, 0.08) !important; color: #ffffff !important; border: 1px solid rgba(0, 242, 255, 0.4) !important; backdrop-filter: blur(8px) !important; border-radius: 10px !important; font-weight: 900 !important; text-shadow: -0.5px -0.5px 0 #000, 0.5px -0.5px 0 #000, -0.5px 0.5px 0 #000, 0.5px 0.5px 0 #000 !important; letter-spacing: 2px; width: 100% !important; min-height: 62px !important; font-size: 1.25rem !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; position: relative; padding: 0 !important; } .stButton > button:hover { background: rgba(0, 242, 255, 0.15) !important; border: 1px solid rgba(0, 242, 255, 0.8) !important; box-shadow: 0 0 25px rgba(0, 242, 255, 0.35) !important; transform: translateY(-2px) !important; } .dataframe-wrapper { animation: fadeSlideUp 0.7s ease-out forwards; padding: 2px; border-radius: 14px; background: linear-gradient(180deg, rgba(0,242,255,0.15) 0%, rgba(0,0,0,0) 100%); } 

/* 🔥 全域 Radio 魔法 - 徹底拔除原生與自訂的所有點點，鎖定像素細節，選取後外框發光 */
[data-testid="stRadio"] div[role="radiogroup"] {
    display: grid !important;
    grid-template-columns: repeat(1, 1fr) !important; /* 強制等寬避免跑版 */
    gap: 12px !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

/* 🚨 終極清道夫：將所有可能產生點點的元素全部隱藏！ */
[data-testid="stRadio"] div[role="radiogroup"] input[type="radio"] { display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] div[data-baseweb="radio"] > div:first-child { display: none !important; width: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; border: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p::before { content: none !important; display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p::after { content: none !important; display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p > strong::before { content: none !important; display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p > strong::after { content: none !important; display: none !important; }

[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #0b0f19 !important; 
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important; 
    padding: 16px 12px !important; /* 精準調整內距 */
    margin: 0 !important;
    cursor: pointer !important; 
    transition: all 0.3s ease !important;
    display: flex !important; 
    align-items: center !important;
    justify-content: center !important; /* 絕對置中 */
    box-sizing: border-box !important;
    width: 100% !important;
    text-align: center !important;
    min-height: 80px !important; /* 確保卡片高度統一 */
}

[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    border-color: rgba(0, 242, 255, 0.4) !important;
}

/* 🎯 選取時的終極發光質感 (背景微亮 + 邊框霓虹發光) */
[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked) {
    border: 1px solid #00f2ff !important; 
    background-color: rgba(0, 242, 255, 0.05) !important; /*淡淡的藍色暈染*/
    box-shadow: 0 0 15px rgba(0, 242, 255, 0.2), inset 0 0 8px rgba(0, 242, 255, 0.1) !important; /* 內外發光 */
}

/* 攔截選項文字容器，鎖定垂直置中 */
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
    width: 100% !important; 
    display: flex !important; 
    flex-direction: column !important; 
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* 鎖定上下文字的間距與對齊 */
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p {
    display: flex !important;
    flex-direction: column !important; /* 讓名稱與漲幅上下排列 */
    align-items: center !important; 
    justify-content: center !important;
    gap: 6px !important; /* 上下行間距 */
    margin: 0 !important;
    text-align: center !important;
    width: 100% !important;
    line-height: 1.1 !important;
}

/* 攔截 strong 標籤（策略名稱） */
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p > strong {
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', 'Noto Sans TC', monospace !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
}

/* 文字在選取時也霓虹發光 */
[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked) div[data-testid="stMarkdownContainer"] > p > strong {
    color: #00f2ff !important;
    font-weight: 800 !important;
    text-shadow: 0 0 8px rgba(0, 242, 255, 0.4) !important;
}

/* 🔥 數據表格 CSS 新增手機端表格滑動抗飄移穩定性 */
[data-testid="stDataFrame"] { border: 1px solid rgba(0, 242, 255, 0.25) !important; border-radius: 12px !important; padding: 4px !important; background-color: #0b0f19 !important; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4); overscroll-behavior-x: none !important; -webkit-overflow-scrolling: touch !important; touch-action: pan-x pan-y !important; transform: translateZ(0); } [data-testid="stDataFrame"] canvas { touch-action: pan-x pan-y !important; } [data-testid="stDataFrame"] th { background-color: #161b2a !important; color: #94a3b8 !important; border-bottom: 1px solid rgba(0, 242, 255, 0.2) !important; font-weight: 700 !important; } [data-testid="stDataFrame"] td { background-color: #0b0f19 !important; color: #ffffff !important; } .empty-state-glass { padding: 40px; text-align: center; background: linear-gradient(135deg, rgba(0, 242, 255, 0.05) 0%, rgba(11, 15, 25, 0.8) 100%); border: 1px dashed rgba(0, 242, 255, 0.3); border-radius: 16px; margin-top: 30px; animation: fadeSlideUp 0.6s ease-out forwards; backdrop-filter: blur(10px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); } .disclaimer-wrapper { background-color: #0e121a; border: 1px solid rgba(0, 242, 255, 0.2) !important; border-radius: 8px; padding: 16px 16px 10px 16px !important; margin-top: 35px !important; margin-bottom: 35px !important; display: flex; flex-direction: column; gap: 10px !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); animation: fadeSlideUp 0.8s ease-out forwards; } .footer-wrapper { margin-top: 60px; padding: 30px 10px 50px 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; justify-content: center !important; }

/* 個股反查雷達專屬 */
.search-box-glass { background: linear-gradient(135deg, rgba(11, 15, 25, 0.95) 0%, rgba(22, 27, 34, 0.85) 100%); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 16px; padding: 24px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); backdrop-filter: blur(12px); animation: fadeSlideUp 0.5s ease-out forwards; } .strat-badge-premium { background: linear-gradient(90deg, rgba(22, 27, 34, 0.9), rgba(11, 15, 25, 0.9)); border: 1px solid rgba(0, 242, 255, 0.3); border-left: 3px solid #00f2ff; padding: 8px 14px; border-radius: 6px; color: #e2e8f0; font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }

/* 🔥 新增：分頁 Tabs 專屬 Glassmorphism CSS */
[data-testid="stTabs"] { background-color: transparent !important; } [data-testid="stTabs"] button { background-color: rgba(11, 15, 25, 0.4) !important; border: 1px solid rgba(0, 242, 255, 0.1) !important; border-radius: 8px 8px 0 0 !important; color: #94a3b8 !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 700 !important; font-size: 1.1rem !important; padding: 12px 20px !important; transition: all 0.3s ease !important; } [data-testid="stTabs"] button[aria-selected="true"] { background: linear-gradient(180deg, rgba(0, 242, 255, 0.15) 0%, rgba(11, 15, 25, 0) 100%) !important; border-color: #00f2ff !important; color: #00f2ff !important; } [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #00f2ff !important; }
</style>""", unsafe_allow_html=True)

def highlight_pivot_full_row(row):
    styles = []
    for col_name, val in row.items():
        text_css = 'color: #ffffff;'
        if "漲幅" in str(col_name):
            try:
                v = float(val)
                if v > 0: text_css = 'color: #ff3333;'
                elif v < 0: text_css = 'color: #00ff33;'
            except: pass
        styles.append(f'font-weight: 800; {text_css}')
    return styles

# 🔥 [全域快取獲取模組]
@st.cache_data(ttl=60) 
def fetch_and_rename(filename):
    paths_to_check = [filename, f"quantum-scanner-web/{filename}", f"../{filename}"]
    df = pd.DataFrame()
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except: pass
    
    if df.empty and GITHUB_USER and GITHUB_REPO:
        try:
            url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{filename}"
            df = pd.read_csv(url)
        except: pass
        
    if df.empty: return pd.DataFrame()
    
    rename_map = {"股價代號": "代號", "公司名稱": "名稱", "產業別": "產業", "當日漲幅(%)": "漲幅(%)", "漲幅 (%)": "漲幅(%)", "季乖離": "季乖離(%)", "年乖離": "年乖離(%)", "月營收MoM(%)": "月營收MoM(%)", "月營收MoM (%)": "月營收MoM(%)", "月營收YoY(%)": "月營收YoY(%)", "月營收YoY (%)": "月營收YoY(%)", "今年以來累積營收YoY(%)": "今年營收YoY(%)", "今年營收YoY (%)": "今年營收YoY(%)", "近20日法人買賣超(張數)": "20日法人買賣超(張)", "近20日法人買超(張數)": "20日法人買賣超(張)", "近20日法人買賣超(張)": "20日法人買賣超(張)", "20日法人買賣超 (張)": "20日法人買賣超(張)"}
    if "代號" in df.columns: 
        df["代號"] = df["代號"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    return df.rename(columns=rename_map)

# 🌟 [預運算模組] 背景全自動計算各策略的平均漲幅與數量
@st.cache_data(ttl=60)
def precalculate_strategy_performance():
    keys = ['A', 'B', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O']
    filenames = [
        "strategy_a_result.csv", "strategy_b_result.csv", "strategy_d_result.csv", 
        "strategy_e_result.csv", "strategy_f_result.csv", "strategy_g_result.csv", 
        "strategy_h_result.csv", "strategy_j_result.csv", "strategy_k_result.csv",
        "strategy_l_result.csv", "strategy_m_result.csv", "strategy_n_result.csv",
        "strategy_o_result.csv"
    ]
    df_dict = {k: fetch_and_rename(f) for k, f in zip(keys, filenames)}
    
    def _calc(df_to_calc):
        count = len(df_to_calc) if not df_to_calc.empty else 0
        val = None
        if not df_to_calc.empty and "漲幅(%)" in df_to_calc.columns:
            val = pd.to_numeric(df_to_calc["漲幅(%)"], errors='coerce').mean()
            if pd.isna(val): val = None
        return {"count": count, "avg": val}

    perf = {k: _calc(v) for k, v in df_dict.items()}
    
    # Intersections for C, I
    df_c = pd.DataFrame()
    if not df_dict['A'].empty and not df_dict['B'].empty:
        df_c = df_dict['A'][df_dict['A']['代號'].isin(set(df_dict['A']['代號']).intersection(set(df_dict['B']['代號'])))]
    perf['C'] = _calc(df_c)
    
    df_i = pd.DataFrame()
    if not df_dict['A'].empty and not df_dict['H'].empty:
        df_i = df_dict['A'][df_dict['A']['代號'].isin(set(df_dict['A']['代號']).intersection(set(df_dict['H']['代號'])))]
    perf['I'] = _calc(df_i)
    
    # Combined logic for R and S
    dfs_to_concat = [d for d in df_dict.values() if not d.empty]
    if dfs_to_concat:
        df_combined = pd.concat(dfs_to_concat, ignore_index=True).drop_duplicates(subset=['代號'])
        id_map = {}
        for k, d in df_dict.items():
            if not d.empty:
                for sid in d['代號'].astype(str):
                    id_map.setdefault(sid, set()).add(k)
                    
        target_sids_r = [sid for sid, tags in id_map.items() if len(tags.intersection({"A", "B", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "O"})) >= 4]
        perf['R'] = _calc(df_combined[df_combined['代號'].astype(str).isin(target_sids_r)])
        
        if '現價' in df_combined.columns and '轉折值' in df_combined.columns:
            df_s_temp = df_combined.copy()
            df_s_temp['現價_num'] = pd.to_numeric(df_s_temp['現價'], errors='coerce')
            df_s_temp['轉折_num'] = pd.to_numeric(df_s_temp['轉折值'], errors='coerce')
            perf['S'] = _calc(df_s_temp[(df_s_temp['現價_num'] > df_s_temp['轉折_num']) & (df_s_temp['轉折_num'] > 0)])
        else:
            perf['S'] = {"count": 0, "avg": None}
    else:
        perf['R'] = {"count": 0, "avg": None}
        perf['S'] = {"count": 0, "avg": None}
        
    return perf

strategy_perf = precalculate_strategy_performance()

# 🌟 新增：最安全、無 HTML 的 Markdown 文字產生器 (搭配 CSS 攔截器完美排版)
def get_strat_label(key, base_name):
    data = strategy_perf.get(key, {"count": 0, "avg": None})
    val = data["avg"]
    
    if val is not None:
        sign = "+" if val > 0 else ""
        if val > 0:
            # 正報酬：使用刪除線 ~~ (CSS 會攔截轉為紅色 Badge)
            return f"**{key}. {base_name}** \n~~AVG: {sign}{val:.2f}%~~"
        elif val < 0:
            # 負報酬：使用斜體 * (CSS 會攔截轉為綠色 Badge)
            return f"**{key}. {base_name}** \n*AVG: {sign}{val:.2f}%*"
        else:
            # 零報酬：使用程式碼 ` (CSS 會攔截轉為灰色 Badge)
            return f"**{key}. {base_name}** \n`AVG: {sign}{val:.2f}%`"
    
    return f"**{key}. {base_name}** \n`AVG: --`"

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False

now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
data_date = now_taipei.strftime('%Y/%m/%d') if (now_taipei.hour >= 20) else (now_taipei - datetime.timedelta(days=1)).strftime('%Y/%m/%d')

st.markdown(f'''<div class="header-group"><h1 class="main-title">QUANTUM SCANNER</h1><div class="status-pill"><div class="pulse-dot-small"></div>LAST UPDATE : <span class="status-val">{data_date} 20:00</span></div></div>''', unsafe_allow_html=True)

# 🌟 全域戰情雷達總覽面板
st.markdown("<div class='section-header-container'><div class='section-accent'></div><div class='section-header-text'><span class='section-label-en'>GLOBAL RADAR</span><span class='section-label-zh'>全域戰情總覽</span></div><div class='section-line'></div></div>", unsafe_allow_html=True)

radar_keys = ['A', 'H', 'M', 'O', 'D', 'L', 'N', 'B', 'G', 'J', 'K', 'R']
name_map = {"A": "營收趨勢增長", "H": "財報三率三升", "M": "營收創高精選", "O": "合約負債爆發", "D": "法人籌碼吃貨", "L": "股本法人鎖碼", "N": "股本投信鎖碼", "B": "股價強勢動能", "G": "中長周期轉折", "J": "指標強勢共振", "K": "跨週期多矩陣", "R": "複式策略交集"}

c1, c2, c3, c4 = st.columns(4)
col_list = [c1, c2, c3, c4]
for idx, k in enumerate(radar_keys):
    data = strategy_perf.get(k, {"count": 0, "avg": None})
    avg = data["avg"]
    avg_str = "--"
    perf_cls = "perf-zero"
    if avg is not None:
        avg_str = f"{'+' if avg > 0 else ''}{avg:.2f}%"
        perf_cls = "perf-up" if avg > 0 else ("perf-down" if avg < 0 else "perf-zero")
        
    with col_list[idx % 4]:
        st.markdown(f'''<div style="background: linear-gradient(135deg, rgba(22, 27, 34, 0.8), rgba(11, 15, 25, 0.9)); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 12px; padding: 16px; margin-bottom: 15px; position: relative; overflow: hidden;"><div style="content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #00f2ff, transparent);"></div><div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase;">STRATEGY {k} · {name_map.get(k, k)}</div><div style="display: flex; align-items: baseline; justify-content: space-between;"><div><span style="font-size: 1.8rem; font-weight: 900; color: #ffffff; font-family: 'Inter', sans-serif;">{data['count']}</span><span style="font-size: 0.8rem; color: rgba(255,255,255,0.5); font-weight: 600; margin-left: 4px;">檔</span></div><div class="{perf_cls}" style="font-size: 1rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; {'color: #ff3333;' if avg > 0 else 'color: #00ff33;' if avg < 0 else 'color: #94a3b8;'}">{avg_str}</div></div></div>''', unsafe_allow_html=True)

# 🌟 獨立的個股反查雷達模組
def render_search_radar(location="top"):
    with st.expander("◈ 個股反查雷達 (輸入代號或名稱)", expanded=False):
        with st.form(key=f"search_{location}"):
            c_input, c_btn = st.columns([3, 1])
            search_query = c_input.text_input("輸入股票代號或名稱：", key=f"q_{location}", label_visibility="collapsed").strip()
            if c_btn.form_submit_button("🔍 啟動反查", use_container_width=True) and search_query:
                try:
                    s_a, s_b, s_d, s_e, s_f, s_g, s_h, s_j, s_k, s_l, s_m, s_n, s_o = map(fetch_and_rename, ["strategy_a_result.csv", "strategy_b_result.csv", "strategy_d_result.csv", "strategy_e_result.csv", "strategy_f_result.csv", "strategy_g_result.csv", "strategy_h_result.csv", "strategy_j_result.csv", "strategy_k_result.csv", "strategy_l_result.csv", "strategy_m_result.csv", "strategy_n_result.csv", "strategy_o_result.csv"])
                    hit_strategies = []; match_info = {"id": "", "name": "", "price": 0.0, "pivot": 0.0}
                    def check(df, name):
                        if not df.empty:
                            m = (df['代號'] == search_query) | (df['名稱'].astype(str).str.contains(search_query, na=False))
                            h = df[m]
                            if not h.empty:
                                match_info.update({"id": str(h.iloc[0]['代號']), "name": str(h.iloc[0]['名稱'])})
                                try: match_info.update({"price": float(h.iloc[0]['現價']), "pivot": float(h.iloc[0]['轉折值'])})
                                except: pass
                                hit_strategies.append(name)
                    
                    check(s_a, "A")
                    check(s_h, "H")
                    if 'A' in hit_strategies and 'B' in hit_strategies: hit_strategies.append("C")
                    if 'A' in hit_strategies and 'H' in hit_strategies: hit_strategies.append("I")
                    if match_info["price"] > match_info["pivot"] > 0: hit_strategies.append("S")
                    if len(hit_strategies) >= 4: hit_strategies.append("R")
                    
                    if hit_strategies:
                        badges = "".join([f"<div class='strat-badge-premium'><span>{s}</span></div>" for s in sorted(list(set(hit_strategies)))])
                        st.markdown(f'''<div class="search-box-glass"><div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px dashed rgba(0, 242, 255, 0.2); padding-bottom: 16px; margin-bottom: 16px;"><div style="font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 900; color: #ffffff;">{match_info['id']} <span style="font-size: 1.2rem; color: #e2e8f0; font-weight: 800; letter-spacing: 2px;">{match_info['name']}</span></div><div style="background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.4); padding: 4px 10px; border-radius: 4px; color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 800;">MATCHED</div></div><div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 12px;">標的當前符合：</div><div style="display: flex; flex-wrap: wrap; gap: 10px;">{badges}</div></div>''', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="empty-state-glass">Target Not Found or Input Error</div>', unsafe_allow_html=True)
                except Exception as e: st.error(str(e))

render_search_radar(location="top")

if not st.session_state['scan_completed']:
    st.markdown("<div class='section-header-container'><div class='section-accent'></div><div class='section-header-text'><span class='section-label-en'>STRATEGY CONFIGURATION</span><span class='section-label-zh'>策略類型選取</span></div><div class='section-line'></div></div>", unsafe_allow_html=True)
    
    t_fund, t_chip, t_tech, t_multi = st.tabs(["I. 基本面區", "II. 籌碼面區", "III. 技術面區", "IV. 多吻合區"])
    
    with t_fund:
        strat_fund = st.radio("基本面區", [get_strat_label("A", "營收趨勢增長"), get_strat_label("H", "財報三率三升"), get_strat_label("I", "營收財報雙能"), get_strat_label("M", "營收創高精選"), get_strat_label("O", "合約負債爆發")], label_visibility="collapsed")
        run_fund = st.button("啟動AI量化篩選", key="btn_fund", use_container_width=True)

    with t_chip:
        strat_chip = st.radio("籌碼面區", [get_strat_label("D", "法人籌碼吃貨"), get_strat_label("E", "市場區間共振"), get_strat_label("F", "左側超跌優質"), get_strat_label("L", "股本法人鎖碼"), get_strat_label("N", "股本投信鎖碼")], label_visibility="collapsed")
        run_chip = st.button("啟動AI量化篩選", key="btn_chip", use_container_width=True)

    with t_tech:
        strat_tech = st.radio("技術面區", [get_strat_label("B", "股價強勢動能"), get_strat_label("G", "中長周期轉折"), get_strat_label("J", "指標強勢共振"), get_strat_label("K", "跨週期多矩陣")], label_visibility="collapsed")
        run_tech = st.button("啟動AI量化篩選", key="btn_tech", use_container_width=True)

    with t_multi:
        strat_multi = st.radio("多吻合區", [get_strat_label("C", "營收股價雙能"), get_strat_label("R", "複式策略交集"), get_strat_label("S", "趨勢轉折延伸"), "**T. 自訂策略交集型**\n`AVG: 動態計算`"], label_visibility="collapsed")
        run_multi = st.button("啟動AI量化篩選", key="btn_multi", use_container_width=True)

    if (run_fund or run_chip or run_tech or run_multi):
        p_placeholder = st.empty()
        p_placeholder.markdown('<div class="scanner-ritual-wrapper">Quantum Processing...</div>', unsafe_allow_html=True)
        time.sleep(1)
        # Simplified execution logic
        strat_map = {"btn_fund": strat_fund, "btn_chip": strat_chip, "btn_tech": strat_tech, "btn_multi": strat_multi}
        choice = None
        for k, v in strat_map.items():
            if locals().get(k.replace("btn_", "run_")): choice = v; break
        active_key = choice.replace("**", "").strip()[0]
        try:
            df = fetch_and_rename(f"strategy_{active_key.lower()}_result.csv")
            if not df.empty:
                st.session_state.update({'temp_df': df, 'selected_strategy': active_key, 'scan_completed': True}); st.rerun()
            else: st.error("No target found.")
        except Exception as e: st.error(f"Error: {e}")
        p_placeholder.empty()

else:
    df, active_key = st.session_state['temp_df'], st.session_state['selected_strategy']
    st.button("重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}), use_container_width=True)
    
    name_map = {"A": "營收趨勢增長", "H": "財報三率三升", "I": "營收財報雙能", "M": "營收創高精選", "O": "合約負債爆發", "D": "法人籌碼吃貨", "E": "市場區間共振", "F": "左側超跌優質", "L": "股本法人鎖碼", "N": "股本投信鎖碼", "B": "股價強勢動能", "G": "中長周期轉折", "J": "指標強勢共振", "K": "跨週期多矩陣", "R": "複式策略交集", "S": "趨勢轉折延伸", "C": "營收股價雙能", "T": "自訂策略交集"}
    st.markdown(f'<div class="strategy-header-container"><h3 class="strategy-title">STRATEGY {active_key}. {name_map.get(active_key, "")}</h3><div style="font-family: Inter; font-size: 1.2rem; color: #ffffff;">觸發標的：{len(df)} 檔</div></div>', unsafe_allow_html=True)
    
    with st.expander("量子篩選結果數據", expanded=True):
        if '現價' in df.columns and '轉折值' in df.columns:
            try:
                p = pd.to_numeric(df['現價'], errors='coerce')
                v = pd.to_numeric(df['轉折值'], errors='coerce')
                df['轉折乖離(%)'] = ((p - v) / v.replace(0, pd.NA) * 100).fillna(0).round(2)
            except: pass
        
        cols = ["代號", "名稱", "產業", "現價", "漲幅(%)", "季乖離(%)", "20日法人買賣超(張)", "轉折值", "轉折乖離(%)"]
        disp_df = df[[c for c in cols if c in df.columns]].copy()
        if "代號" in disp_df.columns: disp_df = disp_df.set_index("代號")
            
        st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
        st.dataframe(disp_df.style.apply(highlight_pivot_full_row, axis=1).format("{:.2f}", na_rep="-"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    render_search_radar(location="bottom")
    st.markdown('<div class="disclaimer-wrapper"><h4 style="color:white; margin:0 0 10px 0;">免責聲明</h4><div style="color:#94a3b8; font-size:0.9rem;">本系統僅供研究參考，不構成投資建議.</div></div>', unsafe_allow_html=True)

st.markdown('<div class="footer-wrapper"><div style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase;">QUANTUM DATA SYSTEM © 2026</div></div>', unsafe_allow_html=True)
