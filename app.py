# =============================================================================
# QUANTUM TECH SCANNER - VERSION 100.1 (後端滿血版 - 終極不斷線護城河 + H策略放寬版)
# 核心優化：修復遺失的歷史下載函數 / 融合 3 波盤中補考 / 休眠 3 秒 / FM 參數完全鎖死
# 工程優化：解除 RESULT_LOCK 死鎖瓶頸 / 優先 YF 輕量級 API / 陣列空值防呆處理
# 新增功能：策略 J (MACD 200/201/202, DMI 300, W%R 50) + 徹底解決 NaN 毒藥問題
# 新增功能：策略 K (跨週期 日/週/月 RSI, DMI, W%R, VR 矩陣 6取4)
# 新增功能：策略 L (股本法人鎖碼型，精準對齊 Goodinfo 籌碼排行)
# 終極調整：策略 M (營收創高爆發型，下修至4次，且最新單月營收必須「創歷史新高」)
# 新增調整：策略 N (投信作帳認同型，下修至實戰最甜起漲點 10日>0.5%, 20日>1%)
# 終極調整：策略 O (合約負債爆發型，嚴抓 YoY>50% + 季增 + EPS>0 + 總佔比>5%)
# 終極調整：策略 E (市場區間共振型，站上AVWAP、差距10%內、今日出量、季線正乖離<=20%)
# 最新修正：策略 H (財報三率三升型，完全移除 LTM 營收大於前12個月之限制)
# =============================================================================
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import os
import time
import requests
import sys
import gc
import threading
import concurrent.futures
import random
import logging
import warnings
from tqdm.auto import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 🚨 [手動控制台：全域掃描模式設定] 🚨
LINE_NOTIFY_TOKENS = [""]  # 👈 請在此輸入一組或多組 LINE Token

# -----------------------------------------------------------------------------
# 【設定一】歷史日K線大數據庫 (影響全市場 1700 檔的 2y 歷史 K 線)
#   True  = 強制重新下載：無視現有快取檔案，全部重新從 YF 下載 (耗時較長)。
#   False = 智能讀取：只要今天有成功下載過，就直接讀取快取檔，極大幅省時 (預設推薦)。
# -----------------------------------------------------------------------------
FORCE_RELOAD_DAILY_HISTORY = False

# -----------------------------------------------------------------------------
# 【設定二】盤中即時報價模式 (僅在 09:00~14:00 之間生效)
#   請填入以下三種模式的其中一種字串 (記得保留雙引號)：
#   "LIVE"  = 最新報價：啟動 8 核心批量極速抓取全市場「1分鐘前」最新價格，並自動存成快取檔。
#   "CACHE" = 讀取快取：跳過網路抓取，直接讀取您今天稍早存下來的盤中報價快取檔 (極速)。
#   "OFF"   = 關閉盤中：不抓即時價也不讀快取，直接當作「盤後」來進行靜態掃描。
# -----------------------------------------------------------------------------
INTRADAY_MODE = "LIVE"

# --- [自定義護城河與量能過濾門檻] ---
MIN_VOL_LOTS_ALL = 500        # 檢查近 20日 的平均日成交量，須大於此值 (單位：張)

# =============================================================================
# ⬇️ 系統變數底層映射 (請勿更動此區塊，系統會自動轉換您的設定以維持核心邏輯)
# =============================================================================
FORCE_RELOAD_PRICE = FORCE_RELOAD_DAILY_HISTORY
ENABLE_INTRADAY_LIVE_PRICE = (INTRADAY_MODE in ["LIVE", "CACHE"])
USE_CACHED_LIVE_PRICES = (INTRADAY_MODE == "CACHE")
# =============================================================================

# 🌐 [專屬 Proxy 代理清單 - 10 組火力配置]
PROXY_LIST = [
    "http://chiachan:damao0108@31.59.20.176:6754",
    "http://chiachan:damao0108@23.95.150.145:6114",
    "http://chiachan:damao0108@107.172.163.27:6543",
    "http://chiachan:damao0108@142.111.67.146:5611",
    "http://chiachan:damao0108@31.58.9.4:6077",
    "http://chiachan:damao0108@45.38.107.97:6014",
    "http://chiachan:damao0108@216.10.27.159:6837",
    "http://chiachan:damao0108@198.105.121.200:6462",
    "http://chiachan:damao0108@198.23.239.134:6540",
    "http://chiachan:damao0108@191.96.254.138:6185"
]

CURRENT_PROXY_IDX = random.randint(0, len(PROXY_LIST) - 1) if PROXY_LIST else 0

FORCE_RELOAD_INST = False
FORCE_RELOAD_REV = False
API_EXHAUSTED = False
TARGET_REV_UPDATE = []
LOCAL_IP_BANNED = False # 🌟 核心防護標記：防止本機 IP 陷入無限 429 死亡迴圈

# [系統修復] 載入完整的下市/停止交易黑名單 (158 檔終極驗證版)
DELISTED_BLACKLIST = {
    '1107', '1230', '1258', '1262', '1311', '1469', '1507', '1520', '1523', '1592',
    '1601', '1606', '1613', '1701', '1704', '1715', '1716', '1724', '1729', '1902',
    '2311', '2315', '2325', '2336', '2341', '2350', '2361', '2381', '2384', '2391',
    '2396', '2403', '2411', '2418', '2437', '2443', '2446', '2447', '2448', '2452',
    '2456', '2463', '2469', '2473', '2475', '2479', '2494', '2499', '2526', '2807',
    '2809', '2823', '2827', '2831', '2833', '2837', '2841', '2847', '2854', '2856',
    '2888', '2928', '2936', '3007', '3009', '3020', '3053', '3061', '3063', '3080',
    '3089', '3142', '3144', '3202', '3214', '3271', '3315', '3367', '3383', '3474',
    '3514', '3519', '3534', '3536', '3559', '3561', '3573', '3579', '3584', '3598',
    '3599', '3614', '3638', '3642', '3682', '3697', '3698', '4137', '4141', '4144',
    '4152', '4429', '4529', '4576', '4712', '4725', '4733', '4803', '4933', '4944',
    '4945', '4984', '5102', '5259', '5264', '5280', '5281', '5304', '5305', '5349',
    '5383', '5820', '5854', '6004', '6012', '6119', '6131', '6145', '6172', '6238',
    '6247', '6251', '6255', '6280', '6286', '6287', '6288', '6289', '6404', '6422',
    '6423', '6438', '6452', '6457', '6497', '6514', '6594', '6702', '6747', '7795',
    '8008', '8078', '8199', '8406', '8418', '8420', '8427', '8476', '8480', '8497',
    '8934', '9915', '9922'
}
EXCLUDE_IND = ['ETF', 'ETN', '存託憑證', '受益證券', '特別股']

# 🤫 靜音模式
logging.getLogger('yfinance').setLevel(logging.CRITICAL)
logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

print("\n🚀 [系統日誌] 核心引擎啟動：Version 100.1 (策略H 三率純粹版 + 策略M 創高修正)")
sys.stdout.flush()

IS_COLAB = False
try:
    from google.colab import drive, files
    drive.mount('/content/drive', force_remount=True)
    BASE_PATH = "/content/drive/MyDrive/StockQuantData"
    CACHE_DIR = "/content/drive/MyDrive/StockQuantData/cache"
    IS_COLAB = True
except:
    BASE_PATH = "."
    CACHE_DIR = "cache"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def heal_poisoned_cache():
    healed_count = 0
    try:
        for f in os.listdir(CACHE_DIR):
            f_path = os.path.join(CACHE_DIR, f)
            if f.endswith('.csv') and os.path.getsize(f_path) < 150:
                os.remove(f_path)
                healed_count += 1
        if healed_count > 0:
            print(f"🧹 [系統自癒] 已成功清除 {healed_count} 個失效的快取檔。")
    except:
        pass

heal_poisoned_cache()

FM_ACCOUNTS = [
    {"user_id": "wu.chiachan@gmail.com", "password": "damao0108"},
    {"user_id": "jarjengwu@hotmail.com", "password": "damao0108"},
    {"user_id": "chinchyau99@gmail.com", "password": "damao0108"},
    {"user_id": "wu.chiachan@yopmail.com", "password": "damao0108"},
    {"user_id": "chiachan0305@yopmail.com", "password": "damao0108"},
    {"user_id": "chiachan001@yopmail.com", "password": "damao0108"},
    {"user_id": "chiachan002@yopmail.com", "password": "damao0108"},
    {"user_id": "chiachan003@yopmail.com", "password": "damao0108"},
    {"user_id": "chiachan005@yopmail.com", "password": "damao0108"},
    {"user_id": "chiachan006@yopmail.com", "password": "damao0108"}
]

SESSION_MEMO = {}
GLOBAL_TOKEN_IDX = 0
CURRENT_DYNAMIC_TOKEN = None
CURRENT_SESSION = None  

TOKEN_LOCK = threading.Lock()
RESULT_LOCK = threading.Lock()
API_THROTTLE_LOCK = threading.Lock() 

# 🌟 極速傳奇配速：0.01 秒阻塞節流閥
BASE_THROTTLE = 0.01  
LAST_API_REQ_TIME = 0.0
API_CALL_COUNT = 0  

def get_current_public_ip(session=None):
    try:
        s = session if session else requests
        resp = s.get("https://api.ipify.org?format=json", timeout=10)
        return resp.json().get("ip", "Unknown")
    except:
        return "Unknown"

