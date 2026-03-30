import streamlit as st, pandas as pd, datetime, os, time
import streamlit.components.v1 as components

GITHUB_USER, GITHUB_REPO = "chiachan0108", "stock-data"
st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# [CSS 樣式極致壓縮版] 絕對保留未提及的設計與排版，並大幅升級反查模組的專屬 UI 質感與 RWD 響應式防斷行
st.markdown("""<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap'); html, body, [class*="css"], .stApp, [data-testid="stHeader"], [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] { font-family: 'Inter', 'Noto Sans TC', sans-serif !important; background-color: #0b0f19 !important; color: #e2e8f0 !important; -webkit-font-smoothing: antialiased; overscroll-behavior-y: none; } ::-webkit-scrollbar { width: 6px; height: 6px; } ::-webkit-scrollbar-track { background: rgba(11, 15, 25, 0.9); } ::-webkit-scrollbar-thumb { background: rgba(0, 242, 255, 0.3); border-radius: 10px; } ::-webkit-scrollbar-thumb:hover { background: rgba(0, 242, 255, 0.6); } [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu { visibility: hidden !important; display: none !important; } @keyframes fadeSlideUp { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } } .fade-in-container { animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; } .pulse-dot-small { width: 8px; height: 8px; background-color: #00f2ff; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 0 rgba(0, 242, 255, 0.4); animation: breathing 2.5s infinite; flex-shrink: 0; } @keyframes breathing { 0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.6); } 70% { box-shadow: 0 0 0 8px rgba(0, 242, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); } } .header-group { margin-top: -45px; margin-bottom: 5px; animation: fadeSlideUp 0.4s ease-out forwards; } .main-title { font-family: 'JetBrains Mono', monospace !important; font-weight: 700; letter-spacing: -2px; background: linear-gradient(90deg, #00f2ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(2.0rem, 6vw, 3.5rem); line-height: 1.1; margin: 0; } .status-pill { display: inline-flex; align-items: center; white-space: nowrap; background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); padding: 6px 16px; border-radius: 50px; font-size: 0.8rem; color: rgba(148, 163, 184, 0.9); margin-bottom: 20px; font-weight: 500; letter-spacing: 0.5px; } .status-val { color: #ffffff; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-left: 6px; } .section-header-container { margin-top: 25px; margin-bottom: 16px; display: flex; align-items: center; position: relative; animation: fadeSlideUp 0.5s ease-out forwards; } .section-accent { width: 4px; height: 34px; background: linear-gradient(180deg, #00f2ff, #0072ff); border-radius: 4px; margin-right: 14px; box-shadow: 0 0 12px rgba(0, 242, 255, 0.4); } .section-header-text { display: flex; flex-direction: column; justify-content: center; } .section-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: rgba(0, 242, 255, 0.9); letter-spacing: 2px; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; line-height: 1; } .section-label-zh { font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: 1.5px; line-height: 1; } .section-line { flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 242, 255, 0.2), transparent); margin-left: 20px; } .stRadio > div[role="radiogroup"] { display: flex !important; flex-direction: column !important; gap: 12px !important; margin-top: 10px !important; margin-bottom: 10px !important; } .stRadio div[role="radiogroup"] input[type="radio"], .stRadio div[role="radiogroup"] label > div:first-child, .stRadio div[role="radiogroup"] div[data-baseweb="radio"] > div:first-child { display: none !important; opacity: 0 !important; width: 0 !important; height: 0 !important; position: absolute !important; } .stRadio div[role="radiogroup"] label { background-color: #0b0f19 !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 8px !important; padding: 14px 20px !important; margin: 0 !important; cursor: pointer !important; transition: all 0.3s ease !important; display: flex !important; align-items: center !important; width: 100% !important; } .stRadio div[role="radiogroup"] label:hover { border-color: rgba(0, 242, 255, 0.4) !important; } .stRadio div[role="radiogroup"] label:has(input[type="radio"]:checked) { border: 1px solid #00f2ff !important; background-color: #0b0f19 !important; box-shadow: 0 0 15px rgba(0, 242, 255, 0.2), inset 0 0 8px rgba(0, 242, 255, 0.1) !important; } .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"], .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p { background: transparent !important; border: none !important; margin: 0 !important; padding: 0 !important; color: #94a3b8 !important; font-family: 'JetBrains Mono', 'Noto Sans TC', monospace !important; font-size: 1.05rem !important; font-weight: 600 !important; display: flex !important; align-items: center !important; width: 100% !important; } .stRadio div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] > p::before { content: ''; display: inline-block !important; width: 8px !important; height: 8px !important; border-radius: 50% !important; background-color: rgba(255, 255, 255, 0.15) !important; margin-right: 15px !important; transition: all 0.3s ease !important; border: none !important; transform: none !important; box-shadow: none !important; flex-shrink: 0 !important; } .stRadio div[role="radiogroup"] label:has(input[type="radio"]:checked) div[data-testid="stMarkdownContainer"] > p::before { background-color: #00f2ff !important; box-shadow: 0 0 8px #00f2ff, 0 0 15px #00f2ff !important; } .stRadio div[role="radiogroup"] label:has(input[type="radio"]:checked) div[data-testid="stMarkdownContainer"] > p { color: #00f2ff !important; font-weight: 800 !important; text-shadow: 0 0 8px rgba(0, 242, 255, 0.4) !important; } .stButton > button { background: rgba(0, 242, 255, 0.08) !important; color: #ffffff !important; border: 1px solid rgba(0, 242, 255, 0.4) !important; backdrop-filter: blur(8px) !important; border-radius: 10px !important; font-weight: 900 !important; text-shadow: -0.5px -0.5px 0 #000, 0.5px -0.5px 0 #000, -0.5px 0.5px 0 #000, 0.5px 0.5px 0 #000 !important; letter-spacing: 2px; width: 100% !important; min-height: 62px !important; font-size: 1.25rem !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important; position: relative; padding: 0 !important; } .stButton > button:hover { background: rgba(0, 242, 255, 0.15) !important; border: 1px solid rgba(0, 242, 255, 0.8) !important; box-shadow: 0 0 25px rgba(0, 242, 255, 0.35) !important; transform: translateY(-2px) !important; } .stButton > button:active { transform: translateY(1px) !important; box-shadow: 0 0 10px rgba(0, 242, 255, 0.2) !important; } .stButton > button div[data-testid="stMarkdownContainer"] { display: flex !important; align-items: center !important; justify-content: center !important; width: 100% !important; height: 100% !important; margin: 0 !important; padding: 0 !important; } .stButton > button div[data-testid="stMarkdownContainer"] p { display: flex !important; align-items: center !important; justify-content: center !important; margin: 0 !important; padding: 0 !important; line-height: 1 !important; transform: translate(-4px, 2px) !important; } .stButton > button div[data-testid="stMarkdownContainer"] p::before { content: ''; display: block !important; flex-shrink: 0 !important; width: 11px; height: 11px; background: rgba(0, 242, 255, 0.8); margin-right: 14px !important; transform: rotate(45deg); border: 0.5px solid #000; box-shadow: 4px -4px 0 rgba(0, 242, 255, 0.4); } .logic-grid { display: grid; gap: 16px; grid-template-columns: 1fr; grid-auto-rows: 1fr; margin-bottom: 25px; margin-top: 10px; } @media (min-width: 1024px) { .logic-grid { grid-template-columns: repeat(4, 1fr) !important; } } .logic-item { background: linear-gradient(145deg, rgba(22, 27, 34, 0.9) 0%, rgba(11, 15, 25, 0.95) 100%); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 12px; padding: 20px 16px; transition: all 0.3s ease; height: 100%; display: flex; flex-direction: column; position: relative; box-shadow: inset 0 0 15px rgba(0, 242, 255, 0.02), 0 4px 12px rgba(0, 0, 0, 0.2); opacity: 0; animation: fadeSlideUp 0.5s ease-out forwards; } .logic-item:nth-child(1) { animation-delay: 0.1s; } .logic-item:nth-child(2) { animation-delay: 0.2s; } .logic-item:nth-child(3) { animation-delay: 0.3s; } .logic-item:nth-child(4) { animation-delay: 0.4s; } .logic-item:nth-child(5) { animation-delay: 0.5s; } .logic-item:nth-child(6) { animation-delay: 0.6s; } .logic-item:nth-child(7) { animation-delay: 0.7s; } .logic-item:nth-child(8) { animation-delay: 0.8s; } .logic-item::before { content: ''; position: absolute; top: 0; left: 15%; right: 15%; height: 1.5px; background: linear-gradient(90deg, transparent, rgba(0, 242, 255, 0.5), transparent); transition: opacity 0.3s ease; opacity: 0.7; } .logic-item:hover { border-color: rgba(0, 242, 255, 0.5); transform: translateY(-4px); box-shadow: inset 0 0 20px rgba(0, 242, 255, 0.05), 0 8px 20px rgba(0, 0, 0, 0.4); } .logic-item:hover::before { opacity: 1; background: linear-gradient(90deg, transparent, rgba(0, 242, 255, 1), transparent); } .logic-header { display: flex; flex-direction: column; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); } .logic-tag-row { display: flex; align-items: center; margin-bottom: 4px; } .logic-index-tag { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 700; color: rgba(0, 242, 255, 0.8); border: 1px solid rgba(0, 242, 255, 0.3); padding: 1px 6px; border-radius: 3px; margin-right: 10px; background: rgba(0, 242, 255, 0.05); } .logic-label-en { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: rgba(148, 163, 184, 0.7); letter-spacing: 1.2px; text-transform: uppercase; } .logic-label-zh { font-size: 1.1rem; font-weight: 700; color: #ffffff; line-height: 1.2; margin-top: 2px; } .logic-desc { font-size: 0.95rem; color: #94a3b8; line-height: 1.65; font-weight: 400; flex-grow: 1; } .highlight { color: #00f2ff !important; font-weight: 800 !important; text-shadow: 0 0 8px rgba(0, 242, 255, 0.4); } .strategy-header-container { border-left: 4px solid #00f2ff; background: linear-gradient(90deg, rgba(0, 242, 255, 0.08) 0%, transparent 100%); padding: 16px 20px; margin-top: 25px; margin-bottom: 15px; border-radius: 0 8px 8px 0; display: flex; flex-direction: column; gap: 6px; animation: fadeSlideUp 0.5s ease-out forwards; } .status-tag-text { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #00f2ff; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; } .strategy-title { font-size: clamp(1.2rem, 4.5vw, 1.6rem) !important; color: #ffffff; font-weight: 800; line-height: 1.4; margin: 0; white-space: normal !important; word-break: keep-all !important; } 
.summary-box-group { display: flex; flex-direction: column; gap: 12px; margin-bottom: 22px; align-items: flex-start; animation: fadeSlideUp 0.6s ease-out forwards; } .result-summary, .return-summary { display: flex; align-items: center; justify-content: center; padding: 0 !important; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.35); border-radius: 6px; margin-bottom: 0px !important; width: 220px; height: 52px; box-sizing: border-box; transition: all 0.3s ease; overflow: hidden; } .result-summary:hover, .return-summary:hover { background: rgba(0, 242, 255, 0.12); border-color: rgba(0, 242, 255, 0.6); box-shadow: 0 0 15px rgba(0, 242, 255, 0.15); } .box-left { display: flex; align-items: center; transform: translateY(1px); } .box-right { display: flex; align-items: center; padding-left: 8px; gap: 4px; transform: translateY(1px); } .box-label { font-weight: 800; font-size: 0.9rem; color: #00f2ff; letter-spacing: 0.5px; line-height: 1; margin: 0; } .box-num { font-family: 'Inter', sans-serif; font-size: 1.15rem; color: #ffffff; font-weight: 700; line-height: 1; margin: 0; } .box-unit { font-weight: 800; font-size: 0.9rem; color: #00f2ff; line-height: 1; margin: 0; } .return-val-up { color: #ff3333 !important; } .return-val-down { color: #00ff33 !important; } .return-val-zero { color: #ffffff !important; } .scanner-ritual-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center !important; background: radial-gradient(circle at center, rgba(11, 15, 25, 0.95), #0b0f19); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 12px; width: clamp(280px, 90%, 400px); min-height: 180px; margin: 20px auto !important; box-shadow: 0 0 30px rgba(0, 242, 255, 0.05); position: relative; overflow: hidden; padding: 25px; } .scanner-ritual-wrapper::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(0, 242, 255, 0.02) 0%, transparent 60%); animation: dataSyncFlow 5s linear infinite; } .quantum-ritual-core { position: relative; width: 60px; height: 60px; margin-bottom: 25px; display: flex; align-items: center; justify-content: center !important; } .core-diamond { position: absolute; width: 35px; height: 35px; background: rgba(0, 242, 255, 0.8); border: 0.5px solid #000; box-shadow: 4px -4px 0 rgba(0, 242, 255, 0.4); transform: rotate(45deg); animation: ritualDiamond 3s ease-in-out infinite; } .core-ring { position: absolute; width: 60px; height: 60px; border: 1.5px solid rgba(0, 242, 255, 0.2); border-radius: 50%; border-top-color: rgba(0, 242, 255, 0.8); border-bottom-color: rgba(0, 242, 255, 0.8); animation: ritualRing 3s linear infinite; } .core-ring::after { content: ''; position: absolute; width: 45px; height: 45px; border: 1.5px solid rgba(0, 242, 255, 0.1); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(0deg); border-right-color: rgba(0, 242, 255, 0.6); border-left-color: rgba(0, 242, 255, 0.6); animation: ritualRingInner 3s linear infinite; } .scanner-ritual-text-group { text-align: center; width: 100%; } .scanner-ritual-status { font-family: 'Inter', 'Noto Sans TC', sans-serif !important; font-weight: 800 !important; color: #ffffff !important; font-size: 1.05rem !important; letter-spacing: 1.5px !important; margin-bottom: 15px !important; line-height: 1.2 !important; text-shadow: -0.5px -0.5px 0 #000, 0.5px -0.5px 0 #000, -0.5px 0.5px 0 #000, 0.5px 0.5px 0 #000 !important; } .progress-bar-container { width: 80%; height: 6px; background-color: rgba(0, 242, 255, 0.1); border-radius: 10px; overflow: hidden; margin: 0 auto; position: relative; border: 1px solid rgba(0, 242, 255, 0.2); } .progress-bar-fill { height: 100%; background: linear-gradient(90deg, #0072ff, #00f2ff); border-radius: 10px; box-shadow: 0 0 10px rgba(0, 242, 255, 0.8); width: 0%; transition: width 0.3s ease; } @keyframes dataSyncFlow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } } .dataframe-wrapper { animation: fadeSlideUp 0.7s ease-out forwards; padding: 2px; border-radius: 14px; background: linear-gradient(180deg, rgba(0,242,255,0.15) 0%, rgba(0,0,0,0) 100%); } [data-testid="stDataFrame"] { border: 1px solid rgba(0, 242, 255, 0.25) !important; border-radius: 12px !important; padding: 4px !important; background-color: #0b0f19 !important; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4); overscroll-behavior: contain !important; touch-action: pan-x pan-y !important; } [data-testid="stDataFrame"] div[data-testid="stTable"] { background-color: #0b0f19 !important; overscroll-behavior: contain !important; -webkit-overflow-scrolling: touch !important; } [data-testid="stDataFrame"] th { background-color: #161b2a !important; color: #94a3b8 !important; border-bottom: 1px solid rgba(0, 242, 255, 0.2) !important; font-weight: 700 !important; } [data-testid="stDataFrame"] td { background-color: #0b0f19 !important; color: #ffffff !important; } .empty-state-glass { padding: 40px; text-align: center; background: linear-gradient(135deg, rgba(0, 242, 255, 0.05) 0%, rgba(11, 15, 25, 0.8) 100%); border: 1px dashed rgba(0, 242, 255, 0.3); border-radius: 16px; margin-top: 30px; animation: fadeSlideUp 0.6s ease-out forwards; backdrop-filter: blur(10px); box-shadow: 0 10px 30px rgba(0,0,0,0.2); } .empty-state-icon { font-size: 48px; margin-bottom: 15px; opacity: 0.9; filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.4)); } .empty-state-title { color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-size: 1.3rem; margin-bottom: 8px; font-weight: 800; letter-spacing: 1px; } .empty-state-desc { color: #94a3b8; font-size: 0.95rem; margin: 0; line-height: 1.6; } .disclaimer-wrapper { background-color: #0e121a; border: 1px solid rgba(0, 242, 255, 0.2) !important; border-radius: 8px; padding: 16px 16px 10px 16px !important; margin-top: 35px !important; margin-bottom: 35px !important; display: flex; flex-direction: column; gap: 10px !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); animation: fadeSlideUp 0.8s ease-out forwards; } .disclaimer-header { display: flex; align-items: center; margin-bottom: 0px !important; } .disclaimer-title { font-weight: 700; color: #ffffff; font-size: 14px !important; letter-spacing: 0.5px; margin: 0 !important; padding: 0 !important; line-height: 1 !important; display: flex; align-items: center; } .disclaimer-list { display: flex; flex-direction: column; gap: 6px !important; list-style: none; padding: 0 !important; padding-left: 18px !important; margin: 0 !important; } .disclaimer-item { font-size: 13px !important; color: #94a3b8; line-height: 1.4 !important; font-weight: 400; margin: 0 !important; text-align: justify !important; text-justify: inter-ideograph !important; } .footer-wrapper { margin-top: 60px; padding: 30px 10px 50px 10px; border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; justify-content: center !important; } .brand-copyright { color: #94a3b8; font-weight: 800 !important; font-size: 0.85rem !important; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; } .design-container { display: flex; align-items: center; justify-content: center; gap: 15px; flex-wrap: wrap; } .design-tag { background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 700; padding: 3px 8px 2px 8px; border-radius: 4px; text-transform: uppercase; display: inline-flex; align-items: center; justify-content: center; line-height: 1; height: 20px; box-sizing: border-box; } .design-email-tech { font-family: 'JetBrains Mono', monospace !important; color: #ffffff !important; font-size: 0.65rem !important; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; opacity: 0.9; display: inline-flex; align-items: center; height: 20px; } @media (max-width: 768px) { .design-container { flex-direction: column; gap: 10px; } }

/* 🔥 升級版：個股反查雷達專屬 Glassmorphism CSS (防斷行修復版) */
.search-box-glass {
    background: linear-gradient(135deg, rgba(11, 15, 25, 0.95) 0%, rgba(22, 27, 34, 0.85) 100%);
    border: 1px solid rgba(0, 242, 255, 0.25);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(0, 242, 255, 0.05);
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
    animation: fadeSlideUp 0.5s ease-out forwards;
}
.search-box-glass::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 242, 255, 0.8), transparent);
}
.search-header-row {
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
    border-bottom: 1px dashed rgba(0, 242, 255, 0.2);
    padding-bottom: 16px; margin-bottom: 16px;
}
.id-name-group {
    display: flex; align-items: baseline; flex-wrap: wrap; gap: 6px;
}
.search-target-id {
    font-family: 'JetBrains Mono', monospace; font-size: clamp(1.4rem, 6vw, 2.2rem); font-weight: 900;
    color: #ffffff; text-shadow: 0 0 15px rgba(0, 242, 255, 0.4); line-height: 1; margin: 0; display: inline-block;
}
.search-target-name {
    font-size: clamp(1rem, 4.5vw, 1.3rem); font-weight: 800; color: #e2e8f0; margin-left: 10px; letter-spacing: 2px;
    white-space: nowrap; word-break: keep-all; display: inline-block;
}
.search-status-tag {
    background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.4);
    padding: 4px 10px; border-radius: 4px; color: #00f2ff;
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 800; letter-spacing: 1px;
}
.search-badges-container {
    display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px;
}
.strat-badge-premium {
    background: linear-gradient(90deg, rgba(22, 27, 34, 0.9), rgba(11, 15, 25, 0.9));
    border: 1px solid rgba(0, 242, 255, 0.3); border-left: 3px solid #00f2ff;
    padding: 8px 14px; border-radius: 6px; color: #e2e8f0; font-weight: 600;
    font-size: 0.9rem; display: flex; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}
.strat-badge-premium:hover {
    border-color: rgba(0, 242, 255, 0.7); box-shadow: 0 4px 15px rgba(0, 242, 255, 0.2);
    transform: translateY(-2px);
}
.strat-badge-premium span {
    color: #00f2ff; font-family: 'JetBrains Mono', monospace; font-weight: 800; margin-right: 6px;
}
.search-subtitle {
    color: #94a3b8; font-size: 0.9rem; letter-spacing: 1px; margin-bottom: 12px; display: flex; align-items: center; font-weight: 500;
}
.search-subtitle svg {
    margin-right: 8px; filter: drop-shadow(0 0 5px rgba(0, 242, 255, 0.5)); flex-shrink: 0;
}
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

# 🔥 [全域快取獲取模組]：提升至最外層，讓主系統與反查系統能共用同一個快取資料
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
    return df.rename(columns=rename_map)

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False
now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
data_date = now_taipei.strftime('%Y/%m/%d') if (now_taipei.hour >= 20) else (now_taipei - datetime.timedelta(days=1)).strftime('%Y/%m/%d')

st.markdown(f'''<div class="header-group"><h1 class="main-title">QUANTUM SCANNER</h1><div class="status-pill"><div class="pulse-dot-small"></div>LAST UPDATE : <span class="status-val">{data_date} 20:00</span></div></div>''', unsafe_allow_html=True)

if not st.session_state['scan_completed']:
    
    # 🎯 [優化版 UI] 將 Emoji 替換為高質感幾何符號，整體風格冷峻化
    with st.expander("◈ 個股量化雷達反查 (輸入代號或名稱)", expanded=False):
        search_query = st.text_input("請輸入股價代號或名稱 (例如: 2330 或 台積電)", key="search_input").strip()
        if search_query:
            # 獲取所有策略資料
            s_a, s_b, s_d, s_e, s_f, s_g, s_h = map(fetch_and_rename, [
                "strategy_a_result.csv", "strategy_b_result.csv", "strategy_d_result.csv", 
                "strategy_e_result.csv", "strategy_f_result.csv", "strategy_g_result.csv", "strategy_h_result.csv"
            ])
            
            hit_strategies = []
            match_info = {"id": "", "name": "", "price": 0.0, "pivot": 0.0}

            def check_hit(df, strat_name):
                if not df.empty and '代號' in df.columns and '名稱' in df.columns:
                    mask = (df['代號'].astype(str) == search_query) | (df['名稱'].astype(str).str.contains(search_query, na=False))
                    hits = df[mask]
                    if not hits.empty:
                        match_info["id"] = str(hits.iloc[0]['代號'])
                        match_info["name"] = str(hits.iloc[0]['名稱'])
                        # 捕捉現價與轉折值，供後續策略 S 判定使用
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
            
            # 策略 C 判定邏輯 (交集)
            if "A. 營收趨勢增長型" in hit_strategies and "B. 股價強勢動能型" in hit_strategies:
                hit_strategies.append("C. 營收股價雙能型")
                
            # 策略 S 判定邏輯 (只要符合任一策略，且現價大於轉折值)
            if hit_strategies and match_info["price"] > match_info["pivot"] and match_info["pivot"] > 0:
                hit_strategies.append("S. 趨勢轉折延伸型")
                
            hit_strategies.sort()

            if hit_strategies:
                # 採用全新升級的 Glassmorphism UI 加上純手工繪製的 SVG 科技瞄準星
                badge_html = "".join([f"<div class='strat-badge-premium'><span>{s.split('.')[0]}.</span>{s.split('.')[1].strip()}</div>" for s in hit_strategies])
                result_html = f"""
                <div class="search-box-glass">
                    <div class="search-header-row">
                        <div class="id-name-group">
                            <span class="search-target-id">{match_info['id']}</span>
                            <span class="search-target-name">{match_info['name']}</span>
                        </div>
                        <div class="search-status-tag">MATCHED</div>
                    </div>
                    <div class="search-subtitle">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00f2ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 9V5h4M19 9V5h-4M5 15v4h4M19 15v4h-4M12 12h.01"/></svg>
                        標的當前觸發之量化策略矩陣：
                    </div>
                    <div class="search-badges-container">
                        {badge_html}
                    </div>
                </div>
                """
                st.markdown(result_html, unsafe_allow_html=True)
            else:
                st.warning("⚠️ 查無相符資料。該標的目前可能未符合任何嚴格的量化策略濾網，或輸入格式有誤。")

    st.markdown("<div class='section-header-container'><div class='section-accent'></div><div class='section-header-text'><span class='section-label-en'>STRATEGY CONFIGURATION</span><span class='section-label-zh'>策略類型選取</span></div><div class='section-line'></div></div>", unsafe_allow_html=True)
    strategy_choice = st.radio("量化策略模組", ["A. 營收趨勢增長型", "B. 股價強勢動能型", "C. 營收股價雙能型", "D. 法人籌碼吃貨型", "E. 市場區間共振型", "F. 左側超跌優質型", "G. 中長周期轉折型", "H. 財報三率三升型", "S. 趨勢轉折延伸型"], label_visibility="collapsed")
    st.markdown("<div class='section-header-container'><div class='section-accent'></div><div class='section-header-text'><span class='section-label-en'>SYSTEM ARCHITECTURE</span><span class='section-label-zh'>策略核心邏輯</span></div><div class='section-line'></div></div>", unsafe_allow_html=True)
    
    # [HTML 邏輯區塊極致壓縮版] 
    logic_dict = {
        "A.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">鎖定台灣<span class="highlight">全體上市櫃普通股</span>標的.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近60日的日均量必須大於<span class="highlight">500張</span>，確保流動性安全無虞.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">LEVEL</span></div><div class="logic-label-zh">技術位階</div></div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">TREND</span></div><div class="logic-label-zh">趨勢排列</div></div><div class="logic-desc"><span class="highlight">MA60 大於 MA240</span>，呈現多頭排列走勢.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">05</span><span class="logic-label-en">SCALE</span></div><div class="logic-label-zh">營收規模</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下<span class="highlight">公司有史以來同期新高</span>.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">06</span><span class="logic-label-en">MOMENTUM</span></div><div class="logic-label-zh">雙巔峰動能</div></div><div class="logic-desc">單月營收<span class="highlight">歷史新高與次高</span>必須同時在近6、12個月內.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">07</span><span class="logic-label-en">DYNAMICS</span></div><div class="logic-label-zh">雙重成長</div></div><div class="logic-desc">確保近1季 <span class="highlight">YoY 正成長</span>且今年營收YoY(%)<span class="highlight">大於20%</span>.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">08</span><span class="logic-label-en">TRACKING</span></div><div class="logic-label-zh">法人佈局位階</div></div><div class="logic-desc">追蹤近20日<span class="highlight">三大法人</span>買賣超張數及<span class="highlight">股價乖離率</span>.</div></div></div>',
        "B.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc"><span class="highlight">全體上市櫃公司</span>，排除 ETF、ETN、存託憑證及下市黑名單.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近60日的日均量必須大於<span class="highlight">500張</span>，確保流動性安全無虞.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">STRENGTH</span></div><div class="logic-label-zh">相對強勢動能</div></div><div class="logic-desc">股價短中長期皆強勢，<span class="highlight">近20日、60日與240日報酬</span>超越大盤同期績效.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">CASHFLOW</span></div><div class="logic-label-zh">法人資金流</div></div><div class="logic-desc">近 5、20 個交易日三大法人合計皆呈現<span class="highlight">淨買超狀態</span>，具備機構短、中期資金護航實力.</div></div></div>',
        "C.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">INTERSECTION</span></div><div class="logic-label-zh">雙引擎交集</div></div><div class="logic-desc">抓出具備<span class="highlight">營收創高成長</span>與<span class="highlight">技術強勢動能</span>的交集標的.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">FUNDAMENTAL</span></div><div class="logic-label-zh">基本面護城河</div></div><div class="logic-desc"><span class="highlight">近1年累積營收</span>創歷史同期新高，且今年以來累積 YoY <span class="highlight">大於 20%</span>.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">TECHNICAL</span></div><div class="logic-label-zh">技術面爆發</div></div><div class="logic-desc"><span class="highlight">短、中、長期報酬</span>全數超越大盤同期績效.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SMART MONEY</span></div><div class="logic-label-zh">法人雙重認同</div></div><div class="logic-desc">確保近 5、20 日三大法人皆為<span class="highlight">淨買超</span>，具備機構短、中期資金護航實力.</div></div></div>',
        "D.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">四重防線</div></div><div class="logic-desc">近 20、60、120、240 日均量<span class="highlight">皆大於500張</span>，確保短、中、長線流動性皆安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">WHALE CHIP</span></div><div class="logic-label-zh">巨鯨級籌碼</div></div><div class="logic-desc">法人近 60 日淨買超必須<span class="highlight">大於 10,000 張</span>，確保重金護盤。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">CONTINUITY</span></div><div class="logic-label-zh">買盤延續</div></div><div class="logic-desc">近 20 日與近 5 日的法人動向皆維持<span class="highlight">正向淨買超</span>，無短期反手倒貨。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">STEP ACCUM</span></div><div class="logic-label-zh">階梯創高吃貨</div></div><div class="logic-desc">買超張數 <span class="highlight">60日>20日>5日</span>，且法人近5日總持股創<span class="highlight">近 60 日新高</span>。</div></div></div>',
        "E.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">流動性門檻</div></div><div class="logic-desc">近1季日平均日成交量需大於 <span class="highlight">1,000張</span>，確保流動性無虞.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">VOL SPIKE</span></div><div class="logic-label-zh">異常攻擊表態</div></div><div class="logic-desc">近1個月內至少有兩天以上成交量<span class="highlight">大於季均量 3 倍</span>，確認市場大量換手.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">RESONANCE</span></div><div class="logic-label-zh">籌碼極致共振</div></div><div class="logic-desc">季度市場加權成本價 (AVWAP)，與成交區間重心價 (POC) 差距在 <span class="highlight">3% 以內</span>.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PULLBACK</span></div><div class="logic-label-zh">量縮沉澱買點</div></div><div class="logic-desc">現價與市場加權成本價 (AVWAP) 差距在 <span class="highlight">3% 內</span>，且今日成交量<span class="highlight">小於近 5 日均量</span>.</div></div></div>',
        "F.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">OVERSOLD</span></div><div class="logic-label-zh">超跌位階</div></div><div class="logic-desc">現價為近半年最高點以來<span class="highlight">修正20%以上</span>，且近期股價低於月平均價<span class="highlight">10%以上</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">ACCUMULATE</span></div><div class="logic-label-zh">主力吸籌</div></div><div class="logic-desc">近10個交易日成交量<span class="highlight">明顯大於季均量</span>，確認市場籌碼進行大量換手。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">REVENUE</span></div><div class="logic-label-zh">營收巔峰</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下<span class="highlight">公司歷年以來同期新高</span>。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">GROWTH</span></div><div class="logic-label-zh">今年成長</div></div><div class="logic-desc">今年累計營收年增率 (YTD YoY) <span class="highlight">維持正成長</span>。</div></div></div>',
        "G.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc"><span class="highlight">全體上市櫃普通股</span>，嚴格排除 ETF 與 158 檔損壞黑名單.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">四重防線</div></div><div class="logic-desc">近 20、60、120、240 日均量<span class="highlight">皆必須大於500張</span>，確保穩健的長線流動性.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">PIVOT W</span></div><div class="logic-label-zh">中期轉折</div></div><div class="logic-desc">現價必須強勢站上<span class="highlight">週線級別轉折值 (T.A.B 最大值)</span>.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">PIVOT M</span></div><div class="logic-label-zh">長期共振</div></div><div class="logic-desc">現價同步突破<span class="highlight">月線級別轉折值</span>，形成無懼年線位階的強大多頭起漲點.</div></div></div>',
        "H.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">LIQUIDITY</span></div><div class="logic-label-zh">四重防線</div></div><div class="logic-desc">近 20、60、120、240 日均量<span class="highlight">皆大於500張</span>，確保短、中、長線流動性安全無虞。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">MOMENTUM</span></div><div class="logic-label-zh">營收爆發</div></div><div class="logic-desc">近 12 個月累積營收 (LTM) <span class="highlight">強勢超越去年同期</span>，展現強勁動能。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">PROFITABILITY</span></div><div class="logic-label-zh">三率齊揚</div></div><div class="logic-desc">連續 <span class="highlight">3 季</span> 毛利率、營利率、淨利率皆同步上升，公司整體質量逐步優化。</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SAFETY</span></div><div class="logic-label-zh">獲利底線</div></div><div class="logic-desc">最新一季稅後淨利必須<span class="highlight">大於 0</span>，堅決拒絕虛假轉機股。</div></div></div>',
        "S.": '<div class="logic-grid"><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">01</span><span class="logic-label-en">SCOPE</span></div><div class="logic-label-zh">選股範圍</div></div><div class="logic-desc">統整 <span class="highlight">策略 A、B、C、D、E、F、G、H</span> 所篩選出的全體優質標的作為判斷樣本.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">02</span><span class="logic-label-en">TRIGGER</span></div><div class="logic-label-zh">轉折觸發</div></div><div class="logic-desc">鎖定 <span class="highlight">現價突破轉折值</span> 的標的，預判未來行情繼續延伸.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">03</span><span class="logic-label-en">FUNDAMENTAL</span></div><div class="logic-label-zh">營收動能</div></div><div class="logic-desc">追蹤 <span class="highlight">今年以來累積營收 YoY(%)</span>，確保基本面支撐.</div></div><div class="logic-item"><div class="logic-header"><div class="logic-tag-row"><span class="logic-index-tag">04</span><span class="logic-label-en">SMART MONEY</span></div><div class="logic-label-zh">法人籌碼</div></div><div class="logic-desc">觀察近 20 日 <span class="highlight">法人買賣超動向</span>，確認機構資金流向.</div></div></div>'
    }
    st.markdown(next((v for k, v in logic_dict.items() if k in strategy_choice), logic_dict["A."]), unsafe_allow_html=True)

    if st.button("啟動AI量化篩選", use_container_width=True):
        p_placeholder = st.empty() 
        for progress in range(10, 101, 15):
            p_placeholder.markdown(f'<div class="scanner-ritual-wrapper"><div class="quantum-ritual-core"><div class="core-diamond"></div><div class="core-ring"></div></div><div class="scanner-ritual-text-group"><div class="scanner-ritual-status">多因子量化矩陣運算中...</div><div class="progress-bar-container"><div class="progress-bar-fill" style="width: {progress}%;"></div></div></div></div>', unsafe_allow_html=True)
            time.sleep(0.5) 
            
        try:
            # 載入所有策略資料
            df1, df2, df_d, df_e, df_squat, df_g, df_h = map(fetch_and_rename, [
                "strategy_a_result.csv", "strategy_b_result.csv", "strategy_d_result.csv", 
                "strategy_e_result.csv", "strategy_f_result.csv", "strategy_g_result.csv", "strategy_h_result.csv"
            ])
            
            if "A." in strategy_choice: df_f = df1
            elif "B." in strategy_choice: df_f = df2
            elif "C." in strategy_choice:
                df_f = df1[df1['代號'].isin(set(df1['代號']).intersection(set(df2['代號'])))].copy() if not df1.empty and not df2.empty else pd.DataFrame()
            elif "D." in strategy_choice: df_f = df_d
            elif "E." in strategy_choice: df_f = df_e
            elif "F." in strategy_choice: df_f = df_squat
            elif "G." in strategy_choice: df_f = df_g
            elif "H." in strategy_choice: df_f = df_h 
            elif "S." in strategy_choice:
                id_map = {}
                for sid in df1['代號'].astype(str) if not df1.empty else []: id_map.setdefault(sid, set()).add("A")
                for sid in df2['代號'].astype(str) if not df2.empty else []: id_map.setdefault(sid, set()).add("B")
                for sid, tags in id_map.items(): 
                    if "A" in tags and "B" in tags: tags.add("C")
                for sid in df_d['代號'].astype(str) if not df_d.empty else []: id_map.setdefault(sid, set()).add("D")
                for sid in df_e['代號'].astype(str) if not df_e.empty else []: id_map.setdefault(sid, set()).add("E")
                for sid in df_squat['代號'].astype(str) if not df_squat.empty else []: id_map.setdefault(sid, set()).add("F")
                for sid in df_g['代號'].astype(str) if not df_g.empty else []: id_map.setdefault(sid, set()).add("G")
                for sid in df_h['代號'].astype(str) if not df_h.empty else []: id_map.setdefault(sid, set()).add("H")

                dfs_to_concat = [d for d in [df1, df2, df_d, df_e, df_squat, df_g, df_h] if not d.empty]
                if dfs_to_concat:
                    df_combined = pd.concat(dfs_to_concat, ignore_index=True).drop_duplicates(subset=['代號'])
                    if '現價' in df_combined.columns and '轉折值' in df_combined.columns:
                        df_combined['現價_num'] = pd.to_numeric(df_combined['現價'], errors='coerce')
                        df_combined['轉折_num'] = pd.to_numeric(df_combined['轉折值'], errors='coerce')
                        df_f = df_combined[(df_combined['現價_num'] > df_combined['轉折_num']) & (df_combined['轉折_num'] > 0)].copy()
                        df_f['名稱'] = df_f.apply(lambda r: f"{r['名稱']} ({','.join(sorted(list(id_map.get(str(r['代號']), set()))))})" if id_map.get(str(r['代號'])) else r['名稱'], axis=1) if not df_f.empty else df_f['名稱']
                        df_f = df_f.drop(columns=['現價_num', '轉折_num'])
                    else: df_f = pd.DataFrame()
                else: df_f = pd.DataFrame()
                
            if not df_f.empty:
                if '編號' in df_f.columns: df_f = df_f.drop(columns=['編號'])
                if '現價' in df_f.columns and '轉折值' in df_f.columns:
                    v_num = pd.to_numeric(df_f['轉折值'], errors='coerce')
                    df_f['轉折乖離(%)'] = ((pd.to_numeric(df_f['現價'], errors='coerce') - v_num) / v_num.replace(0, pd.NA) * 100).fillna(0).round(2)
                df_f = df_f.reset_index(drop=True)
                st.session_state.update({'temp_df': df_f, 'selected_strategy': strategy_choice, 'scan_completed': True})
                st.toast('量化矩陣資料載入成功！⚡', icon='⚡')
                st.rerun()
            else: 
                p_placeholder.empty()
                st.markdown('<div class="empty-state-glass"><div class="empty-state-icon">📡</div><div class="empty-state-title">TARGET NOT FOUND</div><p class="empty-state-desc">全市場掃描完畢，目前無標的符合此嚴苛策略之濾網條件.</p></div>', unsafe_allow_html=True)
        except Exception as e: 
            p_placeholder.empty()
            st.error(f"⚠️ 資料讀取異常：無法取得 {strategy_choice} 之報告檔案。請確認後端是否已產出該 CSV。")

else:
    components.html(f"""<script id="scroll_{time.time()}">setTimeout(function() {{ const parent = window.parent; parent.scrollTo({{top: 0, behavior: 'smooth'}}); const appViews = parent.document.querySelectorAll('.stApp, [data-testid="stMainBlockContainer"], [data-testid="stAppViewContainer"]'); appViews.forEach(view => {{ view.scrollTo({{top: 0, behavior: 'smooth'}}); }}); }}, 200); </script>""", height=0)
    df, strategy_choice = st.session_state['temp_df'], st.session_state['selected_strategy']
    st.button("重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}), use_container_width=True)
    
    # 🔥 共通欄位顯示配置 (包含所有策略，嚴格不新增未指定的欄位)
    base_cols = ["代號", "名稱", "產業", "現價", "漲幅(%)", "季乖離(%)", "年乖離(%)", "月營收MoM(%)", "月營收YoY(%)", "今年營收YoY(%)", "20日法人買賣超(張)", "轉折值", "轉折乖離(%)"]
    for col in base_cols: 
        if col not in df.columns: df[col] = pd.NA
    display_cols = base_cols

    avg_ret = pd.to_numeric(df["漲幅(%)"], errors='coerce').mean() if "漲幅(%)" in df.columns and len(df) > 0 else 0.0
    if pd.isna(avg_ret): avg_ret = 0.0
    ret_class, ret_sign = "return-val-up" if avg_ret > 0 else ("return-val-down" if avg_ret < 0 else "return-val-zero"), "+" if avg_ret > 0 else ""

    avg_ret_html = f'''
    <div class="strategy-header-container">
      <div class="quantum-status-tag"><span class="status-tag-text">QUANTUM SCANNER SUMMARY</span></div>
      <h3 class="strategy-title">{strategy_choice}</h3>
    </div>
    <div class="summary-box-group">
      
      <div class="result-summary">
        <div class="box-left">
          <span class="box-label">共篩選出 :</span>
        </div>
        <div class="box-right">
          <span class="box-num">{len(df)}</span>
          <span class="box-unit">檔標的</span>
        </div>
      </div>
      
      <div class="return-summary">
        <div class="box-left">
          <span class="box-label">平均漲幅 :</span>
        </div>
        <div class="box-right">
          <span class="box-num {ret_class}">{ret_sign}{avg_ret:.2f}</span>
          <span class="box-unit {ret_class}">%</span>
        </div>
      </div>
      
    </div>
    '''
    st.markdown(avg_ret_html, unsafe_allow_html=True)
    
    df_for_display = df[display_cols].copy()
    if "代號" in display_cols and "名稱" in display_cols:
        df_for_display.insert(0, "代號 / 名稱", df_for_display["代號"].astype(str) + " " + df_for_display["名稱"])
        df_for_display = df_for_display.drop(columns=["代號", "名稱"]).set_index("代號 / 名稱")
    elif "代號" in display_cols: df_for_display = df_for_display.set_index(["代號"])
        
    col_config = {"代號 / 名稱": st.column_config.TextColumn(width=160), "產業": st.column_config.TextColumn(width=125), "現價": st.column_config.NumberColumn(width=85), "漲幅(%)": st.column_config.NumberColumn(width=85), "季乖離(%)": st.column_config.NumberColumn(width=95), "年乖離(%)": st.column_config.NumberColumn(width=95), "月營收MoM(%)": st.column_config.NumberColumn(width=115), "月營收YoY(%)": st.column_config.NumberColumn(width=115), "今年營收YoY(%)": st.column_config.NumberColumn(width=125), "20日法人買賣超(張)": st.column_config.NumberColumn(width=150), "轉折值": st.column_config.NumberColumn(width=85), "轉折乖離(%)": st.column_config.NumberColumn(width=95)}
    format_dict = {c: "{:.2f}" for c in df_for_display.columns if any(x in c for x in ["現價", "乖離", "報酬", "YoY", "MoM", "轉折值", "漲幅"])}
    format_dict.update({c: "{:,.0f}" for c in df_for_display.columns if any(x in c for x in ["法人", "買超", "張"])})

    st.markdown('<div class="dataframe-wrapper">', unsafe_allow_html=True)
    st.dataframe(df_for_display.style.apply(highlight_pivot_full_row, axis=1).format(format_dict, na_rep="-"), use_container_width=True, column_config=col_config)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div id="disclaimer-target" class="disclaimer-wrapper"><div class="disclaimer-header"><div class="pulse-dot-small"></div><h4 class="disclaimer-title">重要免責聲明</h4></div><ul class="disclaimer-list"><li class="disclaimer-item">1.系統篩選結果均為量化模型產出，僅供研究參考不構成投資建議.</li><li class="disclaimer-item">2.過往績效不保證未來表現，請做好自身風控本系統不負法律責任.</li></ul></div>', unsafe_allow_html=True)

st.markdown('<div class="footer-wrapper"><div class="brand-copyright">QUANTUM DATA SYSTEM © 2026</div><div class="design-container"><span class="design-tag">Developer / Design</span><span class="design-email-tech">WU.CHIACHAN@GMAIL.COM</span></div></div>', unsafe_allow_html=True)
