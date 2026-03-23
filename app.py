import streamlit as st
import pandas as pd
import datetime, io, time, requests, os
import streamlit.components.v1 as components

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap');
    
    html, body, [class*="css"], .stApp, [data-testid="stHeader"], [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { 
        font-family: 'Inter', 'Noto Sans TC', sans-serif !important; 
        background-color: #0b0f19 !important; color: #e2e8f0 !important;
        -webkit-font-smoothing: antialiased; overscroll-behavior-y: none;
    }

    /* 🚨 隱藏右上角 Streamlit 預設選單、Fork 按鈕與 GitHub 連結 */
    [data-testid="stHeader"] { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    [data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }
    #MainMenu { visibility: hidden !important; display: none !important; }

    .pulse-dot-small { width: 8px; height: 8px; background-color: #00f2ff; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 0 rgba(0, 242, 255, 0.4); animation: breathing 2.5s infinite; flex-shrink: 0; }
    @keyframes breathing { 0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.6); } 70% { box-shadow: 0 0 0 8px rgba(0, 242, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); } }

    .header-group { margin-top: -45px; margin-bottom: 5px; }
    .main-title { font-family: 'JetBrains Mono', monospace !important; font-weight: 700; letter-spacing: -2px; background: linear-gradient(90deg, #00f2ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(2.0rem, 6vw, 3.5rem); line-height: 1.1; margin: 0; }
    .status-pill { display: inline-flex; align-items: center; white-space: nowrap; background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); padding: 6px 16px; border-radius: 50px; font-size: 0.8rem; color: rgba(148, 163, 184, 0.9); margin-bottom: 20px; font-weight: 500; letter-spacing: 0.5px; }
    .status-val { color: #ffffff; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-left: 6px; }

    .section-header-container { margin-top: 25px; margin-bottom: 16px; display: flex; align-items: center; position: relative; }
    .section-accent { width: 4px; height: 34px; background: linear-gradient(180deg, #00f2ff, #0072ff); border-radius: 4px; margin-right: 14px; box-shadow: 0 0 12px rgba(0, 242, 255, 0.4); }
    .section-header-text { display: flex; flex-direction: column; justify-content: center; }
    .section-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: rgba(0, 242, 255, 0.9); letter-spacing: 2px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; line-height: 1; }
    .section-label-zh { font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: 1.5px; line-height: 1; }
    .section-line { flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 242, 255, 0.2), transparent); margin-left: 20px; }

    div[data-testid="stSelectbox"] label { display: none !important; }
    .stSelectbox [data-baseweb="select"] { 
        background-color: #161b2a !important; border: 1px solid rgba(0, 242, 255, 0.3) !important; 
        border-radius: 10px !important; min-height: 56px !important; 
    }
    .stSelectbox [data-baseweb="select"] > div:first-child { padding: 0px 35px 0px 18px !important; display: flex !important; align-items: center !important; height: 100% !important; min-height: 56px !important; }
    .stSelectbox [data-baseweb="select"] div { background-color: transparent !important; font-weight: 600 !important; color: #ffffff !important; font-size: clamp(1.0rem, 4.0vw, 1.15rem) !important; line-height: normal !important; margin: 0 !important; display: flex !important; align-items: center !important; }

    .stButton > button { 
        background: rgba(0, 242, 255, 0.08) !important; 
        color: #ffffff !important; border: 1px solid rgba(0, 242, 255, 0.4) !important; 
        backdrop-filter: blur(8px) !important; border-radius: 10px !important; 
        font-weight: 900 !important; 
        text-shadow: -0.5px -0.5px 0 #000, 0.5px -0.5px 0 #000, -0.5px 0.5px 0 #000, 0.5px 0.5px 0 #000 !important;
        letter-spacing: 2px; width: 100% !important; min-height: 62px !important; 
        font-size: 1.25rem !important; 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important; transition: all 0.4s ease !important; position: relative;
        padding: 0 !important; 
    }
    .stButton > button:hover { background: rgba(0, 242, 255, 0.15) !important; border: 1px solid rgba(0, 242, 255, 0.8) !important; box-shadow: 0 0 20px rgba(0, 242, 255, 0.3) !important; transform: translateY(-1px) !important; }

    .stButton > button div[data-testid="stMarkdownContainer"] {
        display: flex !important; align-items: center !important; justify-content: center !important;
        width: 100% !important; height: 100% !important; margin: 0 !important; padding: 0 !important;
    }
    .stButton > button div[data-testid="stMarkdownContainer"] p {
        display: flex !important; align-items: center !important; justify-content: center !important;
        margin: 0 !important; padding: 0 !important; line-height: 1 !important; transform: translate(-4px, 2px) !important;
    }
    .stButton > button div[data-testid="stMarkdownContainer"] p::before {
        content: ''; display: block !important; flex-shrink: 0 !important; width: 11px; height: 11px; background: rgba(0, 242, 255, 0.8); margin-right: 14px !important; transform: rotate(45deg); border: 0.5px solid #000; box-shadow: 4px -4px 0 rgba(0, 242, 255, 0.4); 
    }

    .logic-grid { display: grid; gap: 16px; grid-template-columns: 1fr; grid-auto-rows: 1fr; margin-bottom: 25px; }
    @media (min-width: 1024px) { .logic-grid { grid-template-columns: repeat(4, 1fr) !important; } }
    .logic-item { 
        background: linear-gradient(145deg, rgba(22, 27, 34, 0.9) 0%, rgba(11, 15, 25, 0.95) 100%); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 12px; padding: 20px 16px; transition: 0.3s; height: 100%; display: flex; flex-direction: column; position: relative; box-shadow: inset 0 0 15px rgba(0, 242, 255, 0.02), 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .logic-item::before { content: ''; position: absolute; top: 0; left: 15%; right: 15%; height: 1.5px; background: linear-gradient(90deg, transparent, rgba(0, 242, 255, 0.5), transparent); }
    .logic-item:hover { border-color: rgba(0, 242, 255, 0.4); transform: translateY(-2px); }
    .logic-header { display: flex; flex-direction: column; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
    .logic-tag-row { display: flex; align-items: center; margin-bottom: 4px; }
    .logic-index-tag { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 700; color: rgba(0, 242, 255, 0.8); border: 1px solid rgba(0, 242, 255, 0.3); padding: 1px 6px; border-radius: 3px; margin-right: 10px; background: rgba(0, 242, 255, 0.03); }
    .logic-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: rgba(148, 163, 184, 0.7); letter-spacing: 1.2px; text-transform: uppercase; }
    .logic-label-zh { font-size: 1.1rem; font-weight: 700; color: #ffffff; line-height: 1.2; margin-top: 2px; } 
    .logic-desc { font-size: 0.95rem; color: #94a3b8; line-height: 1.65; font-weight: 400; flex-grow: 1; }
    .highlight { color: #ffffff !important; font-weight: 600 !important; }

    .strategy-header-container { border-left: 4px solid #00f2ff; background: linear-gradient(90deg, rgba(0, 242, 255, 0.05) 0%, transparent 100%); padding: 16px 20px; margin-top: 25px; margin-bottom: 15px; border-radius: 0 8px 8px 0; display: flex; flex-direction: column; gap: 6px; }
    .status-tag-text { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #00f2ff; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }
    .strategy-title { font-size: clamp(1.2rem, 4.5vw, 1.6rem) !important; color: #ffffff; font-weight: 800; line-height: 1.4; margin: 0; white-space: normal !important; word-break: keep-all !important; }

    .summary-box-group { display: flex; flex-direction: column; gap: 12px; margin-bottom: 22px; align-items: flex-start; }
    .result-summary, .return-summary { display: flex; align-items: center; justify-content: center !important; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.35); padding: 0 12px; border-radius: 6px; margin-bottom: 0px !important; width: 220px; height: 52px; white-space: nowrap; box-sizing: border-box; }
    .result-text { font-weight: 800; font-size: 0.9rem; color: #00f2ff; letter-spacing: 0.5px; transform: translateY(1.5px); line-height: 1; }
    .result-num { font-family: 'Inter', sans-serif; font-size: 1.15rem; margin: 0 8px; color: #ffffff; font-weight: 700; transform: translateY(1.5px); line-height: 1; }
    .return-val-up { font-family: 'Inter', sans-serif; font-size: 1.15rem; margin-left: 10px; color: #ff3333; font-weight: 900; transform: translateY(1.5px); line-height: 1; }
    .return-val-down { font-family: 'Inter', sans-serif; font-size: 1.15rem; margin-left: 10px; color: #00ff33; font-weight: 900; transform: translateY(1.5px); line-height: 1; }
    .return-val-zero { font-family: 'Inter', sans-serif; font-size: 1.15rem; margin-left: 10px; color: #ffffff; font-weight: 700; transform: translateY(1.5px); line-height: 1; }

    .scanner-ritual-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center !important; background: radial-gradient(circle at center, rgba(11, 15, 25, 0.95), #0b0f19); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 12px; width: clamp(280px, 90%, 400px); min-height: 180px; margin: 20px auto !important; box-shadow: 0 0 30px rgba(0, 242, 255, 0.05); position: relative; overflow: hidden; padding: 25px; }
    .scanner-ritual-wrapper::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(0, 242, 255, 0.02) 0%, transparent 60%); animation: dataSyncFlow 5s linear infinite; }
    .quantum-ritual-core { position: relative; width: 60px; height: 60px; margin-bottom: 25px; display: flex; align-items: center; justify-content: center !important; }
    .core-diamond { position: absolute; width: 35px; height: 35px; background: rgba(0, 242, 255, 0.8); border: 0.5px solid #000; box-shadow: 4px -4px 0 rgba(0, 242, 255, 0.4); transform: rotate(45deg); animation: ritualDiamond 3s ease-in-out infinite; }
    .core-ring { position: absolute; width: 60px; height: 60px; border: 1.5px solid rgba(0, 242, 255, 0.2); border-radius: 50%; border-top-color: rgba(0, 242, 255, 0.8); border-bottom-color: rgba(0, 242, 255, 0.8); animation: ritualRing 3s linear infinite; }
    .core-ring::after { content: ''; position: absolute; width: 45px; height: 45px; border: 1.5px solid rgba(0, 242, 255, 0.1); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(0deg); border-right-color: rgba(0, 242, 255, 0.6); border-left-color: rgba(0, 242, 255, 0.6); animation: ritualRingInner 3s linear infinite; }
    .scanner-ritual-text-group { text-align: center; width: 100%; }
    .scanner-ritual-status { font-family: 'Inter', 'Noto Sans TC', sans-serif !important; font-weight: 800 !important; color: #ffffff !important; font-size: 1.05rem !important; letter-spacing: 1.5px !important; margin-bottom: 15px !important; line-height: 1.2 !important; text-shadow: -0.5px -0.5px 0 #000, 0.5px -0.5px 0 #000, -0.5px 0.5px 0 #000, 0.5px 0.5px 0 #000 !important; }
    
    .progress-bar-container { width: 80%; height: 6px; background-color: rgba(0, 242, 255, 0.1); border-radius: 10px; overflow: hidden; margin: 0 auto; position: relative; border: 1px solid rgba(0, 242, 255, 0.2); }
    .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #0072ff, #00f2ff); border-radius: 10px; box-shadow: 0 0 10px rgba(0, 242, 255, 0.8); width: 0%; transition: width 0.3s ease; }
    
    @keyframes ritualDiamond { 0%, 100% { transform: rotate(45deg) scale(1); opacity: 1; } 50% { transform: rotate(135deg) scale(1.1); opacity: 0.6; } }
    @keyframes ritualRing { 100% { transform: rotate(360deg); } }
    @keyframes ritualRingInner { 100% { transform: translate(-50%, -50%) rotate(-360deg); } }
    @keyframes dataSyncFlow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

    /* 確保原生表格順暢渲染 */
    [data-testid="stDataFrame"] { border: 1px solid rgba(0, 242, 255, 0.25) !important; border-radius: 12px !important; padding: 4px !important; background-color: #0b0f19 !important; }
    [data-testid="stDataFrame"] div[data-testid="stTable"] { background-color: #0b0f19 !important; }
    [data-testid="stDataFrame"] th { background-color: #161b2a !important; color: #94a3b8 !important; border-bottom: 1px solid rgba(0, 242, 255, 0.2) !important; }
    [data-testid="stDataFrame"] td { background-color: #0b0f19 !important; color: #ffffff !important; }

    .disclaimer-wrapper { background-color: #0e121a; border: 1px solid rgba(0, 242, 255, 0.3) !important; border-radius: 8px; padding: 16px 16px 10px 16px !important; margin-top: 25px !important; margin-bottom: 35px !important; display: flex; flex-direction: column; gap: 10px !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }
    .disclaimer-header { display: flex; align-items: center; margin-bottom: 0px !important; }
    .disclaimer-title { font-weight: 700; color: #ffffff; font-size: 14px !important; letter-spacing: 0.5px; margin: 0 !important; padding: 0 !important; line-height: 1 !important; display: flex; align-items: center; } 
    .disclaimer-list { display: flex; flex-direction: column; gap: 6px !important; list-style: none; padding: 0 !important; padding-left: 18px !important; margin: 0 !important; } 
    .disclaimer-item { font-size: 13px !important; color: #94a3b8; line-height: 1.4 !important; font-weight: 400; margin: 0 !important; text-align: justify !important; text-justify: inter-ideograph !important; } 

    .footer-wrapper { margin-top: 60px; padding: 30px 10px 50px 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; justify-content: center !important; }
    .brand-copyright { color: #94a3b8; font-weight: 800 !important; font-size: 0.85rem !important; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
    .design-container { display: flex; align-items: center; justify-content: center; gap: 15px; flex-wrap: wrap; }
    .design-tag { background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; padding: 3px 8px 2px 8px; border-radius: 4px; text-transform: uppercase; display: inline-flex; align-items: center; justify-content: center; line-height: 1; height: 20px; box-sizing: border-box; }
    .design-email-tech { font-family: 'JetBrains Mono', monospace !important; color: #ffffff !important; font-size: 0.65rem !important; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; opacity: 0.9; display: inline-flex; align-items: center; height: 20px; }
    @media (max-width: 768px) { .design-container { flex-direction: column; gap: 10px; } }
    </style>
""", unsafe_allow_html=True)

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

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False
now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
data_date = now_taipei.strftime('%Y/%m/%d') if now_taipei.hour >= 20 else (now_taipei - datetime.timedelta(days=1)).strftime('%Y/%m/%d')

st.markdown(f'''<div class="header-group"><h1 class="main-title">QUANTUM SCANNER</h1><div class="status-pill"><div class="pulse-dot-small"></div>LAST UPDATE : <span class="status-val">{data_date} 20:00</span></div></div>''', unsafe_allow_html=True)

if not st.session_state['scan_completed']:
    st.markdown("""
    <div class='section-header-container'>
        <div class='section-accent'></div>
        <div class='section-header-text'>
            <span class='section-label-en'>STRATEGY CONFIGURATION</span>
            <span class='section-label-zh'>策略類型選取</span>
        </div>
        <div class='section-line'></div>
    </div>
    """, unsafe_allow_html=True)
    
    strategy_choice = st.selectbox("量化策略模組", [
        "A. 營收趨勢增長型", 
        "B. 股價強勢動能型", 
        "C. 營收股價雙能型", 
        "D. 法人籌碼吃貨型", 
        "E. 季度倍量攻擊共振型", 
        "F. 股票轉折測試區"
    ], label_visibility="collapsed")
    
    st.markdown("""
    <div class='section-header-container'>
        <div class='section-accent'></div>
        <div class='section-header-text'>
            <span class='section-label-en'>SYSTEM ARCHITECTURE</span>
            <span class='section-label-zh'>策略核心邏輯</span>
        </div>
        <div class='section-line'></div>
    </div>
    """, unsafe_allow_html=True)
    
    if "A." in strategy_choice:
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">鎖定台灣 <span class="highlight">全體上市櫃普通股</span> 標的。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日平均 <span class="highlight">日成交量</span> 需大於 <span class="highlight">1,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">LEVEL</span></div><div class="logic-label-zh">技術位階</div></div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">TREND</span></div><div class="logic-label-zh">趨勢排列</div></div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現多頭排列走勢。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">05</span><span class="logic-label-en">SCALE</span></div><div class="logic-label-zh">營收規模</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下 <span class="highlight">歷年以來同期新高</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">06</span><span class="logic-label-en">MOMENTUM</span></div><div class="logic-label-zh">雙巔峰動能</div></div><div class="logic-desc">單月營收 <span class="highlight">歷史新高與次高</span> 必須同時在近6、12個月內。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">07</span><span class="logic-label-en">DYNAMICS</span></div><div class="logic-label-zh">雙重成長</div></div><div class="logic-desc">確保近1季 <span class="highlight">YoY 正成長</span> 且 <span class="highlight">今年營收YoY(%) > 20%</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">08</span><span class="logic-label-en">TRACKING</span></div><div class="logic-label-zh">法人佈局位階</div></div><div class="logic-desc">追蹤近 <span class="highlight">20 日三大法人</span> 買賣超張數及 <span class="highlight">股價乖離率</span>。</div></div>
        </div>
        """
    elif "B." in strategy_choice:
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc"><span class="highlight">全體上市櫃公司</span>，排除 ETF、ETN、存託憑證及下市黑名單。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">1,000張</span>，確保流動性安全無虞。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">STRENGTH</span></div><div class="logic-label-zh">相對強勢動能</div></div><div class="logic-desc">股價短中長期皆強勢，<span class="highlight">近20日、60日與240日報酬</span>超越大盤同期績效。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">CASHFLOW</span></div><div class="logic-label-zh">法人資金流</div></div><div class="logic-desc">近 5、20 個交易日三大法人合計皆呈現 <span class="highlight">淨買超狀態</span>，具備機構短、中期資金護航實力。</div></div>
        </div>
        """
    elif "C." in strategy_choice:
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">INTERSECTION</span></div><div class="logic-label-zh">雙引擎交集</div></div><div class="logic-desc">抓出具備 <span class="highlight">營收創高成長</span> 與 <span class="highlight">技術強勢動能</span> 的交集標的。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">FUNDAMENTAL</span></div><div class="logic-label-zh">基本面護城河</div></div><div class="logic-desc"><span class="highlight">近1年累積營收</span> 創歷史同期新高，且今年以來累積 YoY > 20%。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">TECHNICAL</span></div><div class="logic-label-zh">技術面爆發</div></div><div class="logic-desc"><span class="highlight">短、中、長期報酬</span>全數超越大盤同期績效。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SMART MONEY</span></div><div class="logic-label-zh">法人雙重認同</div></div><div class="logic-desc">確保近 <span class="highlight">5、20 日三大法人皆為淨買超</span>，具備機構短、中期資金護航實力。</div></div>
        </div>
        """
    elif "D." in strategy_choice:
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近20日均量 > 1,000張 且 <span class="highlight">近60日總量 > 60,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">SAFE ZONE</span></div><div class="logic-label-zh">防護起漲區</div></div><div class="logic-desc">現價與季線乖離 <span class="highlight">不超過 15%</span>，堅決不追高。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">WHALE CHIP</span></div><div class="logic-label-zh">巨鯨級籌碼</div></div><div class="logic-desc">法人近 60 日淨買超必須大於 <span class="highlight">10,000 張</span>，確保重金護盤。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">STEP ACCUM</span></div><div class="logic-label-zh">階梯創高吃貨</div></div><div class="logic-desc">買超張數 <span class="highlight">60日 > 20日 > 5日</span>，且<span class="highlight">法人總持股</span>創近 60 日新高。</div></div>
        </div>
        """
    elif "E." in strategy_choice:
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近60日平均日成交量需大於 <span class="highlight">500張</span>，過濾冷門股。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">VOL SPIKE</span></div><div class="logic-label-zh">倍量攻擊表態</div></div><div class="logic-desc">近20日內至少有一日成交量 <span class="highlight">大於季均量 2 倍</span>，確認主力進場。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">RESONANCE</span></div><div class="logic-label-zh">籌碼雙重共振</div></div><div class="logic-desc">季度大戶成本(AVWAP)與成交重心(POC)差距 <span class="highlight">≤ 5%</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PULLBACK</span></div><div class="logic-label-zh">量縮回踩買點</div></div><div class="logic-desc">現價與成本乖離 <span class="highlight">±5% 內</span>，且今日成交量小於 <span class="highlight">近5日均量</span>。</div></div>
        </div>
        """
    else:
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">統整 <span class="highlight">策略A、B、C、D、E</span> 所篩選出的全體優質標的作為判斷樣本。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">TRIGGER</span></div><div class="logic-label-zh">轉折觸發</div></div><div class="logic-desc">鎖定 <span class="highlight">現價突破轉折值</span> 的標的，預判未來行情繼續延伸。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">FUNDAMENTAL</span></div><div class="logic-label-zh">營收動能</div></div><div class="logic-desc">追蹤 <span class="highlight">今年以來累積營收YoY(%)</span>，確保基本面支撐。</div></div>
            <div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SMART MONEY</span></div><div class="logic-label-zh">法人籌碼</div></div><div class="logic-desc">觀察近 20 日 <span class="highlight">法人買賣超動向</span>，確認機構資金流向。</div></div>
        </div>
        """
    st.markdown(logic_html, unsafe_allow_html=True)

    if st.button("啟動AI量化篩選", use_container_width=True):
        p_placeholder = st.empty() 
        
        for progress in range(10, 101, 15):
            p_placeholder.markdown(f'''
            <div class="scanner-ritual-wrapper">
                <div class="quantum-ritual-core">
                    <div class="core-diamond"></div>
                    <div class="core-ring"></div>
                </div>
                <div class="scanner-ritual-text-group">
                    <div class="scanner-ritual-status">多因子量化篩選中...</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {progress}%;"></div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            time.sleep(1.0)

        try:
            def fetch_and_rename(filepath):
                if not os.path.exists(filepath): return pd.DataFrame()
                d = pd.read_csv(filepath)
                
                rename_map = {
                    "股價代號": "代號", "公司名稱": "名稱", "產業別": "產業", 
                    "當日漲幅(%)": "漲幅(%)", "漲幅 (%)": "漲幅(%)", 
                    "季乖離": "季乖離(%)", "年乖離": "年乖離(%)",
                    "月營收MoM(%)": "月營收MoM(%)", "月營收MoM (%)": "月營收MoM(%)",
                    "月營收YoY(%)": "月營收YoY(%)", "月營收YoY (%)": "月營收YoY(%)", 
                    "今年以來累積營收YoY(%)": "今年營收YoY(%)", "今年營收YoY (%)": "今年營收YoY(%)",
                    "近20日法人買賣超(張數)": "20日法人買賣超(張)", "近20日法人買超(張數)": "20日法人買賣超(張)", 
                    "近20日法人買賣超(張)": "20日法人買賣超(張)", "20日法人買賣超 (張)": "20日法人買賣超(張)"
                }
                return d.rename(columns=rename_map)

            df1 = fetch_and_rename("daily_result.csv")
            df2 = fetch_and_rename("momentum_result.csv")
            df_d = fetch_and_rename("strategy_d_result.csv")
            df_e = fetch_and_rename("strategy_e_result.csv")
            
            if "A." in strategy_choice: 
                df_f = df1
            elif "B." in strategy_choice: 
                df_f = df2
            elif "C." in strategy_choice:
                # 🚨 強制進行嚴格交集：必須同時存在於 A(df1) 與 B(df2)
                if not df1.empty and not df2.empty:
                    intersection_ids = set(df1['代號']).intersection(set(df2['代號']))
                    df_f = df1[df1['代號'].isin(intersection_ids)].copy()
                else: df_f = pd.DataFrame()
            elif "D." in strategy_choice:
                df_f = df_d
            elif "E." in strategy_choice:
                df_f = df_e
            else:
                id_map = {}
                if not df1.empty:
                    for sid in df1['代號'].astype(str): id_map.setdefault(sid, set()).add("A")
                if not df2.empty:
                    for sid in df2['代號'].astype(str): id_map.setdefault(sid, set()).add("B")
                
                for sid, tags in id_map.items():
                    if "A" in tags and "B" in tags: tags.add("C")
                
                if not df_d.empty:
                    for sid in df_d['代號'].astype(str): id_map.setdefault(sid, set()).add("D")
                if not df_e.empty:
                    for sid in df_e['代號'].astype(str): id_map.setdefault(sid, set()).add("E")

                dfs_to_concat = [d for d in [df1, df2, df_d, df_e] if not d.empty]
                if dfs_to_concat:
                    df_combined = pd.concat(dfs_to_concat, ignore_index=True).drop_duplicates(subset=['代號'])
                    
                    if '現價' in df_combined.columns and '轉折值' in df_combined.columns:
                        df_combined['現價_num'] = pd.to_numeric(df_combined['現價'], errors='coerce')
                        df_combined['轉折_num'] = pd.to_numeric(df_combined['轉折值'], errors='coerce')
                        df_f = df_combined[(df_combined['現價_num'] > df_combined['轉折_num']) & (df_combined['轉折_num'] > 0)].copy()
                        
                        def remark_name(row):
                            sid = str(row['代號'])
                            tags = sorted(list(id_map.get(sid, set())))
                            tag_str = ",".join(tags) if tags else ""
                            return f"{row['名稱']} ({tag_str})" if tag_str else row['名稱']
                        
                        if not df_f.empty:
                            df_f['名稱'] = df_f.apply(remark_name, axis=1)
                        
                        df_f = df_f.drop(columns=['現價_num', '轉折_num'])
                    else: df_f = pd.DataFrame()
                else:
                    df_f = pd.DataFrame()
                
            if not df_f.empty:
                if '編號' in df_f.columns: df_f = df_f.drop(columns=['編號'])
                # 計算所有策略的轉折乖離
                if '現價' in df_f.columns and '轉折值' in df_f.columns:
                    p_num = pd.to_numeric(df_f['現價'], errors='coerce')
                    v_num = pd.to_numeric(df_f['轉折值'], errors='coerce')
                    df_f['轉折乖離(%)'] = ((p_num - v_num) / v_num.replace(0, pd.NA) * 100).fillna(0).round(2)
                df_f = df_f.reset_index(drop=True)
                st.session_state.update({'temp_df': df_f, 'selected_strategy': strategy_choice, 'scan_completed': True})
                st.rerun()
            else: 
                p_placeholder.empty()
                st.warning("💡 目前無符合標的。")
        except Exception as e: 
            p_placeholder.empty()
            st.error(f"⚠️ 資料讀取異常：請確認 CSV 檔案是否已成功傳送至此儲存庫。")

else:
    df = st.session_state['temp_df']
    strategy_choice = st.session_state['selected_strategy']
    
    st.button("重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}), use_container_width=True)
    
    # 🚨 終極鎖定版：嚴格對齊圖片中的 12 個欄位，確保不論切換到 A~F 任何策略，畫面絕對一模一樣
    base_cols = [
        "代號", "名稱", "產業", "現價", "漲幅(%)", "季乖離(%)", "年乖離(%)", 
        "月營收MoM(%)", "月營收YoY(%)", "今年營收YoY(%)", "20日法人買賣超(張)", 
        "轉折值", "轉折乖離(%)"
    ]
        
    # 如果該策略的 CSV 本來沒有某個欄位 (例如 E 沒有法人)，自動補齊避免跑版
    for col in base_cols:
        if col not in df.columns:
            df[col] = pd.NA

    display_cols = base_cols

    avg_ret = 0.0
    if "漲幅(%)" in df.columns and len(df) > 0: avg_ret = pd.to_numeric(df["漲幅(%)"], errors='coerce').mean()
    if pd.isna(avg_ret): avg_ret = 0.0
    
    ret_class = "return-val-up" if avg_ret > 0 else ("return-val-down" if avg_ret < 0 else "return-val-zero")
    ret_sign = "+" if avg_ret > 0 else ""
    avg_ret_str = f"{ret_sign}{avg_ret:.2f}"

    st.markdown(f'''
        <div class="strategy-header-container">
            <div class="quantum-status-tag"><span class="status-tag-text">QUANTUM SCANNER SUMMARY</span></div>
            <h3 class="strategy-title">{strategy_choice}</h3>
        </div>
        <div class="summary-box-group">
            <div class="result-summary"><span class="result-text">共篩選出 :</span><span class="result-num">{len(df)}</span><span class="result-text">檔標的</span></div>
            <div class="return-summary"><span class="result-text">平均漲幅 :</span><span class="{ret_class}">{avg_ret_str}%</span></div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 🚨 將代號與名稱合體
    if "代號" in display_cols and "名稱" in display_cols:
        df_for_display = df[display_cols].copy()
        df_for_display.insert(0, "代號 / 名稱", df_for_display["代號"].astype(str) + " " + df_for_display["名稱"])
        df_for_display = df_for_display.drop(columns=["代號", "名稱"]).set_index("代號 / 名稱")
    elif "代號" in display_cols:
        df_for_display = df[display_cols].set_index(["代號"])
    else:
        df_for_display = df[display_cols]
        
    col_config = {
        "代號 / 名稱": st.column_config.TextColumn(width=160), 
        "產業": st.column_config.TextColumn(width=125),
        "現價": st.column_config.NumberColumn(width=85),
        "漲幅(%)": st.column_config.NumberColumn(width=85),
        "季乖離(%)": st.column_config.NumberColumn(width=95),
        "年乖離(%)": st.column_config.NumberColumn(width=95),
        "月營收MoM(%)": st.column_config.NumberColumn(width=115),
        "月營收YoY(%)": st.column_config.NumberColumn(width=115),
        "今年營收YoY(%)": st.column_config.NumberColumn(width=125),
        "20日法人買賣超(張)": st.column_config.NumberColumn(width=150),
        "轉折值": st.column_config.NumberColumn(width=85),
        "轉折乖離(%)": st.column_config.NumberColumn(width=95)
    }

    format_dict = {c: "{:.2f}" for c in df_for_display.columns if any(x in c for x in ["現價", "乖離", "報酬", "YoY", "MoM", "轉折值", "漲幅"])}
    for c in df_for_display.columns: 
        if "法人" in c or "買超" in c or "張" in c: format_dict[c] = "{:,.0f}"

    styled_df = df_for_display.style.apply(highlight_pivot_full_row, axis=1).format(format_dict, na_rep="-")
    
    st.dataframe(styled_df, use_container_width=True, column_config=col_config)

    st.markdown('''
        <div id="disclaimer-target" class="disclaimer-wrapper">
            <div class="disclaimer-header"><div class="pulse-dot-small"></div><h4 class="disclaimer-title">重要免責聲明</h4></div>
            <ul class="disclaimer-list">
                <li class="disclaimer-item">1.系統篩選結果均為量化模型產出，僅供研究參考不構成投資建議。</li>
                <li class="disclaimer-item">2.過往績效不保證未來表現，請做好自身風控本系統不負法律責任。</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)

st.markdown(f'''<div class="footer-wrapper"><div class="brand-copyright">QUANTUM DATA SYSTEM © 2026</div><div class="design-container"><span class="design-tag">Developer / Design</span><span class="design-email-tech">WU.CHIACHAN@GMAIL.COM</span></div></div>''', unsafe_allow_html=True)