def send_multi_line_notify(message):
    if not LINE_NOTIFY_TOKENS or LINE_NOTIFY_TOKENS == [""]:
        return
    url = "https://notify-api.line.me/api/notify"
    for token in LINE_NOTIFY_TOKENS:
        if not token:
            continue
        try:
            headers = {"Authorization": f"Bearer {token}"}
            data = {"message": message}
            requests.post(url, headers=headers, data=data, timeout=10)
        except:
            pass

def perform_account_precheck():
    global FM_ACCOUNTS
    sys.stdout.write("\n>>> [進度 0/6] 啟動上帝視角額度預檢與智慧排序...\n")
    sys.stdout.flush()
    healthy_accounts = []
    
    # 🌟 修正 1：加上重試機制，放寬 timeout 時間到 15 秒，避免網路延遲誤殺
    for acc in FM_ACCOUNTS:
        success = False
        for _ in range(2):
            try:
                resp = requests.post("https://api.finmindtrade.com/api/v4/login", data={"user_id": acc["user_id"], "password": acc["password"]}, timeout=(10, 15))
                if resp.status_code == 200 and resp.json().get("status") == 200:
                    token = resp.json().get("token")
                    info_resp = requests.get("https://api.web.finmindtrade.com/v2/user_info", headers={"Authorization": f"Bearer {token}"}, params={"token": token}, timeout=(10, 15))
                    if info_resp.status_code == 200:
                        user_count = int(info_resp.json().get("user_count", 0))
                        if user_count < 555:
                            acc['remaining'] = 555 - user_count; healthy_accounts.append(acc)
                            sys.stdout.write(f"    ✅ 帳號 {acc['user_id']} | 剩餘: {acc['remaining']}\n")
                            success = True
                            break # 成功就跳出重試迴圈
                        else: 
                            sys.stdout.write(f"    ⚠️ 帳號 {acc['user_id']} | 額度已滿 ({user_count}次)，暫時剔除\n")
                            success = True # 雖然滿了但連線成功
                            break
            except Exception as e:
                time.sleep(1.0)
        
        if not success:
            sys.stdout.write(f"    ❌ 帳號 {acc['user_id']} | 測試異常或網路超時\n")
        time.sleep(0.5)
        
    healthy_accounts.sort(key=lambda x: x.get('remaining', 0), reverse=True)
    
    # 🌟 終極備援：如果全部失敗(可能是 FinMind 伺服器暫時卡住)，強制塞入第一個帳號避免系統崩潰
    if len(healthy_accounts) == 0:
        sys.stdout.write("⚠️ 警告：所有帳號預檢失敗，啟動備援機制，強制保留初始帳號進入盲掃模式！\n")
        healthy_accounts = [FM_ACCOUNTS[0]]
        
    FM_ACCOUNTS = healthy_accounts
    return len(healthy_accounts)

def build_finmind_session():
    global CURRENT_PROXY_IDX
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(pool_connections=40, pool_maxsize=40, max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    
    if PROXY_LIST:
        p = PROXY_LIST[CURRENT_PROXY_IDX % len(PROXY_LIST)]
        s.proxies = {"http": p, "https": p}
        
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]
    s.headers.update({
        'User-Agent': random.choice(ua_list),
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate'
    })
    return s

def get_token_by_idx(idx):
    global CURRENT_SESSION, API_CALL_COUNT, CURRENT_PROXY_IDX, LOCAL_IP_BANNED
    if idx >= len(FM_ACCOUNTS):
        return None
    acc = FM_ACCOUNTS[idx]
    
    if CURRENT_SESSION is not None:
        try: CURRENT_SESSION.close()
        except: pass
            
    for _ in range(3):
        try:
            if idx == 0 and not LOCAL_IP_BANNED:
                sys.stdout.write(f"\nℹ️ [提示] 首發帳號不使用 Proxy，直接本機 IP 全速連線。\n")
                original_proxy_list = PROXY_LIST.copy()
                PROXY_LIST.clear()
                new_session = build_finmind_session()
                PROXY_LIST.extend(original_proxy_list)
            elif PROXY_LIST:
                CURRENT_PROXY_IDX += 1
                sys.stdout.write(f"\n🔄 登入切換 Proxy 代理...\n")
                new_session = build_finmind_session()
            else:
                sys.stdout.write(f"\nℹ️ [提示] 尚未配置 Proxy 清單，本機 IP 連線。\n")
                new_session = build_finmind_session()

            resp = new_session.post("https://api.finmindtrade.com/api/v4/login", data={"user_id": acc["user_id"], "password": acc["password"]}, timeout=(5, 15)) # 🌟 延長 timeout
            
            if resp.status_code == 200 and resp.json().get("status") == 200:
                token = resp.json().get("token")
                info_headers = {"Authorization": f"Bearer {token}", "User-Agent": new_session.headers['User-Agent']}
                info_resp = new_session.get("https://api.web.finmindtrade.com/v2/user_info", headers=info_headers, params={"token": token}, timeout=(5, 15))
                
                if info_resp.status_code == 200:
                    API_CALL_COUNT = int(info_resp.json().get("user_count", 0))
                    sys.stdout.write(f"    🟢 帳號 {acc['user_id']} 上線 (水位: {API_CALL_COUNT} 次)\n")
                else:
                    API_CALL_COUNT = 0
                    sys.stdout.write(f"    🟢 帳號 {acc['user_id']} 上線 (水位同步失敗預設 0)\n")
                
                sys.stdout.flush()
                CURRENT_SESSION = new_session
                return token
        except Exception as e:
            sys.stdout.write(f"❌ 代理連線或切換失敗，重試...\n")
            time.sleep(1.0)
    return None

def safe_fetch_finmind(dataset, data_id=None, start_date=None, cache_type='rev'):
    global GLOBAL_TOKEN_IDX, CURRENT_DYNAMIC_TOKEN, API_CALL_COUNT, LAST_API_REQ_TIME, CURRENT_SESSION, API_EXHAUSTED, LOCAL_IP_BANNED
    if API_EXHAUSTED: return pd.DataFrame()
    if CURRENT_DYNAMIC_TOKEN is None:
        with TOKEN_LOCK:
            if CURRENT_DYNAMIC_TOKEN is None: CURRENT_DYNAMIC_TOKEN = get_token_by_idx(GLOBAL_TOKEN_IDX)
    if not CURRENT_DYNAMIC_TOKEN: return pd.DataFrame()
    
    memo_key = f"{dataset}_{data_id}_{cache_type}"
    if memo_key in SESSION_MEMO: return SESSION_MEMO[memo_key]
    cache_path = os.path.join(CACHE_DIR, f"{data_id}_{cache_type}.csv")
    is_force = FORCE_RELOAD_INST if cache_type == 'inst' else (FORCE_RELOAD_REV or data_id in TARGET_REV_UPDATE)
    
    if os.path.exists(cache_path) and not is_force:
        try:
            df = pd.read_csv(cache_path); return df
        except: pass

    retry_count = 0
    while GLOBAL_TOKEN_IDX < len(FM_ACCOUNTS) and retry_count < 3:
        with TOKEN_LOCK:
            req_token = CURRENT_DYNAMIC_TOKEN
            local_session = CURRENT_SESSION
            
        if not req_token: break

        if API_CALL_COUNT >= 550:
            with TOKEN_LOCK:
                if API_CALL_COUNT >= 550 and CURRENT_DYNAMIC_TOKEN == req_token:
                    sys.stdout.write(f"\n🛡️ 額度耗盡！切換伺服器與新帳號... (休眠 3 秒)\n")
                    time.sleep(3.0)
                    GLOBAL_TOKEN_IDX += 1
                    CURRENT_DYNAMIC_TOKEN = get_token_by_idx(GLOBAL_TOKEN_IDX)
                    if not CURRENT_DYNAMIC_TOKEN: break
                elif CURRENT_DYNAMIC_TOKEN != req_token: 
                    time.sleep(1.0)
            retry_count = 0
            continue
            
        with API_THROTTLE_LOCK:
            elapsed = time.time() - LAST_API_REQ_TIME
            if elapsed < BASE_THROTTLE: 
                time.sleep(BASE_THROTTLE - elapsed)
            LAST_API_REQ_TIME = time.time()
            API_CALL_COUNT += 1
            
        try:
            params = {"dataset": dataset, "token": req_token, "data_id": data_id, "start_date": start_date, "_t": int(time.time()*1000)}
            resp = local_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=(8, 15))
            
            if resp.status_code == 200:
                new_df = pd.DataFrame(resp.json().get("data", []))
                if not new_df.empty:
                    if os.path.exists(cache_path) and cache_type != 'fin' and cache_type != 'bs':
                        try:
                            existing_df = pd.read_csv(cache_path)
                            if cache_type == 'inst':
                                new_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['date', 'name'], keep='last').sort_values(['date', 'name'])
                            else:
                                new_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['date'], keep='last').sort_values('date')
                        except: pass
                    new_df.to_csv(cache_path, index=False, encoding='utf-8-sig'); SESSION_MEMO[memo_key] = new_df; return new_df
                
                new_df.to_csv(cache_path, index=False, encoding='utf-8-sig'); SESSION_MEMO[memo_key] = new_df; return new_df
                
            if resp.status_code == 429 or "limit" in resp.text.lower():
                with TOKEN_LOCK:
                    if CURRENT_DYNAMIC_TOKEN == req_token:
                        sys.stdout.write(f"\n⚠️ 觸發 WAF 限制！全面切換伺服器與新帳號... (休眠 3 秒)\n")
                        if GLOBAL_TOKEN_IDX == 0:
                            LOCAL_IP_BANNED = True
                        time.sleep(3.0)
                        GLOBAL_TOKEN_IDX += 1
                        CURRENT_DYNAMIC_TOKEN = get_token_by_idx(GLOBAL_TOKEN_IDX)
                        if not CURRENT_DYNAMIC_TOKEN: break
                    else: 
                        time.sleep(1.0)
                retry_count = 0
                continue
            else:
                retry_count += 1
                time.sleep(1.0)
        except:
            retry_count += 1
            time.sleep(1.0)
            
    API_EXHAUSTED = True; return pd.DataFrame()

