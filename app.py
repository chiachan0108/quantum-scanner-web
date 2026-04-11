import streamlit as st
import pandas as pd
import datetime
import os
import time
import streamlit.components.v1 as components

GITHUB_USER, GITHUB_REPO = "chiachan0108", "stock-data"
st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# =============================================================================
# [CSS 樣式核心] - 絕對置中、徹底拔除原生點點、完美發光、還原 Footer
# =============================================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap'); 
html, body, [class*="css"], .stApp, [data-testid="stHeader"], [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { 
    font-family: 'Inter', 'Noto Sans TC', sans-serif !important; 
    background-color: #0b0f19 !important; 
    color: #e2e8f0 !important; 
    -webkit-font-smoothing: antialiased; 
    overscroll-behavior-y: none; 
} 
::-webkit-scrollbar { width: 6px; height: 6px; } 
::-webkit-scrollbar-track { background: rgba(11, 15, 25, 0.9); } 
::-webkit-scrollbar-thumb { background: rgba(0, 242, 255, 0.3); border-radius: 10px; } 
::-webkit-scrollbar-thumb:hover { background: rgba(0, 242, 255, 0.6); } 
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu { visibility: hidden !important; display: none !important; } 
@keyframes fadeSlideUp { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } } 
.fade-in-container { animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; } 
.pulse-dot-small { width: 8px; height: 8px; background-color: #00f2ff; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 0 rgba(0, 242, 255, 0.4); animation: breathing 2.5s infinite; flex-shrink: 0; } 
@keyframes breathing { 0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.6); } 70% { box-shadow: 0 0 0 8px rgba(0, 242, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); } } 
.header-group { margin-top: -45px; margin-bottom: 5px; animation: fadeSlideUp 0.4s ease-out forwards; } 
.main-title { font-family: 'JetBrains Mono', monospace !important; font-weight: 700; letter-spacing: -2px; background: linear-gradient(90deg, #00f2ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(2.0rem, 6vw, 3.5rem); line-height: 1.1; margin: 0; } 
.status-pill { display: inline-flex; align-items: center; white-space: nowrap; background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); padding: 6px 16px; border-radius: 50px; font-size: 0.8rem; color: rgba(148, 163, 184, 0.9); margin-bottom: 20px; font-weight: 500; letter-spacing: 0.5px; } 
.status-val { color: #ffffff; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-left: 6px; } 
.section-header-container { margin-top: 25px; margin-bottom: 16px; display: flex; align-items: center; position: relative; animation: fadeSlideUp 0.5s ease-out forwards; } 
.section-accent { width: 4px; height: 34px; background: linear-gradient(180deg, #00f2ff, #0072ff); border-radius: 4px; margin-right: 14px; box-shadow: 0 0 12px rgba(0, 242, 255, 0.4); } 
.section-header-text { display: flex; flex-direction: column; justify-content: center; } 
.section-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: rgba(0, 242, 255, 0.9); letter-spacing: 2px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; line-height: 1; } 
.section-label-zh { font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: 1.5px; line-height: 1; } 
.section-line { flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 242, 255, 0.2), transparent); margin-left: 20px; } 
.stButton > button { background: rgba(0, 242, 255, 0.08) !important; color: #ffffff !important; border: 1px solid rgba(0, 242, 255, 0.4) !important; backdrop-filter: blur(8px) !important; border-radius: 10px !important; font-weight: 900 !important; text-shadow: -0.5px -0.5px 0 #000, 0.5px -0.5px 0 #000, -0.5px 0.5px 0 #000, 0.5px 0.5px 0 #000 !important; letter-spacing: 2px; width: 100% !important; min-height: 62px !important; font-size: 1.25rem !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; position: relative; padding: 0 !important; } 
.stButton > button:hover { background: rgba(0, 242, 255, 0.15) !important; border: 1px solid rgba(0, 242, 255, 0.8) !important; box-shadow: 0 0 25px rgba(0, 242, 255, 0.35) !important; transform: translateY(-2px) !important; } 

/* 🌟 核心修復區：策略選項 Radio Buttons (極致版) */
[data-testid="stRadio"] > div[role="radiogroup"] {
    display: grid !important; 
    grid-template-columns: 1fr !important; /* 確保所有選項 100% 填滿等寬 */
    gap: 12px !important; 
    width: 100% !important;
}

/* 🚨 終極核彈級隱藏：針對所有可能產生圓點的 DOM 節點進行毀滅性打擊 */
[data-testid="stRadio"] div[role="radiogroup"] input[type="radio"],
[data-testid="stRadio"] div[role="radiogroup"] div[data-baseweb="radio"] > div:first-child,
[data-testid="stRadio"] div[role="radiogroup"] div[role="radio"] > div:first-child,
[data-testid="stRadio"] div[role="radiogroup"] div[data-baseweb="radio"] svg,
[data-testid="stRadio"] div[role="radiogroup"] label::before,
[data-testid="stRadio"] div[role="radiogroup"] label::after {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    content: none !important;
}

/* 選項卡片本體：絕對置中對齊，留白相等 */
[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #0b0f19 !important; 
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important; 
    padding: 16px 12px !important; 
    margin: 0 !important;
    cursor: pointer !important; 
    transition: all 0.3s ease !important;
    display: flex !important; 
    flex-direction: column !important; /* 內部元素垂直排列 */
    align-items: center !important; /* 水平置中 */
    justify-content: center !important; /* 垂直置中 */
    box-sizing: border-box !important;
    width: 100% !important;
    text-align: center !important;
    min-height: 85px !important;
}

[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    border-color: rgba(0, 242, 255, 0.4) !important;
    background-color: rgba(0, 242, 255, 0.02) !important;
}

/* 🎯 選取時的終極發光質感 (不靠點點，純靠整個區塊發光) */
[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked),
[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
    border: 1px solid #00f2ff !important; 
    background-color: rgba(0, 242, 255, 0.08) !important;
    box-shadow: 0 0 15px rgba(0, 242, 255, 0.25), inset 0 0 10px rgba(0, 242, 255, 0.1) !important; 
}

/* 文字區域設定 */
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
    width: 100% !important; 
    display: flex !important; 
    flex-direction: column !important; 
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p {
    margin: 0 !important;
    font-family: 'JetBrains Mono', 'Noto Sans TC', monospace !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #e2e8f0 !important;
    text-align: center !important;
    line-height: 1.6 !important; /* 確保上下行間距好看 */
}

/* 選取時，文字變成亮藍色發光 */
[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked) div[data-testid="stMarkdownContainer"] > p,
[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] > p {
    color: #00f2ff !important;
    font-weight: 800 !important;
    text-shadow: 0 0 8px rgba(0, 242, 255, 0.5) !important;
}

/* 讓 Streamlit 原生的顏色標籤稍微小一點，像個副標題 */
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p span {
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
}

/* 🔥 全域戰情雷達儀表板 CSS */
.global-radar-wrapper { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; animation: fadeSlideUp 0.6s ease-out forwards; } .radar-card { background: linear-gradient(135deg, rgba(22, 27, 34, 0.8) 0%, rgba(11, 15, 25, 0.9) 100%); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; position: relative; overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); } .radar-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #00f2ff, transparent); } .radar-title { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase; } .radar-data-row { display: flex; align-items: baseline; justify-content: space-between; } .radar-count { font-size: 1.8rem; font-weight: 900; color: #ffffff; font-family: 'Inter', sans-serif; line-height: 1; } .radar-count-unit { font-size: 0.8rem; color: rgba(255,255,255,0.5); font-weight: 600; margin-left: 4px; } .radar-perf { font-size: 1rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; } .perf-up { color: #ff3333; text-shadow: 0 0 5px rgba(255, 51, 51, 0.3); } .perf-down { color: #00ff33; text-shadow: 0 0 5px rgba(0, 255, 51, 0.3); } .perf-zero { color: #94a3b8; } @media (max-width: 1024px) { .global-radar-wrapper { grid-template-columns: repeat(2, 1fr); } } @media (max-width: 640px) { .global-radar-wrapper { grid-template-columns: 1fr; } }

/* 🔥 策略說明卡片與其他工具 CSS 保留 */
.logic-grid { display: grid; gap: 16px; grid-template-columns: repeat(4, 1fr); margin-bottom: 25px; margin-top: 10px; } @media (max-width: 1024px) { .logic-grid { grid-template-columns: repeat(2, 1fr); } } @media (max-width: 640px) { .logic-grid { grid-template-columns: 1fr; } } .logic-item { background: linear-gradient(145deg, rgba(22, 27, 34, 0.9) 0%, rgba(11, 15, 25, 0.95) 100%); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 12px; padding: 20px 16px; display: flex; flex-direction: column; position: relative; box-shadow: inset 0 0 15px rgba(0, 242, 255, 0.02), 0 4px 12px rgba(0, 0, 0, 0.2); } .logic-header { display: flex; flex-direction: column; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); } .logic-tag-row { display: flex; align-items: center; margin-bottom: 4px; } .logic-index-tag { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 700; color: rgba(0, 242, 255, 0.8); border: 1px solid rgba(0, 242, 255, 0.3); padding: 1px 6px; border-radius: 3px; margin-right: 10px; background: rgba(0, 242, 255, 0.05); } .logic-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: rgba(148, 163, 184, 0.7); letter-spacing: 1.2px; text-transform: uppercase; } .logic-label-zh { font-size: 1.1rem; font-weight: 700; color: #ffffff; line-height: 1.2; margin-top: 2px; } .logic-desc { font-size: 0.95rem; color: #94a3b8; line-height: 1.65; font-weight: 400; flex-grow: 1; } .highlight { color: #00f2ff !important; font-weight: 800 !important; text-shadow: 0 0 8px rgba(0, 242, 255, 0.4); }
[data-testid="stDataFrame"] { border: 1px solid rgba(0, 242, 255, 0.25) !important; border-radius: 12px !important; padding: 4px !important; background-color: #0b0f19 !important; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4); } [data-testid="stDataFrame"] th { background-color: #161b2a !important; color: #94a3b8 !important; border-bottom: 1px solid rgba(0, 242, 255, 0.2) !important; font-weight: 700 !important; } [data-testid="stDataFrame"] td { background-color: #0b0f19 !important; color: #ffffff !important; } .search-box-glass { background: linear-gradient(135deg, rgba(11, 15, 25, 0.95) 0%, rgba(22, 27, 34, 0.85) 100%); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 16px; padding: 24px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); backdrop-filter: blur(12px); animation: fadeSlideUp 0.5s ease-out forwards; } .strat-badge-premium { background: linear-gradient(90deg, rgba(22, 27, 34, 0.9), rgba(11, 15, 25, 0.9)); border: 1px solid rgba(0, 242, 255, 0.3); border-left: 3px solid #00f2ff; padding: 8px 14px; border-radius: 6px; color: #e2e8f0; font-weight: 600; font-size: 0.9rem; display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
[data-testid="stTabs"] { background-color: transparent !important; } [data-testid="stTabs"] button { background-color: rgba(11, 15, 25, 0.4) !important; border: 1px solid rgba(0, 242, 255, 0.1) !important; border-radius: 8px 8px 0 0 !important; color: #94a3b8 !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 700 !important; font-size: 1.1rem !important; padding: 12px 20px !important; transition: all 0.3s ease !important; } [data-testid="stTabs"] button[aria-selected="true"] { background: linear-gradient(180deg, rgba(0, 242, 255, 0.15) 0%, rgba(11, 15, 25, 0) 100%) !important; border-color: #00f2ff !important; color: #00f2ff !important; } [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: #00f2ff !important; }
[data-testid="stCheckbox"] { padding: 10px 14px !important; border: 1px solid rgba(255, 255, 255, 0.08) !important; border-radius: 8px !important; background-color: #0b0f19 !important; transition: all 0.3s ease !important; margin-bottom: 8px !important; display: flex !important; align-items: center !important; width: 100% !important; } [data-testid="stCheckbox"]:hover { border-color: rgba(0, 242, 255, 0.4) !important; } [data-testid="stCheckbox"]:has(input[type="checkbox"]:checked) { border: 1px solid #00f2ff !important; background-color: #0b0f19 !important; box-shadow: 0 0 15px rgba(0, 242, 255, 0.2), inset 0 0 8px rgba(0, 242, 255, 0.1) !important; } [data-testid="stCheckbox"] div[data-testid="stMarkdownContainer"] > p { color: #94a3b8 !important; font-weight: 600 !important; margin: 0 !important; } [data-testid="stCheckbox"]:has(input[type="checkbox"]:checked) div[data-testid="stMarkdownContainer"] > p { color: #00f2ff !important; font-weight: 800 !important; text-shadow: 0 0 8px rgba(0, 242, 255, 0.4) !important; }

/* 🌟 Footer 與版權宣告 CSS (完美還原) */
.disclaimer-wrapper { background-color: #0e121a; border: 1px solid rgba(0, 242, 255, 0.2) !important; border-radius: 8px; padding: 16px 16px 10px 16px !important; margin-top: 35px !important; margin-bottom: 35px !important; display: flex; flex-direction: column; gap: 10px !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); animation: fadeSlideUp 0.8s ease-out forwards; } .disclaimer-header { display: flex; align-items: center; margin-bottom: 0px !important; } .disclaimer-title { font-weight: 700; color: #ffffff; font-size: 14px !important; letter-spacing: 0.5px; margin: 0 !important; padding: 0 !important; line-height: 1 !important; display: flex; align-items: center; } .disclaimer-list { display: flex; flex-direction: column; gap: 6px !important; list-style: none; padding: 0 !important; padding-left: 18px !important; margin: 0 !important; } .disclaimer-item { font-size: 13px !important; color: #94a3b8; line-height: 1.4 !important; font-weight: 400; margin: 0 !important; text-align: justify !important; text-justify: inter-ideograph !important; } .footer-wrapper { margin-top: 60px; padding: 30px 10px 50px 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; justify-content: center !important; } .brand-copyright { color: #94a3b8; font-weight: 800 !important; font-size: 0.85rem !important; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; } .design-container { display: flex; align-items: center; justify-content: center; gap: 15px; flex-wrap: wrap; } .design-tag { background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; padding: 3px 8px 2px 8px; border-radius: 4px; text-transform: uppercase; display: inline-flex; align-items: center; justify-content: center; line-height: 1; height: 20px; box-sizing: border-box; } .design-email-tech { font-family: 'JetBrains Mono', monospace !important; color: #ffffff !important; font-size: 0.65rem !important; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; opacity: 0.9; display: inline-flex; align-items: center; height: 20px; } @media (max-width: 768px) { .design-container { flex-direction: column; gap: 10px; } }
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
    
    df_c = pd.DataFrame()
    if not df_dict['A'].empty and not df_dict['B'].empty:
        df_c = df_dict['A'][df_dict['A']['代號'].isin(set(df_dict['A']['代號']).intersection(set(df_dict['B']['代號'])))]
    perf['C'] = _calc(df_c)
    
    df_i = pd.DataFrame()
    if not df_dict['A'].empty and not df_dict['H'].empty:
        df_i = df_dict['A'][df_dict['A']['代號'].isin(set(df_dict['A']['代號']).intersection(set(df_dict['H']['代號'])))]
    perf['I'] = _calc(df_i)
    
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

# 🌟 新增：最安全、完美符合台股配色的換行文字產生器
def get_strat_label(key, base_name):
    data = strategy_perf.get(key, {"count": 0, "avg": None})
    val = data["avg"]
    
    # 雙空白加 \n 是 Streamlit Markdown 強制換行的標準語法
    if val is not None:
        sign = "+" if val > 0 else ""
        if val > 0:
            return f"{key}. {base_name}  \n:red[AVG: {sign}{val:.2f}%]"
        elif val < 0:
            return f"{key}. {base_name}  \n:green[AVG: {sign}{val:.2f}%]"
        else:
            return f"{key}. {base_name}  \n:gray[AVG: {sign}{val:.2f}%]"
            
    return f"{key}. {base_name}  \n:gray[AVG: --]"

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
        st.markdown(f'''<div style="background: linear-gradient(135deg, rgba(22, 27, 34, 0.8), rgba(11, 15, 25, 0.9)); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 12px; padding: 16px; margin-bottom: 15px; position: relative; overflow: hidden;"><div style="content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #00f2ff, transparent);"></div><div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #94a3b8; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase;">STRATEGY {k} · {name_map.get(k, k)}</div><div style="display: flex; align-items: baseline; justify-content: space-between;"><div><span style="font-size: 1.8rem; font-weight: 900; color: #ffffff; font-family: 'Inter', sans-serif;">{data['count']}</span><span style="font-size: 0.8rem; color: rgba(255,255,255,0.5); font-weight: 600; margin-left: 4px;">檔</span></div><div class="{perf_cls}" style="font-size: 1rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; {'color: #ff3333;' if avg is not None and avg > 0 else 'color: #00ff33;' if avg is not None and avg < 0 else 'color: #94a3b8;'}">{avg_str}</div></div></div>''', unsafe_allow_html=True)

# 🌟 獨立的個股反查雷達模組
def render_search_radar(location="top"):
    unique_key = f"search_form_{location}_{int(time.time()*100)}"
    with st.expander("◈ 個股反查雷達 (輸入代號或名稱)", expanded=False):
        with st.form(key=unique_key):
            col1, col2 = st.columns([3, 1])
            with col1:
                search_query = st.text_input("輸入股票代號或名稱：", key=f"input_{location}", label_visibility="collapsed").strip()
            with col2:
                submit_search = st.form_submit_button("🔍 啟動反查", use_container_width=True)
                
        if submit_search and search_query:
            try:
                s_a, s_b, s_d, s_e, s_f, s_g, s_h, s_j, s_k, s_l, s_m, s_n, s_o = map(fetch_and_rename, [
                    "strategy_a_result.csv", "strategy_b_result.csv", "strategy_d_result.csv", 
                    "strategy_e_result.csv", "strategy_f_result.csv", "strategy_g_result.csv", 
                    "strategy_h_result.csv", "strategy_j_result.csv", "strategy_k_result.csv",
                    "strategy_l_result.csv", "strategy_m_result.csv", "strategy_n_result.csv",
                    "strategy_o_result.csv"
                ])
                
                hit_strategies = []
                match_info = {"id": "", "name": "", "price": 0.0, "pivot": 0.0}

                def check_hit(df, strat_name):
                    if not df.empty and '代號' in df.columns and '名稱' in df.columns:
                        df['代號_str'] = df['代號'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                        mask = (df['代號_str'] == search_query) | (df['名稱'].astype(str).str.contains(search_query, na=False))
                        hits = df[mask]
                        if not hits.empty:
                            match_info["id"] = str(hits.iloc[0]['代號_str'])
                            match_info["name"] = str(hits.iloc[0]['名稱']).strip()
                            if "現價" in hits.columns and "轉折值" in hits.columns:
                                try:
                                    match_info["price"] = float(hits.iloc[0]['現價'])
                                    match_info["pivot"] = float(hits.iloc[0]['轉折值'])
                                except: pass
                            hit_strategies.append(strat_name)

                check_hit(s_a, "A. 營收趨勢增長型")
                check_hit(s_b, "B. 股價強勢動能型")
                check_hit(s_d, "D. 法人籌碼吃貨型")
                check_hit(s_e, "E. 市場區間共振型")
                check_hit(s_f, "F. 左側超跌優質型")
                check_hit(s_g, "G. 中長周期轉折型")
                check_hit(s_h, "H. 財報三率三升型")
                check_hit(s_j, "J. 指標強勢共振型")
                check_hit(s_k, "K. 跨週期多矩陣型")
                check_hit(s_l, "L. 股本法人鎖碼型")
                check_hit(s_m, "M. 營收創高精選型")
                check_hit(s_n, "N. 股本投信鎖碼型") 
                check_hit(s_o, "O. 合約負債爆發型")
                
                if "A. 營收趨勢增長型" in hit_strategies and "B. 股價強勢動能型" in hit_strategies:
                    hit_strategies.append("C. 營收股價雙能型")
                if "A. 營收趨勢增長型" in hit_strategies and "H. 財報三率三升型" in hit_strategies:
                    hit_strategies.append("I. 營收財報雙能型")
                    
                if hit_strategies and match_info["price"] > match_info["pivot"] and match_info["pivot"] > 0:
                    hit_strategies.append("S. 趨勢轉折延伸型")
                    
                base_strats = {"A. 營收趨勢增長型", "B. 股價強勢動能型", "D. 法人籌碼吃貨型", "E. 市場區間共振型", "F. 左側超跌優質型", "G. 中長周期轉折型", "H. 財報三率三升型", "J. 指標強勢共振型", "K. 跨週期多矩陣型", "L. 股本法人鎖碼型", "M. 營收創高精選型", "N. 股本投信鎖碼型", "O. 合約負債爆發型", "S. 趨勢轉折延伸型"}
                if len([s for s in hit_strategies if s in base_strats]) >= 4:
                    hit_strategies.append("R. 複式策略交集型")
                    
                hit_strategies.sort()

                if hit_strategies:
                    badge_html = "".join([f"<div class='strat-badge-premium'><span>{s.split('.')[0]}.</span>{s.split('.')[1].strip()}</div>" for s in hit_strategies])
                    result_html = f"""<div class="search-box-glass"><div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px dashed rgba(0, 242, 255, 0.2); padding-bottom: 16px; margin-bottom: 16px;"><div style="font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 900; color: #ffffff;">{match_info['id']} <span style="font-size: 1.2rem; color: #e2e8f0; font-weight: 800; letter-spacing: 2px;">{match_info['name']}</span></div><div style="background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.4); padding: 4px 10px; border-radius: 4px; color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 800;">MATCHED</div></div><div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 12px;">標的當前符合：</div><div style="display: flex; flex-wrap: wrap; gap: 10px;">{badges}</div></div>"""
                    st.markdown(result_html, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="empty-state-glass">Target Not Found or Input Error</div>', unsafe_allow_html=True)
            except Exception as e: st.error(str(e))

render_search_radar(location="top")

# 🌟 定義所有策略的邏輯說明文字
logic_dict = {
    "A": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">鎖定台灣<span class="highlight">全體上市櫃普通股</span>標的。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日的日均量必須大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">LEVEL</span></div><div class="logic-label-zh">技術位階</div></div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">TREND</span></div><div class="logic-label-zh">趨勢排列</div></div><div class="logic-desc"><span class="highlight">MA60 大於 MA240</span>，呈現多頭排列走勢。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">05</span><span class="logic-label-en">SCALE</span></div><div class="logic-label-zh">營收規模</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下公司有史以來<span class="highlight">同期新高</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">06</span><span class="logic-label-en">MOMENTUM</span></div><div class="logic-label-zh">雙巔峰動能</div></div><div class="logic-desc">單月營收歷史<span class="highlight">新高與次高</span>必須同時在近6、12個月內。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">07</span><span class="logic-label-en">DYNAMICS</span></div><div class="logic-label-zh">雙重成長</div></div><div class="logic-desc">確保近1季 <span class="highlight">YoY 正成長</span>且今年營收YoY(%)<span class="highlight">大於10%</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">08</span><span class="logic-label-en">TRACKING</span></div><div class="logic-label-zh">法人佈局位階</div></div><div class="logic-desc">追蹤近20日<span class="highlight">三大法人</span>買賣超張數及<span class="highlight">股價乖離率</span>。</div></div></div>',
    "H": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">四重防線</div></div><div class="logic-desc">近 20日均量皆大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">MOMENTUM</span></div><div class="logic-label-zh">營收爆發</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) <span class="highlight">強勢超越去年同期</span>，展現強勁動能。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">PROFITABILITY</span></div><div class="logic-label-zh">三率齊揚</div></div><div class="logic-desc">連續 <span class="highlight">2 季</span> 毛利率、營利率、淨利率皆同步上升，公司整體質量逐步優化。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SAFETY</span></div><div class="logic-label-zh">獲利底線</div></div><div class="logic-desc">最新一季稅後淨利必須<span class="highlight">大於 0</span>，堅決拒絕虛假轉機股。</div></div></div>',
    "I": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">INTERSECTION</span></div><div class="logic-label-zh">基本面雙引擎</div></div><div class="logic-desc">抓出同時具備<span class="highlight">營收創高增長 (策略A)</span>與<span class="highlight">財報三率三升 (策略H)</span>的頂級績優標的。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">REVENUE</span></div><div class="logic-label-zh">營收規模</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下同期新高，且今年營收YoY(%)<span class="highlight">大於10%</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">PROFITABILITY</span></div><div class="logic-label-zh">三率齊揚</div></div><div class="logic-desc">連續 <span class="highlight">2 季</span> 毛利率、營利率、淨利率皆同步上升，質量大幅優化。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SAFETY</span></div><div class="logic-label-zh">獲利底線</div></div><div class="logic-desc">最新一季稅後淨利必須<span class="highlight">大於 0</span>，堅決拒絕虛假轉機股。</div></div></div>',
    "M": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">鎖定台灣<span class="highlight">全體上市櫃普通股</span>標的。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近 20日均量皆大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">HISTORY</span></div><div class="logic-label-zh">歷史基期</div></div><div class="logic-desc">具備至少 <span class="highlight">24 個月</span>營收數據，避免新股短期失真。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">HIGH-WATER</span></div><div class="logic-label-zh">動態創高</div></div><div class="logic-desc">近一年單月營收打破歷史紀錄達 <span class="highlight">5 次以上</span>，確認爆發動能。</div></div></div>',
    "O": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">EXPLOSION</span></div><div class="logic-label-zh">大單湧入</div></div><div class="logic-desc">最新一季<span class="highlight">合約負債(預收工程/訂單款)</span>相較去年同期，必須展現出 YoY <span class="highlight">大於 50%</span> 的驚人爆發力。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">MOMENTUM</span></div><div class="logic-label-zh">季增動能</div></div><div class="logic-desc">最新季度的合約負債必須大於上一季，呈現<span class="highlight">無可反駁的成長趨勢</span>，過濾掉正在衰退的個股。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">SAFETY</span></div><div class="logic-label-zh">獲利護城河</div></div><div class="logic-desc">除了訂單滿載，公司最新一季 EPS 必須<span class="highlight">大於 0</span>，確保有實質獲利能力，拒絕賠錢接單。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SCALE</span></div><div class="logic-label-zh">訂單規模</div></div><div class="logic-desc">最新一季合約負債總額必須佔公司總股本 <span class="highlight">5% 以上</span>，確保訂單對營收具備實質且龐大的影響力。</div></div></div>',
    "D": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">四重防線</div></div><div class="logic-desc">近 20日均量大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">WHALE CHIP</span></div><div class="logic-label-zh">巨鯨級籌碼</div></div><div class="logic-desc">法人近 60 日淨買超必須<span class="highlight">大於 10,000 張</span>，確保重金護盤。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">CONTINUITY</span></div><div class="logic-label-zh">買盤延續</div></div><div class="logic-desc">近 20 日與近 5 日的法人動向皆維持<span class="highlight">正向淨買超</span>，無短期反手倒貨。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">STEP ACCUM</span></div><div class="logic-label-zh">階梯創高吃貨</div></div><div class="logic-desc">買超張數 <span class="highlight">60日>20日>5日</span>，且法人近5日總持股創<span class="highlight">近 60 日新高</span>。</div></div></div>',
    "E": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日平均日成交量需大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">VOL SPIKE</span></div><div class="logic-label-zh">異常攻擊表態</div></div><div class="logic-desc">近1個月內至少有兩天以上成交量大於季均量 <span class="highlight">3 倍</span>，確認市場籌碼大量換手。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">RESONANCE</span></div><div class="logic-label-zh">籌碼極致共振</div></div><div class="logic-desc">季度市場加權成本價 (AVWAP)，與成交區間重心價 (POC) 差距在 <span class="highlight">3% 以內</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PULLBACK</span></div><div class="logic-label-zh">量縮沉澱買點</div></div><div class="logic-desc">現價與市場加權成本價 (AVWAP) 差距在 <span class="highlight">3% 內</span>，且今日成交量<span class="highlight">小於近 5 日均量</span>。</div></div></div>',
    "F": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">OVERSOLD</span></div><div class="logic-label-zh">超跌位階</div></div><div class="logic-desc">現價為近半年最高點以來<span class="highlight">修正20%以上</span>，且近期股價低於月平均價<span class="highlight">10%以上</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">ACCUMULATE</span></div><div class="logic-label-zh">主力吸籌</div></div><div class="logic-desc">近10個交易日成交量<span class="highlight">明顯大於季均量</span>，確認市場籌碼進行大量換手。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">REVENUE</span></div><div class="logic-label-zh">營收巔峰</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下<span class="highlight">公司歷年以來同期新高</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">GROWTH</span></div><div class="logic-label-zh">今年成長</div></div><div class="logic-desc">今年累計營收年增率 (YTD YoY) <span class="highlight">維持正成長</span>。</div></div></div>',
    "L": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日平均日成交量需大於<span class="highlight">500張</span>，確保流動性無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">ACCUMULATE</span></div><div class="logic-label-zh">連續吃貨</div></div><div class="logic-desc">三大法人合計買超張數 <span class="highlight">20日 > 10日 > 5日 > 0</span>，呈現階梯式買盤。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">LOCK 10D</span></div><div class="logic-label-zh">短線鎖碼</div></div><div class="logic-desc">近 10 日三大法人買超總張數，大於發行總張數的 <span class="highlight">1%</span> 以上。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">LOCK 20D</span></div><div class="logic-label-zh">波段鎖碼</div></div><div class="logic-desc">近 20 日三大法人買超總張數，大於發行總張數的 <span class="highlight">2%</span> 以上。</div></div></div>',
    "N": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">ACCUMULATE</span></div><div class="logic-label-zh">階梯式連買</div></div><div class="logic-desc">單一投信買超呈現 <span class="highlight">20日 >= 10日 >= 5日 > 0</span> 的階梯式吃貨，確保買盤連貫無結帳。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LOCK 10D</span></div><div class="logic-label-zh">短期強力表態</div></div><div class="logic-desc">投信近 10 日淨買超張數，必須大於該公司總發行股本的 <span class="highlight">0.5%</span> 以上，捕捉初升段。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">LOCK 20D</span></div><div class="logic-label-zh">波段極限鎖碼</div></div><div class="logic-desc">投信近 20 日淨買超張數，必須大於該公司總發行股本的 <span class="highlight">1%</span> 以上，確認核心認養。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PURE CHIP</span></div><div class="logic-label-zh">純粹籌碼</div></div><div class="logic-desc">捨棄基本面營收枷鎖，專注捕捉投信無視業績、<span class="highlight">重金強勢鎖碼</span>的轉機爆發股。</div></div></div>',
    "B": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc"><span class="highlight">全體上市櫃公司普通公司</span>，排除 ETF、ETN、存託憑證及下市黑名單。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日的日均量必須大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">STRENGTH</span></div><div class="logic-label-zh">相對強勢動能</div></div><div class="logic-desc">股價短中長期皆強勢，<span class="highlight">近5日、20日與60日報酬</span>超越大盤同期績效。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PURE ACTION</span></div><div class="logic-label-zh">純粹價格行為</div></div><div class="logic-desc">專注市場最真實的資金反應，<span class="highlight">無須等待法人買超確認</span>，第一時間捕捉起漲動能。</div></div></div>',
    "G": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc"><span class="highlight">全體上市櫃公司普通公司</span>，排除 ETF、ETN、存託憑證及下市黑名單。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">四重防線</div></div><div class="logic-desc">近 20日均量必須大於<span class="highlight">500張</span>，確保流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">PIVOT W</span></div><div class="logic-label-zh">中期轉折</div></div><div class="logic-desc">現價必須強勢站上<span class="highlight">週線級別轉折值</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PIVOT M</span></div><div class="logic-label-zh">長期共振</div></div><div class="logic-desc">現價同步突破月線級別轉折值，<span class="highlight">高機率形成多頭起漲點</span>。</div></div></div>',
    "J": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">MACD(200)</span></div><div class="logic-label-zh">極長線趨勢</div></div><div class="logic-desc">使用極端參數 <span class="highlight">200,201,202</span>，且 DIF、D-M、EMA1、EMA2 皆大於前日。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">DMI(300)</span></div><div class="logic-label-zh">超長線動能</div></div><div class="logic-desc">DMI 參數設為 <span class="highlight">300</span>，且運算出的 ADX300 必須大於昨日。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">W%R(50)</span></div><div class="logic-label-zh">多頭慣性</div></div><div class="logic-desc">威廉指標參數設為 50，且指標值必須 <span class="highlight">小於 20</span> (接近高點區)。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">穩健流動性</div></div><div class="logic-desc">近 20日平均成交量皆大於 <span class="highlight">500 張</span>，確認流動性安全無虞。</div></div></div>',
    "K": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">DMI(1) M</span></div><div class="logic-label-zh">月線趨勢</div></div><div class="logic-desc">月線 DMI 參數為 1，且 +DI(1) 值必須 <span class="highlight">大於 50</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">RSI(4) M</span></div><div class="logic-label-zh">月線強度</div></div><div class="logic-desc">月線 RSI 參數為 4，且 RSI(4) 指標值必須 <span class="highlight">大於 77</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">W%R(50) D</span></div><div class="logic-label-zh">日線慣性</div></div><div class="logic-desc">日線威廉指標參數為 50，且指標值必須 <span class="highlight">小於 20</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">RSI(60) D</span></div><div class="logic-label-zh">長線保護</div></div><div class="logic-desc">日線 RSI 參數為 60，且 RSI(60) 指標值必須 <span class="highlight">大於 57</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">05</span><span class="logic-label-en">VR(2) W</span></div><div class="logic-label-zh">週線籌碼</div></div><div class="logic-desc">週線容量比率 VR 參數為 2，且指標值必須 <span class="highlight">大於 9998</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">06</span><span class="logic-label-en">VR(2) M</span></div><div class="logic-label-zh">月線籌碼</div></div><div class="logic-desc">月線容量比率 VR 參數為 2，且指標值必須 <span class="highlight">大於 9998</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">07</span><span class="logic-label-en">MATRIX</span></div><div class="logic-label-zh">矩陣過濾</div></div><div class="logic-desc">以上六大跨週期特徵，必須符合 <span class="highlight">4 個以上</span> 才可觸發入選。</div></div></div>',
    "C": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">INTERSECTION</span></div><div class="logic-label-zh">雙引擎交集</div></div><div class="logic-desc">抓出具備<span class="highlight">營收創高成長</span>與<span class="highlight">技術強勢動能</span>的交集標的。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">FUNDAMENTAL</span></div><div class="logic-label-zh">基本面護城河</div></div><div class="logic-desc">近1年累積營收創歷史<span class="highlight">同期新高</span>，且今年以來累積 YoY <span class="highlight">大於 10%</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">TECHNICAL</span></div><div class="logic-label-zh">技術面爆發</div></div><div class="logic-desc"><span class="highlight">短、中、長期報酬</span>全數超越大盤同期績效。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">TRACKING</span></div><div class="logic-label-zh">法人佈局位階</div></div><div class="logic-desc">追蹤近20日<span class="highlight">三大法人</span>買賣超張數及<span class="highlight">股價乖離率</span>。</div></div></div>',
    "R": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">INTERSECTION</span></div><div class="logic-label-zh">多維度交集</div></div><div class="logic-desc">統整基本面、技術面、籌碼面，尋找<span class="highlight">多重條件共振</span>的強勢標的。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">MATRIX</span></div><div class="logic-label-zh">矩陣濾網</div></div><div class="logic-desc">涵蓋策略 A, B, D, E, F, G, H, J, K, L, M, N, O, S，共 <span class="highlight">14 大核心策略</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">TRIGGER</span></div><div class="logic-label-zh">觸發條件</div></div><div class="logic-desc">單一標的必須同時符合上述 14 大策略中的 <span class="highlight">任意 4 項 (含) 以上</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">CONFIRMATION</span></div><div class="logic-label-zh">極致收斂</div></div><div class="logic-desc">透過多條件疊加，過濾掉單一指標的雜訊，抓出<span class="highlight">法人與主力高度共識</span>的標的。</div></div></div>',
    "S": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">統整 <span class="highlight">所有基礎策略</span> 篩選出的全體優質標的作為判斷樣本。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">TRIGGER</span></div><div class="logic-label-zh">轉折觸發</div></div><div class="logic-desc">鎖定 <span class="highlight">現價突破轉折值</span> 的標的，預判未來行情繼續延伸。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">FUNDAMENTAL</span></div><div class="logic-label-zh">營收動能</div></div><div class="logic-desc">追蹤 <span class="highlight">今年以來累積營收 YoY(%)</span>，確保基本面支撐。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SMART MONEY</span></div><div class="logic-label-zh">法人籌碼</div></div><div class="logic-desc">觀察近 20 日 <span class="highlight">法人買賣超動向</span>，確認機構資金流向。</div></div></div>',
    "T": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">自由選股邊界</div></div><div class="logic-desc">涵蓋全市場優質標的，由使用者自行定奪<span class="highlight">多重篩選邊界</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">CUSTOMIZE</span></div><div class="logic-label-zh">策略自由拼圖</div></div><div class="logic-desc">提供多達 15 項高階量化策略自由組合，打造您的<span class="highlight">專屬量化濾網</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">INTERSECTION</span></div><div class="logic-label-zh">嚴格絕對交集</div></div><div class="logic-desc">嚴格取所選策略的交集，確保標的必須<span class="highlight">同時滿足所有勾選條件</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">CONFIRMATION</span></div><div class="logic-label-zh">極致收斂過濾</div></div><div class="logic-desc">透過多維度條件疊加，強勢過濾單一指標雜訊，抓出<span class="highlight">終極共識飆股</span>。</div></div></div>'
}

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
            if st.session_state.get(k): choice = v; break
        active_key = choice.replace("**", "").strip()[0]
        try:
            df = fetch_and_rename(f"strategy_{active_key.lower()}_result.csv")
            if not df.empty:
                st.session_state.update({'temp_df': df, 'selected_strategy': active_key, 'scan_completed': True}); st.rerun()
            else: st.error("No target found.")
        except Exception as e: st.error(f"Error: {e}")
        p_placeholder.empty()
        
    # 🌟 確保策略說明圖卡只顯示選擇的項目 (絕對不會跑版)
    strat_map_display = {"基本面區": strat_fund, "籌碼面區": strat_chip, "技術面區": strat_tech, "多吻合區": strat_multi}
    # 這裡抓取目前頁面最活躍的變數，預設為A
    active_display_key = "A"
    try:
        active_display_key = strat_fund.replace("**", "").strip()[0]
    except: pass
    
    st.markdown("<div class='section-header-container' style='margin-top: 15px;'><div class='section-accent'></div><div class='section-header-text'><span class='section-label-en'>SYSTEM ARCHITECTURE</span><span class='section-label-zh'>策略核心邏輯</span></div><div class='section-line'></div></div>", unsafe_allow_html=True)
    st.markdown(logic_dict.get(active_display_key, ""), unsafe_allow_html=True)

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
        
        if active_key in ["M", "T"]:
             cols.insert(cols.index("20日法人買賣超(張)"), "近一年創高次數")
        if active_key in ["N", "T"]:
             if "20日法人買賣超(張)" in cols: cols.remove("20日法人買賣超(張)")
             cols.extend(["投信5日買超(張)", "投信10日買超(張)", "投信20日買超(張)"])
        if active_key in ["O", "T"]:
             cols.extend(["合約負債YoY(%)", "增額佔股本(%)", "總佔比(%)", "最新季EPS"])
             
        disp_df = df[[c for c in cols if c in df.columns]].copy()
        if "代號" in disp_df.columns: disp_df = disp_df.set_index("代號")
            
        st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
        # 安全格式化
        format_dict = {c: "{:.2f}" for c in disp_df.columns if any(x in c for x in ["現價", "乖離", "報酬", "YoY", "MoM", "轉折值", "漲幅", "股本比", "總佔比", "EPS"])}
        format_dict.update({c: "{:,.0f}" for c in disp_df.columns if any(x in c for x in ["法人", "買超", "張", "次數"])})
        st.dataframe(disp_df.style.apply(highlight_pivot_full_row, axis=1).format(format_dict, na_rep="-"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    render_search_radar(location="bottom")
    st.markdown('<div id="disclaimer-target" class="disclaimer-wrapper"><div class="disclaimer-header"><div class="pulse-dot-small"></div><h4 class="disclaimer-title">重要免責聲明</h4></div><ul class="disclaimer-list"><li class="disclaimer-item">1.系統篩選結果均為量化模型產出，僅供研究參考不構成投資建議.</li><li class="disclaimer-item">2.過往績效不保證未來表現，請做好自身風控本系統不負法律責任.</li></ul></div>', unsafe_allow_html=True)

st.markdown('<div class="footer-wrapper"><div class="brand-copyright">QUANTUM DATA SYSTEM © 2026</div><div class="design-container"><span class="design-tag">Developer / Design</span><span class="design-email-tech">WU.CHIACHAN@GMAIL.COM</span></div></div>', unsafe_allow_html=True)