# =============================================================================
# 🌟 [歷史日K線下載引擎] YF 8核極速批量下載 (保障 2 年期完整數據)
# =============================================================================
def fetch_yf_safe(chunk):
    time.sleep(random.uniform(0.1, 0.4))
    try:
        return chunk, yf.download(chunk, period="2y", auto_adjust=True, group_by='ticker', progress=False, threads=False)
    except:
        return chunk, pd.DataFrame()

# =============================================================================
# 🌟 [盤中即時報價引擎] YF 8核心批量下載 (極簡降維 2d 版)
# =============================================================================
def fetch_yf_safe_live(chunk):
    time.sleep(random.uniform(0.1, 0.4))
    try:
        return chunk, yf.download(chunk, period="2d", auto_adjust=True, group_by='ticker', progress=False, threads=False)
    except:
        return chunk, pd.DataFrame()

# =============================================================================
# [策略運算與數據分析邏輯]
# =============================================================================
def evaluate_tech_only(full_t, df_p, ticker_info, live_prices):
    try:
        sid = ticker_info[full_t]['sid']
        close_arr = (df_p['Close'].iloc[:, 0] if isinstance(df_p['Close'], pd.DataFrame) else df_p['Close']).values
        vol_arr = (df_p['Volume'].iloc[:, 0] if isinstance(df_p['Volume'], pd.DataFrame) else df_p['Volume']).values
        
        high_arr_j = (df_p['High'].iloc[:, 0] if isinstance(df_p['High'], pd.DataFrame) else df_p['High']).values
        low_arr_j = (df_p['Low'].iloc[:, 0] if isinstance(df_p['Low'], pd.DataFrame) else df_p['Low']).values
        
        # 🌟 核心防護一：前置抓取 YF 總股本 (避免平行運算時觸發 YF Rate Limit)
        shares_out_val = 0
        try:
            info = yf.Ticker(full_t).fast_info
            try: shares_out_val = info.shares
            except: pass
            if not shares_out_val:
                try: shares_out_val = info.market_cap / info.previous_close
                except: pass
        except: pass
        
        if sid in live_prices and live_prices[sid] > 0:
            p_live = live_prices[sid]
            close_arr = np.append(close_arr, p_live)
            vol_arr = np.append(vol_arr, vol_arr[-1] if len(vol_arr) > 0 else 0)
            
            h_live = p_live
            l_live = p_live
            try:
                info = yf.Ticker(full_t).fast_info
                if info.day_high > 0 and info.day_low > 0:
                    h_live = info.day_high
                    l_live = info.day_low
            except:
                pass
                
            high_arr_j = np.append(high_arr_j, h_live)
            low_arr_j = np.append(low_arr_j, l_live)
            
        # =============================================================================
        # 🛡️ [三層神盾自癒架構] K 線健康度 X 光機
        # =============================================================================
        if len(close_arr) >= 2:
            last_c = close_arr[-1]
            last_h = high_arr_j[-1]
            last_l = low_arr_j[-1]
            prev_c = close_arr[-2]
            
            if last_h == last_l and abs((last_c - prev_c) / prev_c) < 0.09:
                healed = False
                try:
                    info = yf.Ticker(full_t).fast_info
                    try:
                        h_info = info.day_high
                        l_info = info.day_low
                        if h_info > l_info:
                            high_arr_j[-1] = h_info
                            low_arr_j[-1] = l_info
                            healed = True
                    except: pass
                except: pass
                    
                if not healed:
                    try:
                        today_str = datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y-%m-%d')
                        df_fm_price = safe_fetch_finmind("TaiwanStockPrice", data_id=sid, start_date=today_str, cache_type='price_fix')
                        if not df_fm_price.empty:
                            today_fm = df_fm_price[df_fm_price['date'] == today_str]
                            if not today_fm.empty:
                                fm_h = float(today_fm.iloc[-1]['max'])
                                fm_l = float(today_fm.iloc[-1]['min'])
                                if fm_h > fm_l:
                                    high_arr_j[-1] = fm_h
                                    low_arr_j[-1] = fm_l
                    except: pass
        # =============================================================================
        
        c_60 = close_arr[-60:]
        c_240 = close_arr[-240:]
        v_60 = vol_arr[-60:]
        v_20 = vol_arr[-20:]
        
        p = float(close_arr[-1])
        prev_p = float(close_arr[-2])
        daily_ret = round(((p - prev_p) / prev_p) * 100, 2)
        
        ma20 = float(close_arr[-20:].mean())
        ma60 = float(c_60.mean())
        ma240 = float(c_240.mean())
        vol_60_mean = v_60.mean()
        avg_vol_240 = int(vol_arr[-240:].mean() / 1000)
        
        tech_a = (p > ma240 and ma60 > ma240)
        
        try:
            t50_60, t50_20, t50_5 = GLOBAL_T50_METRICS
        except:
            t50_60, t50_20, t50_5 = 0, 0, 0
            
        tech_b = ((p/close_arr[-60]-1) > t50_60 and (p/close_arr[-20]-1) > t50_20 and (p/close_arr[-5]-1) > t50_5)
        tech_d = True 
        
        tech_e = False
        avwap = 0
        poc = 0
        if (v_20 > (vol_60_mean * 3.0)).sum() >= 2:
            high_col = (df_p['High'].iloc[:, 0] if isinstance(df_p['High'], pd.DataFrame) else df_p['High']).values[-60:]
            low_col = (df_p['Low'].iloc[:, 0] if isinstance(df_p['Low'], pd.DataFrame) else df_p['Low']).values[-60:]
            if len(high_col) == 60: 
                tp = (high_col + low_col + c_60) / 3
                avwap = np.dot(tp, v_60) / v_60.sum()
                counts, bins = np.histogram(c_60, bins=50, weights=v_60)
                poc = (bins[np.argmax(counts)] + bins[np.argmax(counts)+1]) / 2
                
                # 🌟 策略 E (市場區間共振型) 終極修改：
                # 1. 站上季加權均價 (p >= avwap)
                # 2. AVWAP 與 POC 差距放寬至 10% 內
                # 3. 今日成交量必須大於前 5 日的均量 (出量表態)
                # 4. 現價與季線(MA60)的正乖離不超過 20%
                if p >= avwap and abs(avwap - poc) / poc <= 0.10 and float(vol_arr[-1]) > vol_arr[-6:-1].mean() and (p - ma60) / ma60 <= 0.20:
                    tech_e = True

        tech_s = False
        max_120_h = 0
        if p < ma20 * 0.9:
            high_col_s = (df_p['High'].iloc[:, 0] if isinstance(df_p['High'], pd.DataFrame) else df_p['High']).values[-120:]
            if len(high_col_s) > 0:
                max_120_h = float(high_col_s.max())
                if p < (max_120_h * 0.8) and (v_20 > (vol_60_mean * 2.0)).sum() >= 2 and (vol_arr[-10:] > vol_60_mean).sum() >= 5:
                    tech_s = True

        p_w = get_max_pivot(df_p, 'W-FRI')
        p_m = get_max_pivot(df_p, 'M')
        tech_g_double = (p > p_w and p > p_m and p_w > 0 and p_m > 0)
        
        pass_h_tech = True
        
        # =============================================================================
        # 🌟 策略 J 運算邏輯
        # =============================================================================
        tech_j = False
        j_dif = 0
        j_adx = 0
        j_wr = 0
        if len(close_arr) >= 300:
            ema1 = pd.Series(close_arr).ewm(span=200, adjust=False).mean().values
            ema2 = pd.Series(close_arr).ewm(span=201, adjust=False).mean().values
            dif = ema1 - ema2
            macd_signal = pd.Series(dif).ewm(span=202, adjust=False).mean().values
            d_m = dif - macd_signal
            
            j_dif = dif[-1]
            cond_macd = (dif[-1] > dif[-2]) and (d_m[-1] > d_m[-2]) and (ema1[-1] > ema1[-2]) and (ema2[-1] > ema2[-2])
            
            up = high_arr_j[1:] - high_arr_j[:-1]
            dn = low_arr_j[:-1] - low_arr_j[1:]
            
            pdm = np.where((up > dn) & (up > 0), up, 0)
            ndm = np.where((dn > up) & (dn > 0), dn, 0)
            
            tr1 = high_arr_j[1:] - low_arr_j[1:]
            tr2 = np.abs(high_arr_j[1:] - close_arr[:-1])
            tr3 = np.abs(low_arr_j[1:] - close_arr[:-1])
            tr = np.maximum(tr1, np.maximum(tr2, tr3))
            
            atr = pd.Series(tr).ewm(alpha=1/300, adjust=False).mean()
            atr = atr.replace(0, np.nan)
            
            pdi = 100 * pd.Series(pdm).ewm(alpha=1/300, adjust=False).mean() / atr
            ndi = 100 * pd.Series(ndm).ewm(alpha=1/300, adjust=False).mean() / atr
            
            pdi = pdi.fillna(0)
            ndi = ndi.fillna(0)
            
            dx_den = pdi + ndi
            dx_den = dx_den.replace(0, np.nan) 
            dx = 100 * np.abs(pdi - ndi) / dx_den
            dx = dx.fillna(0)
            
            adx = dx.ewm(alpha=1/300, adjust=False).mean().values
            j_adx = adx[-1]
            cond_dmi = adx[-1] > adx[-2]
            
            max_h_50 = np.max(high_arr_j[-50:])
            min_l_50 = np.min(low_arr_j[-50:])
            if max_h_50 != min_l_50:
                wr = (max_h_50 - close_arr[-1]) / (max_h_50 - min_l_50) * 100
            else:
                wr = 50
                
            j_wr = wr
            cond_wr = wr < 20
            
            tech_j = cond_macd and cond_dmi and cond_wr

        # =============================================================================
        # 🌟 策略 K 運算邏輯
        # =============================================================================
        tech_k = False
        k_pdi_val, k_rsi_m_val, k_wr_50_val, k_rsi_d_val, k_vr_w_val, k_vr_m_val = 0, 0, 0, 0, 0, 0
        cond_k1, cond_k2, cond_k3, cond_k4, cond_k5, cond_k6 = False, False, False, False, False, False
        
        idx_list = list(df_p.index)
        if len(close_arr) > len(idx_list):
            idx_list.append(pd.Timestamp(datetime.datetime.now().date()))
        
        df_temp = pd.DataFrame({
            'High': high_arr_j,
            'Low': low_arr_j,
            'Close': close_arr,
            'Volume': vol_arr
        }, index=idx_list)
        
        df_w = df_temp.resample('W-FRI').agg({'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
        df_m = df_temp.resample('ME').agg({'High':'max', 'Low':'min', 'Close':'last', 'Volume':'sum'}).dropna()
        
        if len(df_m) >= 2:
            high_m = df_m['High'].values
            low_m = df_m['Low'].values
            close_m = df_m['Close'].values
            up_m = high_m[1:] - high_m[:-1]
            dn_m = low_m[:-1] - low_m[1:]
            pdm_m = np.where((up_m > dn_m) & (up_m > 0), up_m, 0)
            tr1_m = high_m[1:] - low_m[1:]
            tr2_m = np.abs(high_m[1:] - close_m[:-1])
            tr3_m = np.abs(low_m[1:] - close_m[:-1])
            tr_m = np.maximum(tr1_m, np.maximum(tr2_m, tr3_m))
            tr_m_last = tr_m[-1]
            if tr_m_last > 0: k_pdi_val = (pdm_m[-1] / tr_m_last) * 100
            else: k_pdi_val = 0
            cond_k1 = k_pdi_val > 50
            
        if len(df_m) >= 5:
            delta_m = df_m['Close'].diff().dropna()
            gain_m = delta_m.where(delta_m > 0, 0); loss_m = -delta_m.where(delta_m < 0, 0)
            avg_gain_m = gain_m.ewm(alpha=1/4, adjust=False).mean()
            avg_loss_m = loss_m.ewm(alpha=1/4, adjust=False).mean()
            rs_m = avg_gain_m / avg_loss_m
            rsi_m_4 = 100 - (100 / (1 + rs_m))
            k_rsi_m_val = rsi_m_4.iloc[-1]
            cond_k2 = k_rsi_m_val > 77

        if len(close_arr) >= 50:
            max_h_50 = np.max(high_arr_j[-50:]); min_l_50 = np.min(low_arr_j[-50:])
            if max_h_50 != min_l_50: k_wr_50_val = (max_h_50 - close_arr[-1]) / (max_h_50 - min_l_50) * 100
            else: k_wr_50_val = 50
            cond_k3 = k_wr_50_val < 20

        if len(close_arr) >= 61:
            delta_d = pd.Series(close_arr).diff().dropna()
            gain_d = delta_d.where(delta_d > 0, 0); loss_d = -delta_d.where(delta_d < 0, 0)
            avg_gain_d = gain_d.ewm(alpha=1/60, adjust=False).mean()
            avg_loss_d = loss_d.ewm(alpha=1/60, adjust=False).mean()
            rs_d = avg_gain_d / avg_loss_d
            rsi_d_60 = 100 - (100 / (1 + rs_d))
            k_rsi_d_val = rsi_d_60.iloc[-1]
            cond_k4 = k_rsi_d_val > 57

        if len(df_w) >= 3:
            diff_w = df_w['Close'].diff().fillna(0)
            up_v_sum = df_w['Volume'].where(diff_w > 0, 0).rolling(2).sum().iloc[-1]
            dn_v_sum = df_w['Volume'].where(diff_w < 0, 0).rolling(2).sum().iloc[-1]
            flat_v_sum = df_w['Volume'].where(diff_w == 0, 0).rolling(2).sum().iloc[-1]
            num_w = up_v_sum + 0.5 * flat_v_sum; den_w = dn_v_sum + 0.5 * flat_v_sum
            if den_w > 0: k_vr_w_val = (num_w / den_w) * 100
            else: k_vr_w_val = 9999 if num_w > 0 else 0
            cond_k5 = k_vr_w_val > 9998
            
        if len(df_m) >= 3:
            diff_m = df_m['Close'].diff().fillna(0)
            up_v_sum_m = df_m['Volume'].where(diff_m > 0, 0).rolling(2).sum().iloc[-1]
            dn_v_sum_m = df_m['Volume'].where(diff_m < 0, 0).rolling(2).sum().iloc[-1]
            flat_v_sum_m = df_m['Volume'].where(diff_m == 0, 0).rolling(2).sum().iloc[-1]
            num_m = up_v_sum_m + 0.5 * flat_v_sum_m; den_m = dn_v_sum_m + 0.5 * flat_v_sum_m
            if den_m > 0: k_vr_m_val = (num_m / den_m) * 100
            else: k_vr_m_val = 9999 if num_m > 0 else 0
            cond_k6 = k_vr_m_val > 9998

        k_conditions_met = sum([cond_k1, cond_k2, cond_k3, cond_k4, cond_k5, cond_k6])
        if k_conditions_met >= 4:
            tech_k = True

        if any([tech_a, tech_b, tech_d, tech_e, tech_s, tech_g_double, pass_h_tech, tech_j, tech_k]):
            name = ticker_info[full_t]['name']
            ind = ticker_info[full_t]['ind']
            
            cand_data = {
                'sid': sid, 'full_t': full_t, 'name': name, 'ind': ind, 'p': round(p,2), 'prev_p': round(prev_p, 2), 'daily_ret': daily_ret,
                'ma60': ma60, 'ma240': ma240, 'ma20': ma20, 'vol_60_mean': vol_60_mean, 'avg_vol_240': avg_vol_240, 'p_w': p_w, 'p_m': p_m,
                'tech_a': tech_a, 'tech_b': tech_b, 'tech_d': tech_d, 'tech_e': tech_e, 'tech_s': tech_s, 'tech_g_double': tech_g_double,
                'pass_h_tech': pass_h_tech, 'tech_j': tech_j, 'tech_k': tech_k, 'j_dif': j_dif, 'j_adx': j_adx, 'j_wr': j_wr,
                'k_pdi_val': k_pdi_val, 'k_rsi_m_val': k_rsi_m_val, 'k_wr_50_val': k_wr_50_val, 'k_rsi_d_val': k_rsi_d_val,
                'k_vr_w_val': k_vr_w_val, 'k_vr_m_val': k_vr_m_val,
                'shares_out_val': shares_out_val  # 🌟 傳遞核心防護抓取的股本
            }
            if tech_e: cand_data.update({'avwap': avwap, 'poc': poc, 'vol_20_max': float(v_20.max())})
            if tech_s: cand_data['max_120_h'] = max_120_h
            return cand_data
    except: pass
    return None

def check_refined_fundamentals(sid):
    df_raw = safe_fetch_finmind("TaiwanStockMonthRevenue", data_id=sid, start_date="2002-02-01", cache_type='rev')
    mom = 0; yoy = 0; ytd_yoy = 0; ok = False; ok_squat = False; high_count = 0; is_latest_ath = False
    if not df_raw.empty and 'revenue' in df_raw.columns:
        try:
            df_raw['revenue'] = pd.to_numeric(df_raw['revenue'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            df = df_raw.copy(); rev = df['revenue'].values; total = len(rev)
            if total >= 24:
                mom = round(((rev[-1] - rev[-2]) / rev[-2]) * 100, 2) if rev[-2] != 0 else 0
                yoy = round(((rev[-1] - rev[-13]) / rev[-13]) * 100, 2) if rev[-13] != 0 else 0
                df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
                latest_y = df['date'].dt.year.iloc[-1]; latest_m = df['date'].dt.month.iloc[-1]
                cur_ytd = df[(df['date'].dt.year == latest_y) & (df['date'].dt.month <= latest_m)]['revenue'].sum()
                last_ytd = df[(df['date'].dt.year == latest_y - 1) & (df['date'].dt.month <= latest_m)]['revenue'].sum()
                ytd_yoy = round(((cur_ytd - last_ytd) / last_ytd) * 100, 2) if last_ytd > 0 else 0
                ltm_series = pd.Series(rev).rolling(window=12).sum().values
                is_ltm_high = (ltm_series[-1] >= np.nanmax(ltm_series[-13::-12]))
                recent_3m = np.sum(rev[-3:]); last_year_3m = np.sum(rev[-15:-12])
                is_3m_yoy_growth = (recent_3m > last_year_3m)
                second_highest_idx = np.argsort(rev)[-2]; is_second_high_recent = (second_highest_idx >= (total - 12))
                if is_ltm_high and is_3m_yoy_growth and (np.argmax(rev) >= (total-6)) and is_second_high_recent and (ytd_yoy > 10): ok = True
                if ytd_yoy > 0 and is_ltm_high: ok_squat = True
                
                # ==========================================
                # 🌟 策略 M 最新修改邏輯
                # 1. 過去 12 個月內創高次數
                # 2. 最新一個月營收必須創下歷史新高
                # ==========================================
                for i in range(total - 12, total):
                    if i > 0 and len(rev[:i]) > 0 and rev[i] > np.nanmax(rev[:i]): 
                        high_count += 1
                if total > 1 and len(rev[:-1]) > 0:
                    if rev[-1] > np.nanmax(rev[:-1]): 
                        is_latest_ath = True
        except: pass
    return ok, mom, yoy, ytd_yoy, ok_squat, high_count, is_latest_ath

def check_financial_margin_growth(sid):
    fetch_days = max(1000, int(2 * 120 + 365))
    df = safe_fetch_finmind("TaiwanStockFinancialStatements", data_id=sid, start_date=(datetime.datetime.now()-datetime.timedelta(days=fetch_days)).strftime('%Y-%m-%d'), cache_type='fin')
    is_h, metrics = False, {"最新毛利率(%)": 0, "最新營利率(%)": 0, "最新淨利率(%)": 0}
    if not df.empty and 'type' in df.columns and 'value' in df.columns:
        try:
            df['value'] = pd.to_numeric(df['value'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            df = df.drop_duplicates(subset=['date', 'type'], keep='last')
            pivot = df.pivot(index='date', columns='type', values='value').sort_index()
            rev_col = 'Revenue' if 'Revenue' in pivot.columns else ('OperatingRevenue' if 'OperatingRevenue' in pivot.columns else None)
            gp_col = 'GrossProfit' if 'GrossProfit' in pivot.columns else None
            op_col = 'OperatingIncome' if 'OperatingIncome' in pivot.columns else None
            ni_col = 'IncomeAfterTaxes' if 'IncomeAfterTaxes' in pivot.columns else ('NetIncome' if 'NetIncome' in pivot.columns else None)
            if rev_col and gp_col and op_col and ni_col:
                pivot[rev_col] = pd.to_numeric(pivot[rev_col], errors='coerce')
                pivot[gp_col] = pd.to_numeric(pivot[gp_col], errors='coerce'); pivot[op_col] = pd.to_numeric(pivot[op_col], errors='coerce'); pivot[ni_col] = pd.to_numeric(pivot[ni_col], errors='coerce')
                pivot = pivot[pivot[rev_col] > 0]
                pivot['g_margin'] = pivot[gp_col] / pivot[rev_col] * 100; pivot['o_margin'] = pivot[op_col] / pivot[rev_col] * 100; pivot['n_margin'] = pivot[ni_col] / pivot[rev_col] * 100
                valid_df = pivot[['g_margin', 'o_margin', 'n_margin']].replace([np.inf, -np.inf], np.nan).dropna()
                if len(valid_df) >= 3:
                    g_arr = valid_df['g_margin'].values; o_arr = valid_df['o_margin'].values; n_arr = valid_df['n_margin'].values
                    cond_g = all(g_arr[-(i)] > g_arr[-(i+1)] for i in range(1, 3)); cond_o = all(o_arr[-(i)] > o_arr[-(i+1)] for i in range(1, 3)); cond_n = all(n_arr[-(i)] > n_arr[-(i+1)] for i in range(1, 3))
                    if cond_g and cond_o and cond_n and n_arr[-1] > 0: is_h = True; metrics = {"最新毛利率(%)": round(g_arr[-1], 2), "最新營利率(%)": round(o_arr[-1], 2), "最新淨利率(%)": round(n_arr[-1], 2)}
        except: pass
    return is_h, metrics

def check_ltm_revenue(sid):
    # 🌟 策略 H 最新修改邏輯：僅保留抓取資料與長度判斷，移除 LTM > 前 12 個月的營收成長限制
    df = safe_fetch_finmind("TaiwanStockMonthRevenue", data_id=sid, start_date=(datetime.datetime.now()-datetime.timedelta(days=1095)).strftime('%Y-%m-%d'), cache_type='rev')
    is_pass, ltm_yoy = False, 0
    if not df.empty and 'revenue' in df.columns and 'date' in df.columns:
        try:
            df['revenue'] = pd.to_numeric(df['revenue'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            df['date'] = pd.to_datetime(df['date']); df = df.sort_values('date'); rev = df['revenue'].values
            
            # 只要有足夠的 24 個月歷史營收數據，就直接放行，不再卡 LTM 成長
            if len(rev) >= 24:
                ltm = np.sum(rev[-12:]); prev_ltm = np.sum(rev[-24:-12])    
                if prev_ltm > 0: ltm_yoy = ((ltm - prev_ltm) / prev_ltm) * 100
                is_pass = True 
        except: pass
    return is_pass, round(ltm_yoy, 2)

def get_max_pivot(df, timeframe):
    try:
        rule = 'ME' if timeframe == 'M' else timeframe
        p = df['Close'].resample(rule).last().dropna().values
        if len(p) < 7: return 0
        return round(max(2*p[-4]-p[-7], 2*p[-3]-p[-6], 2*p[-2]-p[-5]), 2)
    except: return 0

def get_all_inst_metrics(sid):
    df = safe_fetch_finmind("TaiwanStockInstitutionalInvestorsBuySell", data_id=sid, start_date=(datetime.datetime.now()-datetime.timedelta(days=120)).strftime('%Y-%m-%d'), cache_type='inst')
    net_20, net_10, net_5, is_climax = 0, 0, 0, False
    sitc_20, sitc_10, sitc_5 = 0, 0, 0
    d_m = {"20日法人淨買(張)": 0}
    if not df.empty and 'buy' in df.columns:
        df = df.copy()
        df['net_buy'] = pd.to_numeric(df['buy'], errors='coerce').fillna(0) - pd.to_numeric(df['sell'], errors='coerce').fillna(0)
        daily_net = df[~df['name'].isin(['三大法人', 'Total'])].groupby('date')['net_buy'].sum().reset_index().sort_values('date')
        
        last_20_dates = daily_net['date'].tail(20).values if len(daily_net) > 0 else []
        last_10_dates = daily_net['date'].tail(10).values if len(daily_net) > 0 else []
        last_5_dates = daily_net['date'].tail(5).values if len(daily_net) > 0 else []
        
        if len(daily_net) > 0:
            net_20 = int(daily_net['net_buy'].tail(20).sum() / 1000); net_10 = int(daily_net['net_buy'].tail(10).sum() / 1000); net_5 = int(daily_net['net_buy'].tail(5).sum() / 1000)
            daily_net_60 = daily_net.tail(60).copy()
            if len(daily_net_60) >= 5: 
                n60 = daily_net_60['net_buy'].sum(); n20 = daily_net_60['net_buy'].tail(20).sum(); n5 = daily_net_60['net_buy'].tail(5).sum()
                cum_net_60 = daily_net_60['net_buy'].cumsum()
                climax_60d = (cum_net_60.tail(5).max() >= cum_net_60.max()) if len(cum_net_60) > 0 else False
                if (n60 / 1000) >= 10000 and n20 > 0 and n5 > 0 and (n60 > n20 > n5):
                    if climax_60d: is_climax = True; d_m["20日法人淨買(張)"] = int(n20 / 1000)
        
        df_sitc = df[df['name'].str.contains('Investment|投信', case=False, na=False)].groupby('date')['net_buy'].sum().reset_index()
        sitc_merged = pd.merge(daily_net[['date']], df_sitc, on='date', how='left').fillna(0).sort_values('date') 
        
        sitc_20 = int(sitc_merged['net_buy'].tail(20).sum() / 1000)
        sitc_10 = int(sitc_merged['net_buy'].tail(10).sum() / 1000)
        sitc_5 = int(sitc_merged['net_buy'].tail(5).sum() / 1000)
                        
    return net_20, net_10, net_5, is_climax, d_m, sitc_20, sitc_10, sitc_5

# =============================================================================
# 🌟 策略 O 專屬引擎：合約負債與獲利計算 (嚴抓 YoY>50% + 季增 + EPS>0 + 總佔比>5%)
# =============================================================================
def check_strategy_o(sid, fallback_shares_out_value):
    fetch_days = max(1500, int(365 * 4))
    
    df_fin = safe_fetch_finmind("TaiwanStockFinancialStatements", data_id=sid, start_date=(datetime.datetime.now()-datetime.timedelta(days=fetch_days)).strftime('%Y-%m-%d'), cache_type='fin')
    df_bs = safe_fetch_finmind("TaiwanStockBalanceSheet", data_id=sid, start_date=(datetime.datetime.now()-datetime.timedelta(days=fetch_days)).strftime('%Y-%m-%d'), cache_type='bs')
    
    is_o = False
    metrics = {}
    
    dfs = []
    if not df_fin.empty: dfs.append(df_fin)
    if not df_bs.empty: dfs.append(df_bs)
    
    if dfs:
        try:
            df = pd.concat(dfs, ignore_index=True)
            if 'type' in df.columns and 'value' in df.columns:
                df['value'] = pd.to_numeric(df['value'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
                if 'origin_name' not in df.columns: df['origin_name'] = ""
                type_lower = df['type'].astype(str).str.lower()
                origin_lower = df['origin_name'].astype(str).str.lower()
                
                cl_mask = type_lower.str.contains('contract|advance') | origin_lower.str.contains('合約|預收')
                df_cl = df[cl_mask].groupby('date')['value'].sum().sort_index()
                df_cl = df_cl[df_cl > 0]
                
                if len(df_cl) >= 2:
                    df_cl.index = pd.to_datetime(df_cl.index)
                    q0_date = df_cl.index[-1]
                    q0_cl = float(df_cl.iloc[-1])
                    q1_cl = float(df_cl.iloc[-2])
                    
                    target_q4_date = q0_date - pd.DateOffset(years=1)
                    time_diffs = abs(df_cl.index - target_q4_date)
                    
                    time_diff_array = time_diffs.values
                    min_diff_idx = np.argmin(time_diff_array)
                    min_diff_days = pd.Timedelta(time_diff_array[min_diff_idx]).days
                    
                    q4_cl = 0
                    if min_diff_days <= 45:
                        q4_cl = float(df_cl.iloc[min_diff_idx])
                    elif len(df_cl) >= 5:
                        q4_cl = float(df_cl.iloc[-5])
                        
                    q0_eps = 0
                    eps_mask = type_lower.str.contains('eps|earningspershare') | origin_lower.str.contains('每股盈餘')
                    df_eps = df[eps_mask].groupby('date')['value'].last().sort_index()
                    if not df_eps.empty:
                        q0_eps = float(df_eps.iloc[-1])

                    capital = 0
                    cap_mask = type_lower.isin(['ordinaryshare', 'sharecapital']) 
                    df_cap = df[cap_mask].groupby('date')['value'].last().sort_index()
                    
                    if not df_cap.empty:
                        capital = float(df_cap.iloc[-1])
                        
                    if capital < 1000000:
                        capital = (fallback_shares_out_value * 10.0) if fallback_shares_out_value else 0
                        
                    if q0_cl > 0 and q4_cl >= 0:
                        yoy_growth = (q0_cl - q4_cl) / q4_cl if q4_cl > 0 else 999.0
                        
                        liab_to_cap_ratio = 0
                        total_liab_to_cap_ratio = 0
                        if capital > 0:
                            added_liab = q0_cl - q4_cl
                            liab_to_cap_ratio = added_liab / capital
                            total_liab_to_cap_ratio = q0_cl / capital
                            
                            if 0 < liab_to_cap_ratio < 0.005 and added_liab > 1000 and capital > 1e9:
                                liab_to_cap_ratio = (added_liab * 1000) / capital
                                total_liab_to_cap_ratio = (q0_cl * 1000) / capital
                        
                        cond_yoy = (yoy_growth >= 0.50)
                        cond_qoq = (q0_cl > q1_cl)
                        cond_eps = (q0_eps > 0)
                        cond_total_ratio = (total_liab_to_cap_ratio >= 0.05)
                        
                        if cond_yoy and cond_qoq and cond_eps and cond_total_ratio:
                            is_o = True
                            metrics = {
                                "合約負債YoY(%)": round(yoy_growth * 100, 2) if yoy_growth != 999.0 else 999.99,
                                "增額佔股本(%)": round(liab_to_cap_ratio * 100, 2) if capital > 0 else 0.0,
                                "總佔比(%)": round(total_liab_to_cap_ratio * 100, 2) if capital > 0 else 0.0,
                                "最新季EPS": round(q0_eps, 2)
                            }
        except Exception as e:
            pass
    return is_o, metrics

# =============================================================================
# 🔥 [階段二] 零浪費延遲求值引擎
# =============================================================================
final_1, final_2, final_d, final_e, final_squat, final_g_double, final_h_triple, final_j, final_k, final_l, final_m, final_n, final_o = [], [], [], [], [], [], [], [], [], [], [], [], []

def process_api_candidate(cand):
    sid = cand['sid']; pass_a, pass_b, pass_d, pass_e, pass_s, pass_g, pass_h, pass_l, pass_m, pass_n, pass_o = [False]*11
    needs_rev_check = True 
    ok, mom, yoy, ytd, ok_s, high_count, is_latest_ath = False, 0, 0, 0, False, 0, False
    if needs_rev_check:
        ok, mom, yoy, ytd, ok_s, high_count, is_latest_ath = check_refined_fundamentals(sid)
        pass_a = cand['tech_a'] and ok; pass_s = cand['tech_s'] and ok_s; 
        
        # 🌟 策略 M 條件升級判定：創高 >= 4 次 且 最新月是歷史新高
        pass_m = (high_count >= 4) and is_latest_ath 
        
    needs_inst_check = cand['tech_b'] or cand['tech_d'] or True # 🌟 強制進入以支援策略 N (投信)
    net_20, net_10, net_5, is_climax, d_m, sitc_20, sitc_10, sitc_5 = [0]*3 + [False] + [{}] + [0]*3
    if needs_inst_check:
        net_20, net_10, net_5, is_climax, d_m, sitc_20, sitc_10, sitc_5 = get_all_inst_metrics(sid)
        pass_b = cand['tech_b']; pass_d = cand['tech_d'] and is_climax
        
        # 🌟 核心防護二：讀取前置抓取的安全股本，避免在此觸發 YF Rate Limit
        shares_out_value = cand.get('shares_out_val', 0) 

        # 🌟 策略 L (法人合計)
        if net_5 > 0 and net_10 > net_5 and net_20 > net_10:
            if not shares_out_value: # 終極備援
                try:
                    ticker_obj = yf.Ticker(cand['full_t'])
                    shares_out_value = ticker_obj.info.get('sharesOutstanding')
                except: pass
            
            if shares_out_value and shares_out_value > 0:
                l_shares_out = shares_out_value / 1000.0; l_ratio_10 = net_10 / l_shares_out; l_ratio_20 = net_20 / l_shares_out 
                if l_ratio_10 > 0.01 and l_ratio_20 > 0.02: pass_l = True; cand.update({'l_shares_out': l_shares_out, 'l_ratio_5': net_5/l_shares_out, 'l_ratio_10': l_ratio_10, 'l_ratio_20': l_ratio_20, 'net_10': net_10, 'net_5': net_5})

        # 🌟 策略 N (投信作帳認同)
        if sitc_20 >= sitc_10 and sitc_10 >= sitc_5 and sitc_5 > 0:
            if not shares_out_value: # 終極備援
                try:
                    ticker_obj = yf.Ticker(cand['full_t'])
                    shares_out_value = ticker_obj.info.get('sharesOutstanding')
                except: pass
                
            if shares_out_value and shares_out_value > 0:
                o_shares_out = shares_out_value / 1000.0
                sitc_ratio_5 = sitc_5 / o_shares_out
                sitc_ratio_10 = sitc_10 / o_shares_out
                sitc_ratio_20 = sitc_20 / o_shares_out

                if sitc_ratio_5 > 0 and sitc_ratio_10 > 0.005 and sitc_ratio_20 > 0.01:
                    pass_n = True
                    cand.update({
                        'sitc_5': sitc_5, 'sitc_10': sitc_10, 'sitc_20': sitc_20,
                        'sitc_ratio_5': sitc_ratio_5, 'sitc_ratio_10': sitc_ratio_10, 'sitc_ratio_20': sitc_ratio_20
                    })

    # 🌟 策略 O 獨立強制運算，不受外部 YF 失敗影響
    shares_out_value = cand.get('shares_out_val', 0)
    if not shares_out_value:
        try:
            ticker_obj = yf.Ticker(cand['full_t'])
            shares_out_value = ticker_obj.info.get('sharesOutstanding')
            if not shares_out_value:
                mc = getattr(ticker_obj.fast_info, 'market_cap', None)
                pc = getattr(ticker_obj.fast_info, 'previous_close', None)
                if mc and pc and pc > 0: shares_out_value = mc / pc
        except: pass
        
    pass_o_temp, o_metrics = check_strategy_o(sid, shares_out_value)
    if pass_o_temp:
        pass_o = True
        cand.update(o_metrics)

    is_h, h_metrics, ltm_yoy = False, {}, 0
    if cand.get('pass_h_tech', True):
        pass_rev_h, ltm_yoy = check_ltm_revenue(sid)
        if pass_rev_h: is_h, h_metrics = check_financial_margin_growth(sid); pass_h = is_h

    pass_e = cand['tech_e']; pass_g = cand['tech_g_double']; pass_j = cand.get('tech_j', False); pass_k = cand.get('tech_k', False)
    
    is_winner = any([pass_a, pass_b, pass_d, pass_e, pass_s, pass_g, pass_h, pass_j, pass_k, pass_l, pass_m, pass_n, pass_o])
    if not is_winner: return
    
    common_data = {
        "代號": sid, "名稱": cand['name'], "產業": cand['ind'], "現價": cand['p'], "漲幅(%)": cand['daily_ret'], 
        "季乖離(%)": round(((cand['p']-cand['ma60'])/cand['ma60'])*100,2), "年乖離(%)": round(((cand['p']-cand['ma240'])/cand['ma240'])*100,2), 
        "月營收MoM(%)": mom, "月營收YoY(%)": yoy, "今年營收YoY(%)": ytd, "20日法人買賣超(張)": net_20, "轉折值": cand['p_w'],
        "基準價": cand.get('prev_p', cand['p']), "基準MA60": round(cand['ma60'], 2), "基準MA240": round(cand['ma240'], 2)
    }
    
    data_to_append = {}
    if pass_a: data_to_append['1'] = common_data.copy()
    if pass_b: b_data = common_data.copy(); b_data["5日法人買賣超(張)"] = net_5; data_to_append['2'] = b_data
    if pass_d: d_data = common_data.copy(); d_data["20日法人買賣超(張)"] = d_m["20日法人淨買(張)"]; data_to_append['d'] = d_data
    if pass_e: e_data = common_data.copy(); e_data.update({"季度成本(AVWAP)": round(cand['avwap'], 2), "共振程度(%)": round(abs(cand['avwap'] - cand['poc']) / cand['poc'] * 100, 2) if cand['poc'] != 0 else 0, "20日內最大量(倍)": round(cand['vol_20_max'] / cand['vol_60_mean'], 2) if cand['vol_60_mean'] != 0 else 0}); data_to_append['e'] = e_data
    if pass_s: s_data = common_data.copy(); s_data.update({"MA負乖離(%)": round((cand['p']/cand['ma20']-1)*100, 2), "回檔深度(%)": round((cand['p']/cand['max_120_h']-1)*100, 2)}); data_to_append['s'] = s_data
    if pass_g: g2_data = common_data.copy(); g2_data.update({"週轉折值": cand['p_w'], "月轉折值": cand['p_m']}); data_to_append['g'] = g2_data
    if pass_h: h_data = common_data.copy(); data_to_append['h'] = h_data
    if pass_j: j_data = common_data.copy(); j_data.update({"dif值": round(cand.get('j_dif', 0), 4), "ADX300值": round(cand.get('j_adx', 0), 2), "威廉50值": round(cand.get('j_wr', 0), 2)}); data_to_append['j'] = j_data
    if pass_k: k_data = common_data.copy(); k_data.update({"月線+DI(1)": round(cand.get('k_pdi_val', 0), 2), "月線RSI(4)": round(cand.get('k_rsi_m_val', 0), 2), "日線威廉(50)": round(cand.get('k_wr_50_val', 0), 2), "日線RSI(60)": round(cand.get('k_rsi_d_val', 0), 2), "週線VR(2)": round(cand.get('k_vr_w_val', 0), 2), "月線VR(2)": round(cand.get('k_vr_m_val', 0), 2)}); data_to_append['k'] = k_data
    if pass_l: l_data = common_data.copy(); l_data.update({"發行張數(萬)": round(cand.get('l_shares_out', 0) / 10, 2), "5日法人買賣超(張)": cand.get('net_5', net_5), "5日吃貨比例(%)": round(cand.get('l_ratio_5', 0) * 100, 2), "10日法人買賣超(張)": cand.get('net_10', net_10), "10日吃貨比例(%)": round(cand.get('l_ratio_10', 0) * 100, 2), "20日吃貨比例(%)": round(cand.get('l_ratio_20', 0) * 100, 2)}); data_to_append['l'] = l_data
    if pass_m: m_data = common_data.copy(); m_data.update({"近一年創高次數": high_count}); data_to_append['m'] = m_data
    if pass_n: 
        n_data = common_data.copy(); 
        n_data.update({
            "投信5日買超(張)": cand.get('sitc_5', 0), "投信5日股本比(%)": round(cand.get('sitc_ratio_5', 0) * 100, 2), 
            "投信10日買超(張)": cand.get('sitc_10', 0), "投信10日股本比(%)": round(cand.get('sitc_ratio_10', 0) * 100, 2), 
            "投信20日買超(張)": cand.get('sitc_20', 0), "投信20日股本比(%)": round(cand.get('sitc_ratio_20', 0) * 100, 2)
        })
        data_to_append['n'] = n_data
    if pass_o:
        o_data = common_data.copy()
        o_data.update({
            "合約負債YoY(%)": cand.get("合約負債YoY(%)", 0),
            "增額佔股本(%)": cand.get("增額佔股本(%)", 0),
            "總佔比(%)": cand.get("總佔比(%)", 0), 
            "最新季EPS": cand.get("最新季EPS", 0)
        })
        data_to_append['o'] = o_data

    with RESULT_LOCK:
        if '1' in data_to_append: final_1.append(data_to_append['1'])
        if '2' in data_to_append: final_2.append(data_to_append['2'])
        if 'd' in data_to_append: final_d.append(data_to_append['d'])
        if 'e' in data_to_append: final_e.append(data_to_append['e'])
        if 's' in data_to_append: final_squat.append(data_to_append['s'])
        if 'g' in data_to_append: final_g_double.append(data_to_append['g'])
        if 'h' in data_to_append: final_h_triple.append(data_to_append['h'])
        if 'j' in data_to_append: final_j.append(data_to_append['j'])
        if 'k' in data_to_append: final_k.append(data_to_append['k'])
        if 'l' in data_to_append: final_l.append(data_to_append['l'])
        if 'm' in data_to_append: final_m.append(data_to_append['m'])
        if 'n' in data_to_append: final_n.append(data_to_append['n'])
        if 'o' in data_to_append: final_o.append(data_to_append['o'])

    for k in [f"TaiwanStockMonthRevenue_{sid}_rev", f"TaiwanStockInstitutionalInvestorsBuySell_{sid}_inst", f"TaiwanStockFinancialStatements_{sid}_fin", f"TaiwanStockBalanceSheet_{sid}_bs"]: SESSION_MEMO.pop(k, None)

def run_full_pipeline():
    global GLOBAL_T50_METRICS, API_CALL_COUNT, CURRENT_SESSION
    now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    
    is_intraday = (now_taipei.weekday() < 5) and (9 <= now_taipei.hour < 14) and ENABLE_INTRADAY_LIVE_PRICE
    
    sys.stdout.write("\n>>> [進度 0/6] 啟動上帝視角額度預檢與智慧排序...\n")
    sys.stdout.flush()
    global FM_ACCOUNTS
    healthy_accounts = []
    
    for acc in FM_ACCOUNTS:
        success = False
        for _ in range(2):
            try:
                resp = requests.post("https://api.finmindtrade.com/api/v4/login", data={"user_id": acc["user_id"], "password": acc["password"]}, timeout=(10, 15))
                if resp.status_code == 200 and resp.json().get("status") == 200:
                    token = resp.json().get("token")
                    info_resp = requests.get("https://api.web.finmindtrade.com/v2/user_info", headers={"Authorization": f"Bearer {token}"}, params={"token": token}, timeout=(10, 15))
                    if info_resp.status_code == 200:
                        user_count = int(info_resp.json().get("user_count", 0))
                        if user_count < 555:
                            acc['remaining'] = 555 - user_count; healthy_accounts.append(acc)
                            sys.stdout.write(f"    ✅ 帳號 {acc['user_id']} | 剩餘: {acc['remaining']}\n")
                            success = True
                            break
                        else: 
                            sys.stdout.write(f"    ⚠️ 帳號 {acc['user_id']} | 額度已滿 ({user_count}次)，暫時剔除\n")
                            success = True
                            break
            except Exception as e:
                time.sleep(1.0)
        
        if not success:
            sys.stdout.write(f"    ❌ 帳號 {acc['user_id']} | 測試異常或網路超時\n")
        time.sleep(0.5)
        
    healthy_accounts.sort(key=lambda x: x.get('remaining', 0), reverse=True)
    
    if len(healthy_accounts) == 0:
        sys.stdout.write("⚠️ 警告：所有帳號預檢失敗，啟 কালী備援機制，強制保留初始帳號進入盲掃模式！\n")
        healthy_accounts = [FM_ACCOUNTS[0]]
        
    FM_ACCOUNTS = healthy_accounts
    
    data_0050 = pd.DataFrame()
    for _ in range(3):
        try:
            data_0050 = yf.download('0050.TW', period="2y", auto_adjust=True, progress=False)
            if not data_0050.empty: break
        except: pass
        time.sleep(1.0)
    try:
        tw50 = data_0050['Close'].dropna().values
        GLOBAL_T50_METRICS = ((tw50[-1]/tw50[-240]-1), (tw50[-1]/tw50[-60]-1), (tw50[-1]/tw50[-20]-1)) if len(tw50) >= 240 else (0, 0, 0)
    except: GLOBAL_T50_METRICS = (0, 0, 0)

    cache_path = os.path.join(CACHE_DIR, "TaiwanStockInfo_Global.csv"); pool_raw = pd.DataFrame()
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) / (24 * 3600) < 30:
        try: pool_raw = pd.read_csv(cache_path, dtype={'stock_id': str})
        except: pass
    if pool_raw.empty:
        for _ in range(3):
            temp_token = get_token_by_idx(0)
            if not temp_token: break
            try:
                resp = CURRENT_SESSION.get("https://api.finmindtrade.com/api/v4/data", params={"dataset": "TaiwanStockInfo", "token": temp_token}, timeout=(10, 20))
                data_list = resp.json().get("data", [])
                if data_list: pool_raw = pd.DataFrame(data_list); pool_raw.to_csv(cache_path, index=False, encoding='utf-8-sig'); break
            except: pass
            time.sleep(2.0)
            
    if pool_raw.empty:
        if os.path.exists(cache_path):
             sys.stdout.write("⚠️ 無法獲取最新股票清單，強制使用過期快取繼續執行！\n")
             try: pool_raw = pd.read_csv(cache_path, dtype={'stock_id': str})
             except: return
        else:
             return
    
    pool = pool_raw[(pool_raw['stock_id'].astype(str).str.isnumeric()) & (pool_raw['stock_id'].astype(str).str.len() == 4) & ((~pool_raw['industry_category'].isin(EXCLUDE_IND)) | (pool_raw['stock_id'].astype(str) == '0050')) & (pool_raw['type'].isin(['twse', 'tpex'])) & (~pool_raw['stock_id'].astype(str).isin(DELISTED_BLACKLIST))]
    ticker_info = {f"{r['stock_id']}.TW" if r['type']=='twse' else f"{r['stock_id']}.TWO": {'sid': str(r['stock_id']), 'name': r['stock_name'], 'ind': r['industry_category']} for _, r in pool.iterrows()}
    tickers = list(ticker_info.keys())
    
    latest_price_cache = None
    if os.path.exists(CACHE_DIR):
        pkl_files = [f for f in os.listdir(CACHE_DIR) if f.startswith('yf_prices_') and f.endswith('.pkl')]
        if pkl_files: latest_price_cache = os.path.join(CACHE_DIR, sorted(pkl_files)[-1]) 
            
    if not FORCE_RELOAD_PRICE and latest_price_cache and os.path.exists(latest_price_cache):
        price_data = pd.read_pickle(latest_price_cache)
    else:
        today_str = now_taipei.strftime('%Y-%m-%d'); price_cache = os.path.join(CACHE_DIR, f"yf_prices_{today_str}.pkl")
        batch_dfs = []; missing_tickers = list(tickers)
        for round_num in range(8):
            if not missing_tickers: break
            chunks = [missing_tickers[i:i+120] for i in range(0, len(missing_tickers), 120)]
            for chunk in chunks: 
                if len(chunk) == 1: 
                    chunk.append('0050.TW' if chunk[0] != '0050.TW' else '2330.TW')
            current_round_success = set()
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_chunk = {executor.submit(fetch_yf_safe, c): c for c in chunks}
                for future in tqdm(concurrent.futures.as_completed(future_to_chunk), total=len(chunks), desc=f"📥 第 {round_num+1} 波掃蕩"):
                    req_chunk, df_b = future.result()
                    if not df_b.empty:
                        df_valid = df_b.dropna(axis=1, how='all')
                        if not df_valid.empty:
                            batch_dfs.append(df_valid)
                            dl_set = set(df_valid.columns.get_level_values(0)) if isinstance(df_valid.columns, pd.MultiIndex) else set(req_chunk)
                            current_round_success.update(dl_set)
            missing_tickers = [t for t in missing_tickers if t not in current_round_success]
            gc.collect()
        if not batch_dfs: return
        price_data = pd.concat(batch_dfs, axis=1).ffill(); price_data = price_data.loc[:, ~price_data.columns.duplicated()] 
        price_data.index = pd.to_datetime(price_data.index).tz_localize(None) 
        if not price_data.empty and price_data.index[-1].date() == now_taipei.date() and now_taipei.hour < 14: price_data = price_data.iloc[:-1]
        price_data.to_pickle(price_cache)

    surviving_dfs = {}
    valid_keys = (price_data.columns.levels[0] if isinstance(price_data.columns, pd.MultiIndex) else price_data.columns).unique()
    for full_t in valid_keys:
        if full_t not in ticker_info: continue
        df_p = price_data[full_t].dropna()
        if len(df_p) < 241: continue
        close_col = df_p['Close'].iloc[:, 0] if isinstance(df_p['Close'], pd.DataFrame) else df_p['Close']
        if float(close_col.values[-1]) <= 10: continue
        vol_col = df_p['Volume'].iloc[:, 0] if isinstance(df_p['Volume'], pd.DataFrame) else df_p['Volume']
        if int(vol_col.values[-20:].mean() / 1000) < MIN_VOL_LOTS_ALL: continue
        surviving_dfs[full_t] = df_p
        
    surviving_tickers = list(surviving_dfs.keys()); live_prices = {}
    if is_intraday:
        today_str = now_taipei.strftime('%Y-%m-%d'); live_cache = os.path.join(CACHE_DIR, f"live_prices_{today_str}.pkl")
        if USE_CACHED_LIVE_PRICES and os.path.exists(live_cache):
            try: live_prices = pd.read_pickle(live_cache)
            except: pass
        if not live_prices: 
            missing_live = list(surviving_tickers)
            for round_num in range(7):
                if not missing_live: break
                chunks = [missing_live[i:i+120] for i in range(0, len(missing_live), 120)]
                for chunk in chunks: 
                    if len(chunk) == 1: 
                        chunk.append('0050.TW' if chunk[0] != '0050.TW' else '2330.TW')
                current_round_success = set()
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                    future_to_chunk = {executor.submit(fetch_yf_safe_live, c): c for c in chunks}
                    for future in tqdm(concurrent.futures.as_completed(future_to_chunk), total=len(chunks), desc=f"📡 盤中報價 (第{round_num+1}波)"):
                        req_chunk, df_live = future.result()
                        if not df_live.empty:
                            try:
                                last_date = df_live.index[-1].date() if isinstance(df_live.index, pd.DatetimeIndex) else pd.to_datetime(df_live.index[-1]).date()
                                if last_date == now_taipei.date():
                                    close_df = df_live['Close'] if 'Close' in df_live.columns.get_level_values(0) else df_live.xs('Close', level=1, axis=1) if isinstance(df_live.columns, pd.MultiIndex) else df_live['Close']
                                    for tk in req_chunk:
                                        if tk in close_df.columns and not close_df[tk].dropna().empty:
                                            sid = ticker_info.get(tk, {}).get('sid')
                                            if sid: live_prices[sid] = float(close_df[tk].dropna().iloc[-1]); current_round_success.add(tk)
                                else:
                                    for tk in req_chunk: current_round_success.add(tk)
                            except: pass
                missing_live = [t for t in missing_live if t not in current_round_success]
            pd.to_pickle(live_prices, live_cache)

    candidates = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(evaluate_tech_only, t, surviving_dfs[t], ticker_info, live_prices) for t in surviving_tickers]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(surviving_tickers), desc="🧠 技術初篩"):
            res = future.result()
            if res: candidates.append(res)
    gc.collect()

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_api_candidate, cand) for cand in candidates]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(candidates), desc="📡 雙軌驗證"):
            future.result()

    def save_df(data, filename):
        df = pd.DataFrame(data)
        if not df.empty: df.insert(0, '編號', range(1, len(df) + 1))
        df.to_csv(filename, index=False, encoding='utf-8-sig'); return df

    save_df(final_1, "strategy_a_result.csv")
    save_df(final_2, "strategy_b_result.csv")
    save_df(final_d, "strategy_d_result.csv")
    save_df(final_e, "strategy_e_result.csv")
    save_df(final_squat, "strategy_f_result.csv")
    save_df(final_g_double, "strategy_g_result.csv")
    save_df(final_h_triple, "strategy_h_result.csv")
    save_df(final_j, "strategy_j_result.csv")
    save_df(final_k, "strategy_k_result.csv")
    save_df(final_l, "strategy_l_result.csv")
    save_df(final_m, "strategy_m_result.csv")
    save_df(final_n, "strategy_n_result.csv")
    save_df(final_o, "strategy_o_result.csv")
    
    msg = (f"\n📊 {datetime.datetime.now().strftime('%Y-%m-%d')} 量化大成日報\n"
           f"━━━━━━━━━━━━━━\n"
           f"🟢 策略A: {len(final_1)} 檔\n"
           f"🔵 策略B: {len(final_2)} 檔\n"
           f"🔴 策略D: {len(final_d)} 檔\n"
           f"⚡ 策略E: {len(final_e)} 檔\n"  
           f"📉 策略F: {len(final_squat)} 檔\n"  
           f"🟣 策略G: {len(final_g_double)} 檔\n"
           f"💎 策略H: {len(final_h_triple)} 檔\n"
           f"🟠 策略J: {len(final_j)} 檔\n"
           f"🟤 策略K: {len(final_k)} 檔\n"
           f"⚪ 策略L: {len(final_l)} 檔\n"
           f"🟡 策略M: {len(final_m)} 檔\n"
           f"🌟 策略N(投信): {len(final_n)} 檔\n"
           f"🔥 策略O(訂單): {len(final_o)} 檔\n"
           f"━━━━━━━━━━━━━━\n"
           f"✅ 全市場大掃描完成！")
    
    print(msg)
    send_multi_line_notify(msg)

if __name__ == "__main__":
    run_full_pipeline()
